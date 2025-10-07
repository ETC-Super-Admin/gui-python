from PySide6.QtWidgets import QFileDialog, QMessageBox
from PySide6.QtCore import QSettings, QStandardPaths
import openpyxl
from datetime import datetime
import os

def export_table_to_excel(parent_widget, table_widget, sheet_title="Sheet1", button=None):
    """
    Exports the visible data from a QTableWidget to an Excel file.

    Args:
        parent_widget (QWidget): The parent widget for dialogs.
        table_widget (QTableWidget): The table to export data from.
        sheet_title (str): The title for the Excel sheet.
        button (QPushButton, optional): The button that triggered the export, to manage its state.
    """
    original_text = ""
    if button:
        original_text = button.text()
        button.setText("Exporting...")
        button.setEnabled(False)

    settings = QSettings("ProAuto", "App")
    last_export_directory = settings.value("excel/last_export_directory", 
                                           QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation))

    try:
        # 1. Get Headers
        headers = []
        for col in range(table_widget.columnCount()):
            if not table_widget.isColumnHidden(col):
                headers.append(table_widget.horizontalHeaderItem(col).text())

        # 2. Get Data from visible rows
        data_to_export = []
        for row in range(table_widget.rowCount()):
            if not table_widget.isRowHidden(row):
                row_data = []
                for col in range(table_widget.columnCount()):
                    if not table_widget.isColumnHidden(col):
                        item = table_widget.item(row, col)
                        row_data.append(item.text() if item else "")
                data_to_export.append(row_data)

        if not data_to_export:
            QMessageBox.information(parent_widget, "Export to Excel", "No data to export.")
            return

        # 3. Generate filename and ask user for file path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"{sheet_title.lower()}_{timestamp}.xlsx"

        file_path, _ = QFileDialog.getSaveFileName(
            parent_widget, 
            "Save Excel File", 
            os.path.join(last_export_directory, default_filename), # Use last directory
            "Excel Files (*.xlsx)"
        )

        if not file_path:
            return  # User cancelled

        # Save the newly selected directory
        settings.setValue("excel/last_export_directory", os.path.dirname(file_path))

        # 4. Write to Excel file
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = sheet_title

        sheet.append(headers)
        for row_data in data_to_export:
            sheet.append(row_data)

        # Auto-adjust column widths
        for col_idx, header in enumerate(headers, 1):
            column_letter = openpyxl.utils.get_column_letter(col_idx)
            max_length = len(header)
            for row in data_to_export:
                if len(str(row[col_idx-1])) > max_length:
                    max_length = len(str(row[col_idx-1]))
            adjusted_width = (max_length + 2) * 1.2
            sheet.column_dimensions[column_letter].width = adjusted_width

        workbook.save(file_path)
        QMessageBox.information(parent_widget, "Export Successful", f"Data successfully exported to\n{file_path}")

    except Exception as e:
        QMessageBox.warning(parent_widget, "Export Failed", f"An error occurred while exporting the file: {e}")
    finally:
        if button:
            button.setText(original_text)
            button.setEnabled(True)