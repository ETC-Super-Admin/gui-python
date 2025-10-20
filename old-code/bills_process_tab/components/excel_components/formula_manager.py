# src/components/tabs/bills_process_tab/components/excel_components/formula_manager.py
from openpyxl.styles import Font

class FormulaManager:
    """
    Manages Excel formulas creation and insertion.
    Handles SUM formulas, ROWS formulas, and other calculations.
    """
    
    def __init__(self):
        self.bold_font = Font(name="Tahoma", size=12, bold=True)
        self.red_font = Font(name="Tahoma", size=12, color="FF0000")
    
    def add_sum_formulas(self, worksheet, first_data_row: int, last_data_row: int):
        """
        Add SUM formulas for columns F, G, H and ROWS formulas for column A.
        
        Args:
            worksheet: Openpyxl worksheet object
            first_data_row: First row containing data
            last_data_row: Last row containing data
        """
        constant_template_row = last_data_row + 1
        next_row = constant_template_row + 1
        
        # Add sum formulas for F, G, H columns in constant_template_row
        self._add_sum_formula(worksheet, "F", first_data_row, last_data_row, constant_template_row, self.bold_font)
        self._add_sum_formula(worksheet, "G", first_data_row, last_data_row, constant_template_row, self.bold_font)
        self._add_sum_formula(worksheet, "H", first_data_row, last_data_row, constant_template_row, self.bold_font)
        
        # Fill ROWS formula in column A for constant_template_row (red text)
        self._add_rows_formula(worksheet, "A", first_data_row, last_data_row, constant_template_row, self.red_font)
        
        # Also fill the same formulas in the next row (freeze row)
        self._add_sum_formula(worksheet, "F", first_data_row, last_data_row, next_row, self.bold_font)
        self._add_sum_formula(worksheet, "G", first_data_row, last_data_row, next_row, self.bold_font)
        self._add_sum_formula(worksheet, "H", first_data_row, last_data_row, next_row, self.bold_font)
        
        # Fill ROWS formula in column A for next_row (bold text)
        self._add_rows_formula(worksheet, "A", first_data_row, last_data_row, next_row, self.bold_font)
    
    def _add_sum_formula(self, worksheet, column: str, first_row: int, last_row: int, target_row: int, font):
        """Add a SUM formula to the specified cell."""
        formula = f"=SUM({column}{first_row}:{column}{last_row})"
        worksheet[f"{column}{target_row}"] = formula
        worksheet[f"{column}{target_row}"].font = font
    
    def _add_rows_formula(self, worksheet, column: str, first_row: int, last_row: int, target_row: int, font):
        """Add a ROWS formula to the specified cell."""
        formula = f"=ROWS({column}{first_row}:{column}{last_row})"
        worksheet[f"{column}{target_row}"] = formula
        worksheet[f"{column}{target_row}"].font = font