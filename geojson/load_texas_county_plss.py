import json
import geopandas as gpd
from shapely.geometry import MultiPolygon, MultiLineString, Polygon, LineString
import sqlite3
from pathlib import Path
import boto3
import tempfile
import os

def section_4_corners(geometry):
    coordinates = []
    try:
        if isinstance(geometry, (MultiPolygon, MultiLineString)):
            for part in geometry.geoms:
                if isinstance(part, (Polygon, LineString)):
                    coordinates.extend(part.exterior.coords if isinstance(part, Polygon) else part.coords)
        elif isinstance(geometry, (Polygon, LineString)):
            coordinates.extend(geometry.exterior.coords if isinstance(geometry, Polygon) else geometry.coords)

        north_bucket = []
        south_bucket = []
        east_bucket = []
        west_bucket = []

        for outter_index, outter_coordinate in enumerate(coordinates):
            # print(f"Outter Index: {outter_index}")
            for inner_index, inner_coordinate in enumerate(coordinates):
                # print(f" Inner Index: {inner_index}")
                if outter_index == inner_index:
                    continue
                rounded_outter_coordinate = round(outter_coordinate[0],3)
                rounded_inner_coordinate = round(inner_coordinate[0],3)
                difference = abs(rounded_outter_coordinate - rounded_inner_coordinate)
                if rounded_outter_coordinate < rounded_inner_coordinate and difference >= 0.01:
                    if inner_index not in north_bucket:
                        # print(f" {inner_index} goes into the North Bucket")
                        north_bucket.append(inner_index)
                elif rounded_outter_coordinate > rounded_inner_coordinate and difference >= 0.01:
                    if inner_index not in south_bucket:
                        # print(f" {inner_index} goes into the South Bucket")
                        south_bucket.append(inner_index)

                rounded_outter_coordinate = round(outter_coordinate[1],3)
                rounded_inner_coordinate = round(inner_coordinate[1],3)
                difference = abs(rounded_outter_coordinate - rounded_inner_coordinate)
                if rounded_outter_coordinate < rounded_inner_coordinate and difference >= 0.01:
                    if inner_index not in east_bucket:
                        # print(f" {inner_index} goes into the East Bucket")
                        east_bucket.append(inner_index)
                elif rounded_outter_coordinate > rounded_inner_coordinate and difference >= 0.01:
                    if inner_index not in west_bucket:
                        # print(f" {inner_index} goes into the West Bucket")
                        west_bucket.append(inner_index)
        
        # print("North: ", north_bucket)
        # print("South: ", south_bucket)
        # print("East: ", east_bucket)
        # print("West: ", west_bucket)

        corners = {}

        for index, coordinate in enumerate(coordinates):
            if index in north_bucket and index in east_bucket:
                # print(f"Northeast: {coordinates[index]}")
                corners["northeast"] = coordinates[index]
            if index in south_bucket and index in east_bucket:
                # print(f"Southeast: {coordinates[index]}")
                corners["southeast"] = coordinates[index]
            if index in north_bucket and index in west_bucket:
                # print(f"Northwest: {coordinates[index]}")
                corners["northwest"] = coordinates[index]
            if index in south_bucket and index in west_bucket:
                # print(f"Southwest: {coordinates[index]}")
                corners["southwest"] = coordinates[index]

        return corners
    
    except NotImplementedError as e:
        raise Exception(f"Four corners processing error") from e  

insert_command = '''
        INSERT INTO texas_land_survey_system (
        county,
        fips_code, 
        abstract, 
        block, 
        section, 
        grantee, 
        southwest_latitude,
        southwest_longitude,
        northwest_latitude,
        northwest_longitude,
        southeast_latitude,
        southeast_longitude,
        northeast_latitude,
        northeast_longitude
        ) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT DO NOTHING
    '''

create_table_command = '''
        CREATE TABLE IF NOT EXISTS texas_land_survey_system (
            county TEXT,
            fips_code TEXT,
            abstract TEXT,
            block TEXT,
            section TEXT,
            grantee TEXT,
            southwest_latitude REAL,
            southwest_longitude REAL,
            northwest_latitude REAL,
            northwest_longitude REAL,
            southeast_latitude REAL,
            southeast_longitude REAL,
            northeast_latitude REAL,
            northeast_longitude REAL
        )
    '''
def create_table_in_db(db_path, table_ddl):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS block_section")
        cursor.execute(table_ddl)
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

