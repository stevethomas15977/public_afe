

import folium

from services import (TexasLandSurveySystemService,
                      NewMexicoLandSurveySystemService)

from context import Context

from helpers import (texas_plss_block_section_overlay,
                     new_mexico_plss_overlay,
                     draw_section_lines,
                     spc_feet_to_latlon)

class Project:
    def __init__(self):
        self.name = None
        self.provider = 'Enverus'
        self.offset_well_file = None
        self.offset_survey_file = None
        self.target_well_information_file = None
        self.target_well_information_source = 'Manual'
        self.state = None
        self.county = None
        self.abstract = None
        self.block = None
        self.tx_section = None
        self.township = None
        self.township_direction = None
        self.range = None
        self.range_direction = None
        self.nm_section = None
        self.system = 'NAD27'
        self.zone = 'Central'
        self.rows = []

    def to_dict(self):
        return {
            "name": self.name,
            "proivder": self.provider,
            "offset_well_file": self.offset_well_file,
            "offset_survey_file": self.offset_survey_file,
            "target_well_information_file": self.target_well_information_file,
            "target_well_information_source": self.target_well_information_source,
            "state": self.state,
            "county": self.county,
            "abstract": self.abstract,
            "block": self.block,
            "tx_section": self.tx_section,
            "township": self.township,
            "township_direction": self.township_direction,
            "range": self.range,
            "range_direction": self.range_direction,
            "nm_section": self.nm_section,
            "system": self.system,
            "zone": self.zone,
            "rows": self.rows
        }
    
def create_surface_map(context: Context, project: Project) -> str:
    try:
        # Initialize the services
        tlss_service = TexasLandSurveySystemService(context._texas_land_survey_system_database_path)
        nmlss_service = NewMexicoLandSurveySystemService(context._new_mexico_land_survey_system_database_path)

        # Create a map object
        map = None

        # Check the state of the project and draw southwest corner and gun barrel plot line
        if project.state == "TX":
            tlss = tlss_service.get_by_county_abstract(county=project.county, abstract=project.abstract)
            fips_codes = []
            fips_codes.append(tlss.fips_code)
            map = folium.Map(
                location=[tlss.southwest_latitude, tlss.southwest_longitude],
                zoom_start=12.5, 
                width='100%', 
                height='100%')
            texas_plss_block_section_overlay(context=context, fip_codes=fips_codes, map=map)
            folium.LayerControl().add_to(map)
            coordinates = {}
            coordinates['southwest_latitude'] = tlss.southwest_latitude
            coordinates['southwest_longitude'] = tlss.southwest_longitude
            tooltip = f"SW Corner {tlss.abstract}-{tlss.block}-{tlss.section}"
            draw_section_lines(coordinates=coordinates, tooltip=tooltip, map=map)
        elif project.state == "NM":
            nmlss = nmlss_service.get_by_township_range_section(township=project.township, township_direction=project.township_direction, range=project.range, range_direction=project.range_direction, section=project.nm_section)
            file_prefixes = []
            file_prefixes.append(f"{project.township}{project.township_direction}")
            file_prefixes.append(f"{int(project.township)-3}{project.township_direction}")
            file_prefixes.append(f"{int(project.township)-2}{project.township_direction}")
            file_prefixes.append(f"{int(project.township)-1}{project.township_direction}")
            file_prefixes.append(f"{int(project.township)+1}{project.township_direction}")
            file_prefixes.append(f"{int(project.township)+2}{project.township_direction}")
            file_prefixes.append(f"{int(project.township)+3}{project.township_direction}")
            map = folium.Map(
                location=[nmlss.southwest_latitude, nmlss.southwest_longitude],
                zoom_start=12.5, 
                width='100%', 
                height='100%')
            new_mexico_plss_overlay(context=context, file_prefixes=file_prefixes, map=map)
            folium.LayerControl().add_to(map)
            coordinates = {}
            coordinates['southwest_latitude'] = nmlss.southwest_latitude
            coordinates['southwest_longitude'] = nmlss.southwest_longitude
            tooltip = f"SW Corner {nmlss.township}-{nmlss.range}-{nmlss.section}"
            draw_section_lines(coordinates=coordinates, tooltip=tooltip, map=map)

        # Draw proposed wells
        for row in project.rows:
            if row['surface_x'] is None and row['surface_y'] is None:
                break
            spcZone = 4203
            inDatum = "NAD27"
            surface_latitude, surface_longitude = spc_feet_to_latlon(northing=row['surface_y'],
                                                                    easting=row['surface_x'],
                                                                    spcZone=spcZone,
                                                                    inDatum=inDatum)
            
            bottom_latitude, bottom_longitude = spc_feet_to_latlon(northing=row['bottom_hole_y'],
                                                                    easting=row['bottom_hole_x'],
                                                                    spcZone=spcZone,
                                                                    inDatum=inDatum)
        
            start = (float(surface_latitude), float(surface_longitude))
            end = (float(bottom_latitude), float(bottom_longitude))
            folium.PolyLine([start, end], color="orange", weight=3.0, tooltip=f"{row['name']}").add_to(map)

        return map._repr_html_()
    except Exception as e:
        return f"<html><body><h1>Error: {e}</h1></body></html>"