
from tasks.task import Task
from tasks.task_enum import TASKS
from helpers import (task_logger, 
                     extract_images_from_pdf, 
                     process_text_detection, 
                     well_data,
                     extract_text_from_pdf,
                     extract_well_table_information)
from traceback import format_exc
from sqlite3 import Connection
import os
import json
from pandas import DataFrame

headers = [
            "id", 
            "name", 
            "api", 
            "afe_landing_zone",
            "logs_landing_zone",
            "enverus_status",
            "afe_md_ft",
            "afe_bhl_tvd_ft",
            "surveys_preforated_interval_ft",
            "afe_gross_dollar",
            "well_cost",
            "seller_effective_gross_nri_percentage",
            "seller_net_nri_percentage",
            "seller_gross_for_sale_percentage",
            "afe_gwi_for_sale_net_capital_dollar",
            "enverus_rkb_elevation_ft",
            "bhl_tvd_ss_ft",
            "afe_in_landing_zone_hyp_spacing_ft",
            "state",
            "county",
            "tx_abstract_southwest_corner",
            "tx_block_southwest_corner",
            "nw_township_southwest_corner",
            "nm_range_southwest_corner",
            "nm_tx_section_southwest_corner",
            "nad_system",
            "nad_zone",
            "x_surface_location",
            "y_surface_location",
            "x_first_take_point",
            "y_first_take_point",
            "x_last_take_point",
            "y_last_take_point",
            "x_bottom_hole",
            "y_bottom_hole",
            "latitude_surface_location",
            "longitude_surface_location",
            "latitude_first_take_point",
            "longitude_first_take_point",
            "latitude_last_take_point",
            "longitude_last_take_point",
            "latitude_bottom_hole",
            "longitude_bottom_hole",
            "legal_tx_abstract_surface_location",
            "Legal_tx_block_surface_location",
            "legal_nw_township_surface_location",
            "legal_nm_tx_section_surface_location",
            "legal_fnl_surface_location",
            "legal_fsl_surface_location",
            "legal_fwl_surface_location",
            "legal_fel_surface_location",
            "legal_tx_abstract_first_take_point",
            "Legal_tx_block_first_take_point",
            "legal_nw_township_first_take_point",
            "legal_nm_tx_section_first_take_point",
            "legal_fnl_first_take_point",
            "legal_fsl_first_take_point",
            "legal_fwl_first_take_point",
            "legal_fel_first_take_point",
            "legal_tx_abstract_last_take_point",
            "Legal_tx_block_last_take_point",
            "legal_nw_township_last_take_point",
            "legal_nm_tx_section_last_take_point",
            "legal_fnl_last_take_point",
            "legal_fsl_last_take_point",
            "legal_fwl_last_take_point",
            "legal_fel_last_take_point",
            "legal_tx_abstract_bottom_hole",
            "Legal_tx_block_bottom_hole",
            "legal_nw_township_bottom_hole",
            "legal_nm_tx_section_bottom_hole",
            "legal_fnl_bottom_hole",
            "legal_fsl_bottom_hole",
            "legal_fwl_bottom_hole",
            "legal_fel_bottom_hole",
            "perf_interval_ft"
            ]

