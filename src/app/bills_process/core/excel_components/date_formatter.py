from openpyxl.styles import Font

class DateFormatter:
    """
    Handles date formatting for the Excel template, specializing in Thai Buddhist Era dates.
    """
    
    def __init__(self):
        self.date_font = Font(name="Tahoma", size=14, bold=True)
    
    def format_thai_date(self, day: int, month: int, year: int) -> str:
        """
        Formats a date to the Thai Buddhist Era format (d/m/YYYY).
        
        Args:
            day: The day of the month.
            month: The month number.
            year: The year in AD, which will be converted to B.E.
            
        Returns:
            A formatted date string in Thai B.E. format.
        """
        # Convert AD year to Buddhist Era by adding 543 years
        thai_year = year + 543
        
        # Format as d/m/yyyy (no leading zeros for day and month)
        return f"{day}/{month}/{thai_year}"
