import os
from PySide6.QtWidgets import QMessageBox
from .result import Result
from .config_manager import ConfigManager
from .excel_components.state_manager import StateManager

class CacheManager:
    """
    Manages the processing state cache for bills processing.
    """
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.state_manager = StateManager()

    def clear_process_cache(self, year: int, month: int, day: int, parent_widget=None) -> Result:
        """
        Deletes the .processing_state.json file for the specified date.
        """
        # 1. Get configuration
        config_result = self.config_manager.load_config()
        if not config_result.success:
            return config_result
        config = config_result.data
        base_path = config['base_path']

        # 2. Construct path to the day directory
        day_path = os.path.join(
            base_path,
            f"Year_{year:04d}",
            f"Month_{month:02d}",
            "Daily_Bills",
            f"Day_{day}"
        )
        
        cache_file = os.path.join(day_path, ".processing_state.json")

        # 3. Ask for confirmation
        if parent_widget:
            reply = QMessageBox.question(
                parent_widget,
                "Confirm Clear Cache",
                "Are you sure you want to clear the cache for this date?\nThis action cannot be undone.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return Result.info("Cache clearing cancelled.")

        # 4. Check if cache file exists and delete it
        if not os.path.exists(cache_file):
            return Result.info("No cache file found for this date.")
        
        try:
            os.remove(cache_file)
            return Result.success("✅ Processing cache cleared successfully.")
        except Exception as e:
            return Result.error(f"❌ An error occurred while clearing cache: {e}")
