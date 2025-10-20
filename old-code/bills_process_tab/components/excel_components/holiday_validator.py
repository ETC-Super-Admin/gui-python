# src/components/tabs/bills_process_tab/components/excel_components/holiday_validator.py
import re
from typing import Optional, Tuple

class HolidayValidator:
    """
    Validates working days vs holidays by analyzing Excel cell values.
    Handles detection of holiday patterns and finding valid working days.
    """
    
    def find_last_valid_working_day(self, workbook, current_day: int) -> Tuple[Optional[str], Optional[int]]:
        """
        Find the last valid working day by checking previous days for valid cumulative sales data.
        
        Args:
            workbook: The Excel workbook object
            current_day: Current day being processed
            
        Returns:
            Tuple of (sheet_name, row_number) for the last valid working day, or (None, None) if not found
        """
        prev_day = current_day - 1
        
        while prev_day >= 1:
            prev_sheet_name = str(prev_day)
            
            # Check if sheet exists
            if prev_sheet_name not in workbook.sheetnames:
                prev_day -= 1
                continue
            
            ws_prev = workbook[prev_sheet_name]
            
            # Find 'ยอดขายสะสม' row in previous sheet
            yodkaysum_row = self._find_cumulative_sales_row(ws_prev)
            
            if yodkaysum_row:
                h_val = ws_prev[f"H{yodkaysum_row}"].value
                
                # Check if this is a valid working day value
                if self._is_valid_cumulative_value(h_val):
                    return prev_sheet_name, yodkaysum_row
            
            prev_day -= 1
        
        return None, None
    
    def _find_cumulative_sales_row(self, worksheet) -> Optional[int]:
        """
        Find the row containing 'ยอดขายสะสม' in column D.
        
        Args:
            worksheet: Openpyxl worksheet object
            
        Returns:
            Row number if found, None otherwise
        """
        for r in range(1, worksheet.max_row + 1):
            d_val = worksheet[f"D{r}"].value
            if d_val == "ยอดขายสะสม":
                return r
        return None
    
    def _is_valid_cumulative_value(self, value) -> bool:
        """
        Check if the value in the cumulative sales cell represents a valid working day.
        
        Args:
            value: The cell value to check
            
        Returns:
            True if it's a valid cumulative value, False if it's a holiday/invalid
        """
        # Handle None, empty string, or 0 values
        if value in (None, "", 0, "=0"):
            return False
        
        # If it's a string (formula), check if it's a valid cumulative formula
        if isinstance(value, str):
            return self._is_valid_formula_value(value.strip())
        
        # Numeric values
        if isinstance(value, (int, float)):
            return value > 0
        
        return False
    
    def _is_valid_formula_value(self, value: str) -> bool:
        """
        Check if a string formula value represents a valid working day.
        
        Args:
            value: The formula string to validate
            
        Returns:
            True if it's a valid working day formula, False otherwise
        """
        # Empty after stripping
        if not value:
            return False
        
        # Check if it's a formula
        if value.startswith("="):
            # Valid cumulative formulas should contain "SUM" and reference to another sheet
            # Pattern like: =SUM(H5:Hn)+'day'!Hn or just =SUM(H5:Hn) for day 1
            if "SUM" in value.upper():
                return self._validate_sum_formula(value)
            
            # MODIFICATION: Check for patterns like =Hn+'day'!Hn
            # This is a valid cumulative formula that adds a cell from the current sheet
            # to a cell from a previous day's sheet.
            if "+" in value and "!" in value:
                return self._validate_addition_formula(value)
            
            # Other formulas like =H7 (simple cell reference) are likely holiday placeholders
            return False
        else:
            # Non-formula values: check if it's a valid number
            try:
                num_val = float(value)
                return num_val > 0
            except (ValueError, TypeError):
                return False
    
    def _validate_sum_formula(self, formula: str) -> bool:
        """
        Validate if a SUM formula is a proper cumulative sales formula.
        
        Args:
            formula: The SUM formula to validate
            
        Returns:
            True if it's a valid cumulative SUM formula
        """
        # This looks like a valid cumulative formula
        # Additional check: if it contains a sheet reference, it should be in the format 'number'!
        if "!" in formula:
            # Extract sheet reference pattern
            sheet_ref_pattern = r"'(\d+)'!"
            if re.search(sheet_ref_pattern, formula):
                return True
        else:
            # SUM without sheet reference (could be day 1)
            return True
        
        return False

    def _validate_addition_formula(self, formula: str) -> bool:
        """
        Validate if an addition formula is a proper cumulative sales formula.
        A valid formula should look like =H7+'2'!H8

        Args:
            formula: The addition formula to validate

        Returns:
            True if it's a valid cumulative addition formula
        """
        # A simple check is to ensure it contains a reference to another sheet.
        # The presence of '!' is a strong indicator.
        # This distinguishes it from simple additions on the same sheet.
        sheet_ref_pattern = r"'(\d+)'!"
        if re.search(sheet_ref_pattern, formula):
            return True

        return False
