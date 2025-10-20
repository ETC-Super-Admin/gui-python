from openpyxl.styles import Font

class FormulaManager:
    """
    Manages the creation and insertion of summary formulas into the worksheet.
    """
    
    def __init__(self):
        self.bold_font = Font(name="Tahoma", size=12, bold=True)
        self.red_font = Font(name="Tahoma", size=12, color="FF0000")
    
    def add_summary_formulas(self, worksheet, first_data_row: int, last_data_row: int):
        """
        Adds SUM formulas for columns F, G, H and a ROWS formula for column A
        to the two rows immediately following the last data row.
        """
        if last_data_row < first_data_row:
            return # No data to summarize

        constant_template_row = last_data_row + 1
        next_row = constant_template_row + 1
        
        # Add sum formulas for F, G, H columns
        self._add_sum_formula(worksheet, "F", first_data_row, last_data_row, constant_template_row, self.bold_font)
        self._add_sum_formula(worksheet, "G", first_data_row, last_data_row, constant_template_row, self.bold_font)
        self._add_sum_formula(worksheet, "H", first_data_row, last_data_row, constant_template_row, self.bold_font)
        
        # Add ROWS formula for column A (red text)
        self._add_rows_formula(worksheet, "A", first_data_row, last_data_row, constant_template_row, self.red_font)
        
        # Also fill the same formulas in the next row (for a freeze pane)
        self._add_sum_formula(worksheet, "F", first_data_row, last_data_row, next_row, self.bold_font)
        self._add_sum_formula(worksheet, "G", first_data_row, last_data_row, next_row, self.bold_font)
        self._add_sum_formula(worksheet, "H", first_data_row, last_data_row, next_row, self.bold_font)
        
        # Add ROWS formula for column A (bold text)
        self._add_rows_formula(worksheet, "A", first_data_row, last_data_row, next_row, self.bold_font)
    
    def _add_sum_formula(self, worksheet, column: str, first_row: int, last_row: int, target_row: int, font: Font):
        """Helper to add a SUM formula to a specified cell."""
        formula = f"=SUM({column}{first_row}:{column}{last_row})"
        cell = worksheet[f"{column}{target_row}"]
        cell.value = formula
        cell.font = font
    
    def _add_rows_formula(self, worksheet, column: str, first_row: int, last_row: int, target_row: int, font: Font):
        """Helper to add a ROWS formula to a specified cell."""
        formula = f"=ROWS({column}{first_row}:{column}{last_row})"
        cell = worksheet[f"{column}{target_row}"]
        cell.value = formula
        cell.font = font
