from PySide6.QtWidgets import QFileDialog, QMessageBox
import openpyxl

def read_excel_to_dict_list(parent_widget):
    """
    Opens a file dialog to select an Excel file and reads its content into a list of dictionaries.

    Args:
        parent_widget (QWidget): The parent widget for the file dialog.

    Returns:
        tuple: A tuple containing (list_of_dicts, filename) or (None, None) if cancelled or failed.
    """
    file_path, _ = QFileDialog.getOpenFileName(
        parent_widget,
        "Open Excel File",
        "",
        "Excel Files (*.xlsx *.xls)"
    )

    if not file_path:
        return None, None

    try:
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active

        # Read header row
        headers = [cell.value for cell in sheet[1]]

        # Read data rows into a list of dictionaries
        data = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            row_data = dict(zip(headers, row))
            data.append(row_data)
        
        return data, file_path

    except Exception as e:
        QMessageBox.warning(
            parent_widget, 
            "Import Failed", 
            f"An error occurred while reading the file: {e}"
        )
        return None, None