def insert_into_db(db_path, table_dml, rows):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.executemany(table_dml, rows)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

def read_fips_county_json():
    file = f"/home/steve/afe/geojson/texas_fips_to_county.json"
    with open(file, 'r') as f:
        data = json.load(f)
    return data

def list_s3_object_urls(bucket_name, folder_prefix):
    s3_client = boto3.client('s3')
    object_urls = []
    objects = []

    # List objects in the specified S3 bucket and folder
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_prefix)

    if 'Contents' in response:
        for obj in response['Contents']:
            # Generate the object URL
            object_url = f"https://{bucket_name}.s3.amazonaws.com/{obj['Key']}"
            object_urls.append(object_url)
            objects.append(obj['Key'])  # Add the key for downloading later
    else:
        print(f"No objects found in {bucket_name}/{folder_prefix}")

    return object_urls, objects

def download_s3_object_to_temp(bucket_name, object_key):
    s3_client = boto3.client('s3')

    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        # Download the object from S3 to the temp file
        s3_client.download_fileobj(bucket_name, object_key, temp_file)
        temp_file_path = temp_file.name
    return temp_file_path
    
def upload_sqlite_to_s3(db_file_path, bucket_name, s3_folder_path):
    s3_client = boto3.client('s3')

    # Construct the S3 key (path in the bucket)
    s3_key = f"{s3_folder_path}/{db_file_path.split('/')[-1]}"  # Use the file name from the db_file_path

    # Upload the SQLite file to S3
    try:
        with open(db_file_path, 'rb') as db_file:
            s3_client.upload_fileobj(db_file, bucket_name, s3_key)
    except Exception as e:
        print(f"Failed to upload {db_file_path} to s3://{bucket_name}/{s3_key}: {e}")

def main():

    bucket_name = 'afe-plss'
    folder_prefix = 'geojson/texas/abstract/' 
    sqlite_folder_prefix = 'geojson/texas/sqlite' 

    # Get the FIPS code for the county
    fips_county = read_fips_county_json()
    for fips_code, county in fips_county.items():
        county = county.strip().lower().replace(' ', '')
        object_key = f"{folder_prefix}{county}.geojson"
        temp_file_path = download_s3_object_to_temp(bucket_name, object_key)

        db_path = f"/home/steve/afe/geojson/texas/dbs/{county}.db"
        create_table_in_db(db_path=db_path, table_ddl=create_table_command)

        gdf = gpd.read_file(temp_file_path, engine='pyogrio', use_arrow=True)
        rows_to_insert = []

        for _, row in gdf.iterrows():
            abstract = row.get('ABSTRACT_L')
            block = row.get('LEVEL2_BLO')
            section = row.get('LEVEL3_SUR')
            grantee = row.get('LEVEL4_SUR')

            geometry = row.get('geometry')
            corners = section_4_corners(geometry=geometry)
            if not corners:
                continue
            southwest_latitude = None
            southwest_longitude = None
            northwest_latitude = None
            northwest_longitude = None
            southeast_latitude = None
            southeast_longitude = None
            northeast_latitude = None
            northeast_longitude = None
            for corner, coords in corners.items():
                longitude = coords[0]
                latitude = coords[1]
                if corner == 'southwest':
                    southwest_latitude = latitude
                    southwest_longitude = longitude
                elif corner == 'northwest':
                    northwest_latitude = latitude
                    northwest_longitude = longitude
                elif corner == 'southeast':
                    southeast_latitude = latitude
                    southeast_longitude = longitude
                elif corner == 'northeast':
                    northeast_latitude = latitude
                    northeast_longitude = longitude

            rows_to_insert.append((county,
                                fips_code,
                                abstract, 
                                block, 
                                section,
                                grantee,
                                southwest_latitude, 
                                southwest_longitude, 
                                northwest_latitude, 
                                northwest_longitude, 
                                southeast_latitude, 
                                southeast_longitude, 
                                northeast_latitude, 
                                northeast_longitude))
    
        insert_into_db(db_path=db_path, table_dml=insert_command, rows=rows_to_insert)
        
        upload_sqlite_to_s3(db_path, bucket_name, sqlite_folder_prefix)

        try:
            os.remove(db_path) 
            os.remove(temp_file_path) 
        except OSError as e:
            print(f"Error: {e.strerror}")

        print(f"Finished processing {county} county")

        import gc
        del gdf
        gc.collect()

if __name__ == "__main__":
    main()