def dtype ():
    return {
            "id": "INTEGER",
            "name": "TEXT",
            "api": "TEXT",
            "afe_landing_zone": "TEXT",
            "logs_landing_zone": "TEXT",
            "enverus_status": "TEXT",
            "afe_md_ft": "INTEGER",
            "afe_bhl_tvd_ft": "INTEGER",
            "surveys_preforated_interval_ft": "INTEGER",
            "afe_gross_dollar": "REAL",
            "well_cost": "REAL",
            "seller_effective_gross_nri_percentage": "REAL",
            "seller_net_nri_percentage": "REAL",
            "seller_gross_for_sale_percentage": "REAL",
            "afe_gwi_for_sale_net_capital_dollar": "REAL",
            "enverus_rkb_elevation_ft": "INTEGER",
            "bhl_tvd_ss_ft": "INTEGER",
            "afe_in_landing_zone_hyp_spacing_ft": "INTEGER",
            "state": "TEXT",
            "county": "TEXT",
            "tx_abstract_southwest_corner": "TEXT",
            "tx_block_southwest_corner": "TEXT",
            "nw_township_southwest_corner": "TEXT",
            "nm_range_southwest_corner": "TEXT",
            "nm_tx_section_southwest_corner": "INTEGER",
            "nad_system": "TEXT",
            "nad_zone": "TEXT",
            "x_surface_location": "REAL",
            "y_surface_location": "REAL",
            "x_first_take_point": "REAL",
            "y_first_take_point": "REAL",
            "x_last_take_point": "REAL",
            "y_last_take_point": "REAL",
            "x_bottom_hole": "REAL",
            "y_bottom_hole": "REAL",
            "latitude_surface_location": "TEXT",
            "longitude_surface_location": "TEXT",
            "latitude_first_take_point": "TEXT",
            "longitude_first_take_point": "TEXT",
            "latitude_last_take_point": "TEXT",
            "longitude_last_take_point": "TEXT",
            "latitude_bottom_hole": "TEXT",
            "longitude_bottom_hole": "TEXT",
            "legal_tx_abstract_surface_location": "TEXT",
            "Legal_tx_block_surface_location": "TEXT",
            "legal_nw_township_surface_location": "TEXT",
            "legal_nm_range_surface_location": "TEXT",
            "legal_nm_tx_section_surface_location": "TEXT",
            "legal_fnl_surface_location": "TEXT",
            "legal_fsl_surface_location": "TEXT",
            "legal_fwl_surface_location": "TEXT",
            "legal_fel_surface_location": "TEXT",
            "legal_tx_abstract_first_take_point": "TEXT",
            "Legal_tx_block_first_take_point": "TEXT",
            "legal_nw_township_first_take_point": "TEXT",
            "legal_nm_range_first_take_point": "TEXT",
            "legal_nm_tx_section_first_take_point": "TEXT",
            "legal_fnl_first_take_point": "TEXT",
            "legal_fsl_first_take_point": "TEXT",
            "legal_fwl_first_take_point": "TEXT",
            "legal_fel_first_take_point": "TEXT",
            "legal_tx_abstract_last_take_point": "TEXT",
            "Legal_tx_block_last_take_point": "TEXT",
            "legal_nw_township_last_take_point": "TEXT",
            "legal_nm_range_last_take_point": "TEXT",
            "legal_nm_tx_section_last_take_point": "TEXT",
            "legal_fnl_last_take_point": "TEXT",
            "legal_fsl_last_take_point": "TEXT",
            "legal_fwl_last_take_point": "TEXT",
            "legal_fel_last_take_point": "TEXT",
            "legal_tx_abstract_bottom_hole": "TEXT",
            "Legal_tx_block_bottom_hole": "TEXT",
            "legal_nw_township_bottom_hole": "TEXT",
            "legal_nm_range_bottom_hole": "TEXT",
            "legal_nm_tx_section_bottom_hole": "TEXT",
            "legal_fnl_bottom_hole": "TEXT",
            "legal_fsl_bottom_hole": "TEXT",
            "legal_fwl_bottom_hole": "TEXT",
            "legal_fel_bottom_hole": "TEXT",
            "perf_interval_ft": "INTEGER"
        }

def extract_table_Data(pdf_path:str) -> list:
    pdf_text = extract_text_from_pdf(pdf_path=pdf_path)
    # print(pdf_text)
    result = extract_well_table_information(pdf_text=pdf_text)
    return result

def lookup_table_data(table_data: list, key: str) -> dict:
    for item in table_data:
        if "WELL_NAME" in item and key in item["WELL_NAME"]:
            return item
    return None

