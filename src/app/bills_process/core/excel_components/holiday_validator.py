import re
from typing import Optional, Tuple

class HolidayValidator:
    """
    Validates working days versus holidays by analyzing Excel cell values
    to find the last valid cumulative sales data.
    """
    
    def find_last_valid_working_day(self, workbook, current_day: int) -> Tuple[Optional[str], Optional[int]]:
        """
        Finds the last valid working day by checking previous days' sheets
        for valid cumulative sales data.
        """
        prev_day = current_day - 1
        
        while prev_day >= 1:
            prev_sheet_name = str(prev_day)
            
            if prev_sheet_name not in workbook.sheetnames:
                prev_day -= 1
                continue
            
            ws_prev = workbook[prev_sheet_name]
            
            cumulative_sales_row = self._find_row_by_value(ws_prev, "D", "ยอดขายสะสม")
            
            if cumulative_sales_row:
                h_val = ws_prev[f"H{cumulative_sales_row}"].value
                
                if self._is_valid_cumulative_value(h_val):
                    return prev_sheet_name, cumulative_sales_row
            
            prev_day -= 1
        
        return None, None
    
    def _find_row_by_value(self, worksheet, column: str, value: str) -> Optional[int]:
        """Finds the row number in a given column that contains a specific value."""
        for row in range(1, worksheet.max_row + 1):
            cell_val = worksheet[f"{column}{row}"].value
            if isinstance(cell_val, str) and cell_val.strip() == value:
                return row
        return None

    def _is_valid_cumulative_value(self, value) -> bool:
        """
        Checks if the value in a cumulative sales cell represents a valid working day.
        A valid value is a number greater than 0 or a formula.
        """
        if value is None or value == "":
            return False
        
        if isinstance(value, str) and value.startswith("="):
            # Any formula is considered a potentially valid cumulative value
            return True
        
        if isinstance(value, (int, float)):
            return value > 0
        
        return False
