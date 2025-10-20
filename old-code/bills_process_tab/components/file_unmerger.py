import os
import json
from src.utils.unmerge_xlsx import unmerge_daily_bills_files_in_dir
from src.components.common.custom_messagebox import CustomMessageBox, MessageType

class FileUnmerger:
    """Handles file unmerging functionality."""
    
    def __init__(self, parent_widget, file1_path):
        self.parent = parent_widget
        self.file1_path = file1_path
    
    def unmerge_daily_bills_files(self, year, month, day):
        """Unmerge cells in all daily bills .xlsx files under the matched year/month/day directory."""
        path1 = self._get_path1_from_config()
        if path1 is None:
            return "❌ ไม่สามารถดึงค่า path1 จากการตั้งค่าได้", "error"
        
        try:
            # Pass parent so CustomMessageBox can show dialogs
            result = unmerge_daily_bills_files_in_dir(path1, year, month, day, parent=self.parent)
            return result, "info"
        except Exception as e:
            error_msg = f"❌ เกิดข้อผิดพลาดในการแยกการรวมเซลล์ไฟล์: {e}"
            CustomMessageBox.show_error(self.parent, "Unmerge Error", f"เกิดข้อผิดพลาดระหว่างการแยกการรวมเซลล์ไฟล์:\n{str(e)}")
            return error_msg, "error"
    
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
