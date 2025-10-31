import os
from typing import List, Dict, Any
from openpyxl.styles import Font, Border, Side

class WorksheetManager:
    """
    Manages worksheet structure, data insertion, and formatting.
    """
    
    def __init__(self):
        self.font = Font(name="Tahoma", size=12)
        self.thin_border = Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')
        )
    
    def prepare_worksheet(self, worksheet, num_new_files: int, num_existing_files: int):
        """
        Prepare the worksheet by inserting rows for the new data.
        """
        if num_existing_files == 0:
            # Template starts with one empty data row at position 5.
            # We need (num_new_files - 1) additional rows.
            rows_to_insert = num_new_files - 1
            insert_position = 5
        else:
            # Subsequent processing: insert rows before the existing formula rows.
            rows_to_insert = num_new_files
            insert_position = 5 + num_existing_files

        if rows_to_insert > 0:
            worksheet.insert_rows(insert_position, rows_to_insert)
    
    def fill_data(self, worksheet, new_daily_files: List[str], new_data: List[Dict[str, Any]], 
                  inventory_code: str, num_existing_files: int):
        """
        Fill the worksheet with data from the new daily files.
        """
        start_row = 5 + num_existing_files
        
        for idx, fname in enumerate(new_daily_files):
            row = start_row + idx
            data_dict = new_data[idx]
            
            # Parse filename for six and two digit parts
            name = os.path.splitext(fname)[0]
            six_digits, two_digits = self._parse_filename(name)
            
            # Fill basic info from filename and config
            self._fill_basic_info(worksheet, row, idx, inventory_code, six_digits, two_digits, num_existing_files)
            
            # Fill collected data from the data dictionary
            self._fill_collected_data(worksheet, row, data_dict)
            
            # Apply borders to the new row
            self._apply_borders(worksheet, row)

    def _parse_filename(self, name: str) -> tuple[str, str]:
        """Extracts six and two-digit parts from a filename."""
        if len(name) == 8 and name.isdigit():
            return name[:6], name[6:]
        return name[:6], name[6:8] if len(name) > 6 else ""

    def _fill_basic_info(self, worksheet, row: int, idx: int, inventory_code: str, 
                        six_digits: str, two_digits: str, num_existing_files: int):
        """Fills columns A, B, C, F."""
        worksheet[f"A{row}"] = num_existing_files + idx + 1
        worksheet[f"B{row}"] = inventory_code
        worksheet[f"C{row}"] = six_digits
        worksheet[f"F{row}"] = int(two_digits) if two_digits.isdigit() else two_digits
        
        for col_letter in ["A", "B", "C", "F"]:
             worksheet[f"{col_letter}{row}"].font = self.font

    def _fill_collected_data(self, worksheet, row: int, data_dict: Dict[str, Any]):
        """Fills columns D, E, G, H, K, L, M from the data dictionary."""
        # This mapping assumes specific 'field_name' values were used in the Cell Configuration.
        column_map = {
            "D": data_dict.get("receiver_name", ""),
            "E": data_dict.get("receiver_address", ""),
            "G": data_dict.get("sum_qty", ""),
            "H": data_dict.get("grand_total", ""),
            "K": data_dict.get("delivery_by", ""),
            "L": data_dict.get("platform", ""),
            "M": data_dict.get("phone", "")
        }
        
        for col_letter, value in column_map.items():
            cell = worksheet[f"{col_letter}{row}"]
            cell.value = value
            cell.font = self.font
            if col_letter in ("G", "H") and isinstance(value, (int, float)):
                cell.number_format = '#,##0'

        def _fill_collected_data(self, worksheet, row: int, data_dict: Dict[str, Any]):
            """Fills columns D, E, G, H, K, L, M from the data dictionary."""
            # This mapping assumes specific 'field_name' values were used in the Cell Configuration.
            column_map = {
                "D": data_dict.get("receiver_name", ""),
                "E": data_dict.get("receiver_address", ""),
                "G": data_dict.get("sum_qty", ""),
                "H": data_dict.get("grand_total", ""),
                "K": data_dict.get("delivery_by", ""),
                "L": data_dict.get("platform", ""),
                "M": data_dict.get("phone", "")
            }
            
            for col_letter, value in column_map.items():
                cell = worksheet[f"{col_letter}{row}"]
                cell.value = value
                cell.font = self.font
                if col_letter in ("G", "H") and isinstance(value, (int, float)):
                    cell.number_format = '#,##0' 
    def _apply_borders(self, worksheet, row: int):
        """Applies thin borders to all cells in the data row."""
        for col in range(1, 15):  # Columns A to N
            worksheet.cell(row=row, column=col).border = self.thin_border
