import os
import json
from PyQt5.QtWidgets import QMessageBox
from src.components.common.custom_messagebox import CustomMessageBox

class CacheManager:
    """Handles cache management for bills processing."""
    
    def __init__(self, parent_widget, app_dir, file1_path):
        self.parent = parent_widget
        self.app_dir = app_dir
        self.file1_path = file1_path
    
    def clear_process_cache(self, year, month, day):
        """Delete the .processing_state.json file for the specified date."""
        # Ask for confirmation first
        response = CustomMessageBox.show_warning(
            self.parent,
            "ยืนยันการล้างแคช",
            "คุณแน่ใจหรือไม่ว่าต้องการล้างแคชสำหรับวันดังกล่าว?\nไม่สามารถย้อนกลับได้.",
            buttons=QMessageBox.Yes | QMessageBox.No
        )
        
        if response != QMessageBox.Yes:
            CustomMessageBox.show_info(self.parent, "ยกเลิก", "ยกเลิกการล้างแคชแล้ว.")
            return "ยกเลิกการล้างแคชแล้ว.", "info"

        # Get path1 from config
        path1 = self._get_path1_from_config()
        if path1 is None:
            CustomMessageBox.show_error(self.parent, "ข้อผิดพลาดการตั้งค่า", "ยังไม่ได้ตั้งค่า Path1 กรุณาตั้งค่าในหน้าตั้งค่า.")
            return "ยังไม่ได้ตั้งค่า Path1 กรุณาตั้งค่าในหน้าตั้งค่า.", "error"
        
        try:
            # Construct path to the day directory following the actual structure
            day_path = os.path.join(
                path1,
                f"Year_{year}",
                f"Month_{month:02d}",
                "Daily_Bills",
                f"Day_{day}"
            )
            
            # If the directory doesn't exist, no cache to clear
            if not os.path.exists(day_path):
                CustomMessageBox.show_info(self.parent, "ไม่มีแคช", "ไม่มีไดเรกทอรีแคชสำหรับวันดังกล่าว.")
                return "ไม่มีแคชสำหรับวันดังกล่าว.", "info"

            # Path to cache file
            cache_file = os.path.join(day_path, ".processing_state.json")
            
            # Check if cache file exists
            if not os.path.exists(cache_file):
                CustomMessageBox.show_info(self.parent, "ไม่มีแคช", "ไม่พบไฟล์แคชสำหรับวันดังกล่าว.")
                return "ไม่พบไฟล์แคช.", "info"
            
            # Delete the cache file
            os.remove(cache_file)
            
            CustomMessageBox.show_success(self.parent, "ล้างแคชสำเร็จ", "ล้างแคชกระบวนการเรียบร้อยแล้ว.")
            return "✅ ล้างแคชกระบวนการเรียบร้อยแล้ว.", "success"
            
        except Exception as e:
            error_msg = f"❌ เกิดข้อผิดพลาดขณะล้างแคช: {e}"
            CustomMessageBox.show_error(self.parent, "ข้อผิดพลาดแคช", str(e))
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
            CustomMessageBox.show_error(
                self.parent, 
                "ข้อผิดพลาดการตั้งค่า", 
                f"เกิดข้อผิดพลาดขณะอ่าน template_path_settings.json: {e}"
            )
            return None