import os
from .result import Result
from src.db.config_queries import get_config
from src.db.path_config_queries import get_all_path_configs

class ConfigManager:
    """
    Handles loading and validation of bills processing configuration from the database.
    """
    def load_config(self) -> Result:
        """
        Load and validate the bills processing configuration.
        
        Returns:
            Result: Contains a config dict on success, or an error message on failure.
        """
        try:
            # Get the default inventory code from the general app config
            default_inventory_code = get_config("bills_process_inventory_code")
            if not default_inventory_code:
                return Result.error("❌ ไม่ได้ตั้งค่ารหัสสินค้าคงคลังเริ่มต้น กรุณาตั้งค่าในหน้า 'การตั้งค่าเส้นทาง'")

            # Get all available path configurations
            all_paths = get_all_path_configs()
            if not all_paths:
                return Result.error("❌ ไม่พบการตั้งค่าเส้นทาง กรุณาเพิ่มการตั้งค่าในหน้า 'การตั้งค่าเส้นทาง'")

            # Find the template directory for the default inventory code
            template_dir = None
            for path_config in all_paths:
                if path_config['inventory_code'] == default_inventory_code:
                    template_dir = path_config['template_dir']
                    break
            
            if not template_dir:
                return Result.error(f"❌ ไม่พบเส้นทางสำหรับรหัสสินค้าคงคลังเริ่มต้น '{default_inventory_code}' กรุณาตรวจสอบ 'การตั้งค่าเส้นทาง'")

            # Normalize the path to ensure consistent separators
            normalized_path = os.path.normpath(template_dir)

            return Result.success({
                "base_path": normalized_path,
                "inventory_code": default_inventory_code
            })

        except Exception as e:
            return Result.error(f"❌ เกิดข้อผิดพลาดที่ไม่คาดคิดขณะโหลดการตั้งค่า: {e}")
