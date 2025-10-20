# src/components/tabs/bills_process_tab/components/excel_components/worksheet_manager.py
import os
from typing import List, Any
from openpyxl.styles import Font, Border, Side

class WorksheetManager:
    """
    Manages worksheet structure and data insertion.
    Handles row insertion, data filling, and formatting.
    """
    
    def __init__(self):
        self.font = Font(name="Tahoma", size=12)
        self.thin_border = Border(
            left=Side(style='thin', color='000000'),
            right=Side(style='thin', color='000000'),
            top=Side(style='thin', color='000000'),
            bottom=Side(style='thin', color='000000')
        )
    
    def prepare_worksheet(self, worksheet, num_new_files: int, num_existing_files: int):
        """
        Prepare the worksheet by inserting additional rows if needed.
        
        Args:
            worksheet: Openpyxl worksheet object
            num_new_files: Number of new daily files to process
            num_existing_files: Number of files already in the sheet
        """
        if num_existing_files == 0:
            # First time processing - template has one row at position 5
            rows_to_insert = num_new_files - 1
            insert_position = 5
        else:
            # Subsequent processing - insert before the formula rows
            rows_to_insert = num_new_files
            insert_position = 5 + num_existing_files

        # Insert all new rows at once before the formula rows
        if rows_to_insert > 0:
            worksheet.insert_rows(insert_position, rows_to_insert)
    
    def fill_data(self, worksheet, daily_files: List[str], collected_data: List[List[Any]], 
                  inventory_code: str, start_row: int = 5):
        """
        Fill the worksheet with data from daily files.
        
        Args:
            worksheet: Openpyxl worksheet object
            daily_files: List of daily file names
            collected_data: Matrix of collected data
            inventory_code: Inventory code from configuration
            start_row: The row to start filling data from
        """
        for idx, fname in enumerate(daily_files):
            row = start_row + idx
            
            # Parse filename for six and two digit parts
            name = os.path.splitext(fname)[0]
            six_digits, two_digits = self._parse_filename(name)
            
            # Fill basic information
            self._fill_basic_info(worksheet, row, idx, inventory_code, six_digits, two_digits, start_row)
            
            # Fill collected data
            if idx < len(collected_data):
                self._fill_collected_data(worksheet, row, collected_data[idx])
            
            # Apply borders
            self._apply_borders(worksheet, row)
    
    def _parse_filename(self, name: str) -> tuple[str, str]:
        """
        Parse filename to extract six digits and two digits parts.
        
        Args:
            name: Filename without extension
            
        Returns:
            Tuple of (six_digits, two_digits)
        """
        if len(name) == 8 and name.isdigit():
            return name[:6], name[6:]
        else:
            return name[:6], name[6:8] if len(name) > 6 else ""
    
    def _fill_basic_info(self, worksheet, row: int, idx: int, inventory_code: str, 
                        six_digits: str, two_digits: str, start_row: int = 5):
        """Fill basic information columns (A, B, C, F)."""
        # Column A: Sequential number should continue from the last one
        seq_num = (start_row - 5) + idx + 1
        worksheet[f"A{row}"] = seq_num
        worksheet[f"A{row}"].font = self.font
        
        # Column B: Inventory code
        worksheet[f"B{row}"] = inventory_code
        worksheet[f"B{row}"].font = self.font
        
        # Column C: Six digits
        worksheet[f"C{row}"] = six_digits
        worksheet[f"C{row}"].font = self.font
        
        # Column F: Two digits (convert to int if numeric)
        worksheet[f"F{row}"] = int(two_digits) if two_digits.isdigit() else two_digits
        worksheet[f"F{row}"].font = self.font
    
    def _fill_collected_data(self, worksheet, row: int, data_row: List[Any]):
        """Fill collected data into columns D, E, G, H, K, L, and M."""
        column_mappings = [
            ("D", 0),  # First collected value -> Column D
            ("E", 1),  # Second collected value (cleaned address) -> Column E
            ("G", 2),  # Third collected value -> Column G
            ("H", 3),  # Fourth collected value -> Column H
            ("K", 4),  # Fifth collected value (config id 5) -> Column K
            ("M", 5),  # Sixth collected value (phone number) -> Column M
            ("L", 6)   # Seventh collected value (platform) -> Column L
        ]
        
        for column, data_index in column_mappings:
            if data_index < len(data_row) and data_row[data_index]:
                cell = worksheet[f"{column}{row}"]
                cell.value = data_row[data_index]
                cell.font = self.font
                
                # MODIFICATION: Apply comma style format for columns G and H
                if column in ("G", "H"):
                    cell.number_format = '#,##0'
    
    def _apply_borders(self, worksheet, row: int):
        """Apply borders to columns A-N for the given row."""
        for col in range(1, 15):  # A=1, N=14
            cell = worksheet.cell(row=row, column=col)
            cell.border = self.thin_border