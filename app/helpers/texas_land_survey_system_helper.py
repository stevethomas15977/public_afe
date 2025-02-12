from shapely.geometry import MultiPolygon, MultiLineString, Polygon, LineString

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
    
def county_fips():
    return {
    "Anderson": "001",
    "Andrews": "003",
    "Angelina": "005",
    "Aransas": "007",
    "Archer": "009",
    "Armstrong": "011",
    "Atascosa": "013",
    "Austin": "015",
    "Bailey": "017",
    "Bandera": "019",
    "Bastrop": "021",
    "Baylor": "023",
    "Bee": "025",
    "Bell": "027",
    "Bexar": "029",
    "Blanco": "031",
    "Borden": "033",
    "Bosque": "035",
    "Bowie": "037",
    "Brazoria": "039",
    "Brazos": "041",
    "Brewster": "043",
    "Briscoe": "045",
    "Brooks": "047",
    "Brown": "049",
    "Burleson": "051",
    "Burnet": "053",
    "Caldwell": "055",
    "Calhoun": "057",
    "Callahan": "059",
    "Cameron": "061",
    "Camp": "063",
    "Carson": "065",
    "Cass": "067",
    "Castro": "069",
    "Chambers": "071",
    "Cherokee": "073",
    "Childress": "075",
    "Clay": "077",
    "Cochran": "079",
    "Coke": "081",
    "Coleman": "083",
    "Collin": "085",
    "Collingsworth": "087",
    "Colorado": "089",
    "Comal": "091",
    "Comanche": "093",
    "Concho": "095",
    "Cooke": "097",
    "Coryell": "099",
    "Cottle": "101",
    "Crane": "103",
    "Crockett": "105",
    "Crosby": "107",
    "Culberson": "109",
    "Dallam": "111",
    "Dallas": "113",
    "Dawson": "115",
    "Deaf Smith": "117",
    "Delta": "119",
    "Denton": "121",
    "Dewitt": "123",
    "Dickens": "125",
    "Dimmit": "127",
    "Donley": "129",
    "Duval": "131",
    "Eastland": "133",
    "Ector": "135",
    "Edwards": "137",
    "Ellis": "139",
    "El Paso": "141",
    "Erath": "143",
    "Falls": "145",
    "Fannin": "147",
    "Fayette": "149",
    "Fisher": "151",
    "Floyd": "153",
    "Foard": "155",
    "Fort Bend": "157",
    "Franklin": "159",
    "Freestone": "161",
    "Frio": "163",
    "Gaines": "165",
    "Galveston": "167",
    "Garza": "169",
    "Gillespie": "171",
    "Glasscock": "173",
    "Goliad": "175",
    "Gonzales": "177",
    "Gray": "179",
    "Grayson": "181",
    "Gregg": "183",
    "Grimes": "185",
    "Guadalupe": "187",
    "Hale": "189",
    "Hall": "191",
    "Hamilton": "193",
    "Hansford": "195",
    "Hardeman": "197",
    "Hardin": "199",
    "Harris": "201",
    "Harrison": "203",
    "Hartley": "205",
    "Haskell": "207",
    "Hays": "209",
    "Hemphill": "211",
    "Henderson": "213",
    "Hidalgo": "215",
    "Hill": "217",
    "Hockley": "219",
    "Hood": "221",
    "Hopkins": "223",
    "Houston": "225",
    "Howard": "227",
    "Hudspeth": "229",
    "Hunt": "231",
    "Hutchinson": "233",
    "Irion": "235",
    "Jack": "237",
    "Jackson": "239",
    "Jasper": "241",
    "Jeff Davis": "243",
    "Jefferson": "245",
    "Jim Hogg": "247",
    "Jim Wells": "249",
    "Johnson": "251",
    "Jones": "253",
    "Karnes": "255",
    "Kaufman": "257",
    "Kendall": "259",
    "Kennedy": "261",
    "Kent": "263",
    "Kerr": "265",
    "Kimble": "267",
    "King": "269",
    "Kinney": "271",
    "Kleberg": "273",
    "Knox": "275",
    "Lamar": "277",
    "Lamb": "279",
    "Lampasas": "281",
    "La Salle": "283",
    "Lavaca": "285",
    "Lee": "287",
    "Leon": "289",
    "Liberty": "291",
    "Limestone": "293",
    "Lipscomb": "295",
    "Live Oak": "297",
    "Llano": "299",
    "Loving": "301",
    "Lubbock": "303",
    "Lynn": "305",
    "McCulloch": "307",
    "McLennan": "309",
    "McMullen": "311",
    "Madison": "313",
    "Marion": "315",
    "Martin": "317",
    "Mason": "319",
    "Matagorda": "321",
    "Maverick": "323",
    "Medina": "325",
    "Menard": "327",
    "Midland": "329",
    "Milam": "331",
    "Mills": "333",
    "Mitchell": "335",
    "Montague": "337",
    "Montgomery": "339",
    "Moore": "341",
    "Morris": "343",
    "Motley": "345",
    "Nacogdoches": "347",
    "Navarro": "349",
    "Newton": "351",
    "Nolan": "353",
    "Nueces": "355",
    "Ochiltree": "357",
    "Oldham": "359",
    "Orange": "361",
    "Palo Pinto": "363",
    "Panola": "365",
    "Parker": "367",
    "Parmer": "369",
    "Pecos": "371",
    "Polk": "373",
    "Potter": "375",
    "Presidio": "377",
    "Rains": "379",
    "Randall": "381",
    "Reagan": "383",
    "Real": "385",
    "Red River": "387",
    "Reeves": "389",
    "Refugio": "391",
    "Roberts": "393",
    "Robertson": "395",
    "Rockwall": "397",
    "Runnels": "399",
    "Rusk": "401",
    "Sabine": "403",
    "San Augustine": "405",
    "San Jacinto": "407",
    "San Patricio": "409",
    "San Saba": "411",
    "Schleicher": "413",
    "Scurry": "415",
    "Shackelford": "417",
    "Shelby": "419",
    "Sherman": "421",
    "Smith": "423",
    "Somervell": "425",
    "Starr": "427",
    "Stephens": "429",
    "Sterling": "431",
    "Stonewall": "433",
    "Sutton": "435",
    "Swisher": "437",
    "Tarrant": "439",
    "Taylor": "441",
    "Terrell": "443",
    "Terry": "445",
    "Throckmorton": "447",
    "Titus": "449",
    "Tom Green": "451",
    "Travis": "453",
    "Trinity": "455",
    "Tyler": "457",
    "Upshur": "459",
    "Upton": "461",
    "Uvalde": "463",
    "Val Verde": "465",
    "Van Zandt": "467",
    "Victoria": "469",
    "Walker": "471",
    "Waller": "473",
    "Ward": "475",
    "Washington": "477",
    "Webb": "479",
    "Wharton": "481",
    "Wheeler": "483",
    "Wichita": "485",
    "Wilbarger": "487",
    "Willacy": "489",
    "Williamson": "491",
    "Wilson": "493",
    "Winkler": "495",
    "Wise": "497",
    "Wood": "499",
    "Yoakum": "501",
    "Young": "503",
    "Zapata": "505"}

