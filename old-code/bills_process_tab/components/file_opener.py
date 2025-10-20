# src/components/tabs/bills_process_tab/components/file_opener.py
import os
import json
import subprocess
import sys
from src.components.common.custom_messagebox import CustomMessageBox, MessageType

class FileOpener:
    """Handles file opening functionality."""
    
    def __init__(self, parent_widget, file1_path):
        self.parent = parent_widget
        self.file1_path = file1_path
    
    def open_monthly_report_file(self, year, month):
        """Open the monthly report .xlsx file for the selected year/month."""
        path1 = self._get_path1_from_config()
        if path1 is None:
            return "❌ ไม่สามารถดึงค่าการตั้งค่าได้", "error"
        
        # Build the file path
        folder = os.path.join(path1, f"Year_{year}", f"Month_{month:02d}")
        filename = f"Monthly_Report_{month}_{year}.xlsx"
        file_path = os.path.join(folder, filename)
        
        if not os.path.exists(file_path):
            CustomMessageBox.show_warning(self.parent, "File Not Found", f"ไม่พบไฟล์:\n{file_path}")
            return f"❌ ไม่พบไฟล์: {filename}", "warning"
        
        # Open the file with the default application
        try:
            self._open_file_with_system(file_path)
            return f"✅ เปิดไฟล์สำเร็จ:\n{file_path}", "success"
            
        except Exception as e:
            CustomMessageBox.show_error(self.parent, "Open Error", f"ไม่สามารถเปิดไฟล์ได้:\n{e}")
            return f"❌ ไม่สามารถเปิดไฟล์ได้: {e}", "error"
    
    def _get_path1_from_config(self):
        """Read path1 from template_path_settings.json."""
        if not os.path.exists(self.file1_path):
            CustomMessageBox.show_error(self.parent, "Configuration Error", "ไม่พบไฟล์ template_path_settings.json")
            return None
            
        try:
            with open(self.file1_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                path1 = config.get("path1", None)
                if not path1:
                    CustomMessageBox.show_warning(self.parent, "Configuration Warning", "ไม่พบค่า root path (path1) ในไฟล์ template_path_settings.json.")
                return path1
        except Exception as e:
            CustomMessageBox.show_error(self.parent, "Configuration Error", f"เกิดข้อผิดพลาดในการอ่านไฟล์ template_path_settings.json: {e}")
            return None
    
    def _open_file_with_system(self, file_path):
        """Open file with the system's default application."""
        if sys.platform.startswith('darwin'):
            subprocess.call(('open', file_path))
        elif os.name == 'nt':
            os.startfile(file_path)
        elif os.name == 'posix':
            subprocess.call(('xdg-open', file_path))
        else:
            raise OSError("ไม่รองรับระบบปฏิบัติการนี้สำหรับการเปิดไฟล์")
