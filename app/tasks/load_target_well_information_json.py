
from tasks.task import Task
from tasks.task_enum import TASKS
from helpers import task_logger
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

class LoadTargetWellInformationJSON(Task):

    def execute(self):
        task = TASKS.LOAD_TARGET_WELL_INFORMATION_JSON.value
        logger = task_logger(task, self.context.logs_path)
        try:
            # Create connection to the database
            self.context.connection = Connection(self.context.db_path)

            # Load the json file into a DataFrame
            with open(os.path.join(self.context.target_well_information_path, self.context.target_well_information_file), 'rb') as file:
                data = json.load(file)

            wells = []
            for row in data['rows']:
                well = {}
                well['id'] = row['id']
                well['name'] = row['name']
                well['afe_landing_zone'] = row['lz']
                well['logs_landing_zone'] = row['lz']
                well['surveys_preforated_interval_ft'] = row['perf_int']
                well['bhl_tvd_ss_ft'] = row['ssd']
                well['x_surface_location'] = row['surface_x']
                well['y_surface_location'] = row['surface_y']
                well['x_first_take_point'] = row['surface_x']
                well['y_first_take_point'] = row['surface_y']
                well['x_last_take_point'] = row['bottom_hole_x']
                well['y_last_take_point'] = row['bottom_hole_y']
                well['x_bottom_hole'] = row['bottom_hole_x']
                well['y_bottom_hole'] = row['bottom_hole_y']
                well['nad_system'] = data['system']
                well['nad_zone'] = data['zone']
                well['state'] = data['state']
                well['county'] = data['county']
                if 'TX' in well['state']:
                    well['tx_abstract_southwest_corner'] = data['abstract']
                    well['tx_block_southwest_corner'] = data['block']
                    well['nm_tx_section_southwest_corner'] = data['tx_section']
                if 'NM' in well['state']:
                    well['nw_township_southwest_corner'] = f"{data['township']}{data['township_direction']}"
                    well['nm_range_southwest_corner'] = f"{data['range']}{data['range_direction']}"
                    well['nm_tx_section_southwest_corner'] = data['nm_section']
                wells.append(well)
                
            # Create empty DataFrame
            df = DataFrame(wells, columns=headers)

            df.to_sql('target_well_information', self.context.connection, if_exists='replace', index=False, dtype=dtype())
            
            logger.info(f"{task}: {self.context.logs_path}")
        except Exception as e:
            logger.error(f"Error {task} workflow task: {e}\n{format_exc()}")
            raise ValueError(f"Error {task} workflow task: {e}")