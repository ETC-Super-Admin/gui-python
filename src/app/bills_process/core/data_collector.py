import os
import re
from typing import List, Any, Tuple, Dict
from openpyxl import load_workbook
from .result import Result
from src.db.bill_config_queries import get_all_bill_configs

class DataCollector:
    """
    Handles collecting data from daily bill files based on configuration rules
    stored in the database.
    """
    
    def __init__(self):
        self.bill_configs = get_all_bill_configs()
    
    def collect_from_files(self, daily_files: List[str], target_dir: str) -> Result:
        """
        Collect data from all daily files based on the loaded bill configuration.
        
        Args:
            daily_files: List of daily bill file names.
            target_dir: Directory containing the daily files.
            
        Returns:
            Result: Contains a list of dictionaries (one per file) on success.
        """
        if not self.bill_configs:
            return Result.error("❌ No bill processing configurations found. Please set them up in the 'Bill Processing Configuration' page.")

        try:
            collected_data = []
            for fname in daily_files:
                file_path = os.path.join(target_dir, fname)
                file_result_dict = self._collect_from_single_file(file_path)
                collected_data.append(file_result_dict)
            
            return Result.success(collected_data)
            
        except Exception as e:
            return Result.error(f"❌ An error occurred while collecting data from files: {e}")
    
    def _collect_from_single_file(self, file_path: str) -> Dict[str, Any]:
        """
        Collect data from a single Excel file and return it as a dictionary
        where keys are the configured field names.
        """
        try:
            wb_daily = load_workbook(file_path, data_only=True)
            ws_daily = wb_daily.active
            
            result_dict = {}
            
            for config in self.bill_configs:
                field_name = config.get('field_name')
                if not field_name:
                    continue
                
                value = self._extract_value_by_type(ws_daily, config)
                result_dict[field_name] = value
            
            return result_dict

        except Exception as e:
            print(f"Error processing file {os.path.basename(file_path)}: {e}")
            return {}

    def _extract_value_by_type(self, worksheet, config) -> Any:
        """
        Extract value from worksheet based on item type and configuration.
        """
        try:
            config_type = config['config_type'] # 0: By Cell, 1: By Column
            if config_type == 0: # By Cell
                return self._extract_by_cell(worksheet, config)
            elif config_type == 1: # By Column
                return self._extract_by_column(worksheet, config)
            else:
                return ""
        except Exception:
            return ""

    def _extract_by_cell(self, worksheet, config) -> Any:
        """Extract value using 'By Cell' method."""
        check_cell_address = config.get('check_text')
        expected_value = config.get('value')
        
        if not check_cell_address:
            return ""

        actual_value = worksheet[check_cell_address].value
        
        # Compare values, stripping strings for safety
        if str(actual_value).strip() == str(expected_value):
            focus_cell_address = config.get('focus')
            if focus_cell_address:
                return worksheet[focus_cell_address].value
        return ""

    def _extract_by_column(self, worksheet, config) -> Any:
        """Extract value using 'By Column' method (which now functions as 'By Collect Column')."""
        focus_col = config.get('focus')
        check_val = config.get('check_text')
        collect_col = config.get('value')
        
        if not all([focus_col, check_val, collect_col]):
            return ""

        for row in worksheet.iter_rows(min_row=1, max_row=worksheet.max_row):
            cell_focus = None
            cell_collect = None
            
            for cell in row:
                if cell.column_letter == focus_col:
                    cell_focus = cell
                if cell.column_letter == collect_col:
                    cell_collect = cell
            
            if cell_focus and cell_focus.value and str(cell_focus.value).strip() == check_val:
                return cell_collect.value if cell_collect else ""
        
        return ""
