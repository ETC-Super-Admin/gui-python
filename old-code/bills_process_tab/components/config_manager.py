# src/components/tabs/bills_process_tab/components/config_manager.py
import os
import json
from platformdirs import user_data_dir
from .result import Result

class TemplateConfigManager:
    """
    Handles loading and validation of template configuration settings.
    """
    
    def __init__(self, app_name: str = "ProAuto", app_author: str = "ETC-ProAuto"):
        self.app_name = app_name
        self.app_author = app_author
        self.config_file = self._get_config_file_path()
    
    def _get_config_file_path(self) -> str:
        """Get the path to the configuration file."""
        app_dir = user_data_dir(self.app_name, self.app_author)
        return os.path.join(app_dir, "template_path_settings.json")
    
    def load_config(self) -> Result:
        """
        Load and validate the template configuration.
        
        Returns:
            Result: Contains config dict on success, error message on failure
        """
        if not os.path.exists(self.config_file):
            return Result.error("❌ ไม่พบไฟล์การตั้งค่า template path.")
        
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            path1 = config.get("path1", "")
            inventory_code = config.get("inventory_code", "")
            
            if not path1:
                return Result.warning("⚠️ ไม่พบ template path ในไฟล์การตั้งค่า.")
            
            return Result.success({
                "path1": path1,
                "inventory_code": inventory_code
            })
            
        except json.JSONDecodeError as e:
            return Result.error(f"❌ ไฟล์ config ไม่ใช่ JSON ที่ถูกต้อง: {e}")
        except Exception as e:
            return Result.error(f"❌ เกิดข้อผิดพลาดในการอ่านไฟล์การตั้งค่า template path: {e}")