# src/components/tabs/bills_process_tab/components/bills_processor.py
import os
import json
from src.utils.day_listing import list_files_and_folders_under_day
from src.components.common.custom_messagebox import CustomMessageBox, MessageType

class BillsProcessor:
    """Handles bills processing logic."""
    
    def __init__(self, parent_widget, app_dir, file1_path, file2_path):
        self.parent = parent_widget
        self.app_dir = app_dir
        self.file1_path = file1_path
        self.file2_path = file2_path
    
    def process_bills(self, year, month, day, show_popup=True):
        """Call listing modules and return results for display."""
        # Get path1 from config
        path1 = self._get_path1_from_config()
        if path1 is None:
            return self._create_error_result("ยังไม่ได้ตั้งค่า Path1 กรุณาตั้งค่าในหน้าตั้งค่า.")
        
        try:
            # List all files and folders under the matched year/month/day directory
            day_result_tuple = list_files_and_folders_under_day(
                path1, year, month, day, config_path=self.file2_path, 
                parent=self.parent,
                show_popup=show_popup
            )
            
            # Extract message and type from the enhanced result
            if isinstance(day_result_tuple, tuple):
                message_text, message_type_str = day_result_tuple
                return message_text, message_type_str
            else:
                # Fallback for backward compatibility
                return str(day_result_tuple), "info"
                
        except Exception as e:
            error_msg = f"❌ เกิดข้อผิดพลาดขณะประมวลผลบิล: {e}"
            # Show error message box
            if show_popup:
                CustomMessageBox.show_error(self.parent, "ข้อผิดพลาดการประมวลผล", f"เกิดข้อผิดพลาดที่ไม่คาดคิด:\n{str(e)}")
            return error_msg, "error"
    
    def _get_path1_from_config(self):
        """Read path1 from template_path_settings.json."""
        if not os.path.exists(self.file1_path):
            return None
            
        try:
            with open(self.file1_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                return config.get("path1", None)
        except Exception as e:
            CustomMessageBox.show_error(self.parent, "ข้อผิดพลาดการตั้งค่า", f"เกิดข้อผิดพลาดขณะอ่าน template_path_settings.json: {e}")
            return None
    
    def _create_error_result(self, message):
        """Create a standardized error result."""
        return f"❌ {message}", "error"