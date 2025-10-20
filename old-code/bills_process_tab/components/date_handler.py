from PyQt5.QtCore import QDate

class DateHandler:
    """Handles date-related operations for the bills process tab."""
    
    def __init__(self, date_input_widget):
        self.date_input = date_input_widget
    
    def get_selected_date(self):
        """Return the currently selected date as QDate."""
        return self.date_input.date()
    
    def get_date_components(self):
        """Return year, month, day as separate integers."""
        selected_date = self.date_input.date()
        # Return the original numeric values as these might be needed by other components
        return selected_date.year(), selected_date.month(), selected_date.day()
    
    def get_formatted_date_components(self):
        """Return year, month (02d), and day (Day_X) as formatted strings."""
        selected_date = self.date_input.date()
        year = selected_date.year()
        month = f"{selected_date.month():02d}"
        day = f"Day_{selected_date.day()}"
        return str(year), month, day