class LoadTargetWellInformationAnadarko(Task):

    def execute(self):
        task = TASKS.LOAD_TARGET_WELL_INFORMATION_ANADARKO.value
        logger = task_logger(task, self.context.logs_path)
        try:
            pdf_path = self.context.target_well_information_file

            table_data = extract_table_Data(pdf_path=pdf_path)

            if table_data is None:
                logger.error(f"Error {task} workflow task: No data found in the pdf")
                raise ValueError(f"Error {task} workflow task: No data found in the pdf")

            # {'WELL_NAME': 'MOOSEHORN 54-1-41-44 G 61H', 'Target_Bench': '2BSS', 'Est_TVD_ft': 9982, 'Est_MD_ft': 20738.6, 'Approx_SHL_Location': '812’ FNL X 2148’ FWL, SEC 41, BLK 54 T1, Loving County, Texas'}

            images = extract_images_from_pdf(pdf_path=pdf_path)
            wells = []
            id = 1
            for image in images:
                well = {}
                lines=process_text_detection(image=image)
                if "NEW DRILL" in lines:
                    surface_location = well_data("SURFACE LOCATION", "PENETRATION POINT", lines)
                    bottom_hole = well_data("LAST TAKE POINT", "END OF TERMINUS", lines)
                    additional_data = lookup_table_data(table_data, surface_location["SURFACE LOCATION"]['Well Name'])
                    well_name = surface_location["SURFACE LOCATION"]['Well Name']
                    interval = None
                    ground_elevation = int(float(surface_location["SURFACE LOCATION"]['Ground Elevation']))
                    tvd = 0
                    md = 0
                    state = None
                    if additional_data:
                        well_name = additional_data["WELL_NAME"]
                        interval = additional_data["Target_Bench"]
                        tvd = int(float(additional_data["Est_TVD_ft"]))
                        md = int(float(additional_data["Est_MD_ft"]))
                        if 'Texas' in additional_data["Approx_SHL_Location"]:
                            state = "TX"
                        else:
                            state = "NM"
                    else: 
                        continue
                    # print(surface_location)
                    # print(bottom_hole)

                    well['id'] = id
                    well['name'] = well_name
                    well['afe_landing_zone'] = interval
                    well['logs_landing_zone'] = interval
                    well['surveys_preforated_interval_ft'] = md - tvd
                    well['bhl_tvd_ss_ft'] = (md - tvd - ground_elevation) * -1
                    well['x_surface_location'] = surface_location["SURFACE LOCATION"]['X']
                    well['y_surface_location'] = surface_location["SURFACE LOCATION"]['Y']
                    well['x_first_take_point'] = surface_location["SURFACE LOCATION"]['X']
                    well['y_first_take_point'] = surface_location["SURFACE LOCATION"]['Y']
                    if 'X' in bottom_hole["LAST TAKE POINT"]:
                        if bottom_hole["LAST TAKE POINT"]['X']:
                            well['x_last_take_point'] = bottom_hole["LAST TAKE POINT"]['X']
                            well['x_bottom_hole'] = bottom_hole["LAST TAKE POINT"]['X']
                        else:
                            continue
                    else:
                        continue
                    if 'Y' in bottom_hole["LAST TAKE POINT"]:
                        if bottom_hole["LAST TAKE POINT"]['Y']:
                            well['y_last_take_point'] = bottom_hole["LAST TAKE POINT"]['Y']
                            well['y_bottom_hole'] = bottom_hole["LAST TAKE POINT"]['Y']
                        else:
                            continue
                    else:
                        continue
                    well['nad_system'] = "NAD27"
                    well['nad_zone'] = "Central"
                    well['state'] = state
                    well['county'] = surface_location["SURFACE LOCATION"]['County']
                    well['tx_abstract_southwest_corner'] = surface_location["SURFACE LOCATION"]['Abstract']
                    wells.append(well)
                    id += 1

            self.context.connection = Connection(self.context.db_path)
            df = DataFrame(wells, columns=headers)
            df.to_sql('target_well_information', self.context.connection, if_exists='replace', index=False, dtype=dtype())
            self.context.connection.commit()
            
            logger.info(f"{task}: {self.context.logs_path}")
        except Exception as e:
            logger.error(f"Error {task} workflow task: {e}\n{format_exc()}")
            raise ValueError(f"Error {task} workflow task: {e}")