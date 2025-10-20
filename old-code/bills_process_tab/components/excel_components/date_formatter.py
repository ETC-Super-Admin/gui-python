# src/components/tabs/bills_process_tab/components/excel_components/date_formatter.py
from openpyxl.styles import Font

class DateFormatter:
    """
    Handles date formatting for Excel processing.
    Specializes in Thai Buddhist Era date formatting.
    """
    
    def __init__(self):
        self.date_font = Font(name="Tahoma", size=14, bold=True)
    
    def format_thai_date(self, day: int, month: int, year: int) -> str:
        """
        Format date to Thai Buddhist Era format (d/m/YYYY).
        
        Args:
            day: Day number
            month: Month number
            year: Year in AD (will be converted to B.E.)
            
        Returns:
            Formatted date string in Thai B.E. format
        """
        # Convert AD year to Buddhist Era (add 543 years)
        thai_year = year + 543
        
        # Format as d/m/yyyy (no leading zeros for day and month)
        formatted_date = f"{day}/{month}/{thai_year}"
        return formatted_date