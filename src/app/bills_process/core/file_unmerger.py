import os
from .result import Result
from .config_manager import ConfigManager
from .excel_components.unmerge_utils import unmerge_cells_in_file

class FileUnmerger:
    """
    Handles unmerging cells in daily bill Excel files.
    """
    
    def __init__(self):
        self.config_manager = ConfigManager()

    def unmerge_daily_bills_files(self, year: int, month: int, day: int) -> Result:
        """
        Unmerges cells in all daily bills .xlsx files for the specified date.
        """
        # 1. Get configuration
        config_result = self.config_manager.load_config()
        if not config_result.success:
            return config_result
        config = config_result.data
        base_path = config['base_path']

        # 2. Construct path to the daily bills directory
        daily_bills_dir = os.path.join(
            base_path,
            f"Year_{year:04d}",
            f"Month_{month:02d}",
            "Daily_Bills",
            f"Day_{day}"
        )
        
        if not os.path.exists(daily_bills_dir):
            return Result.warning(f"❌ Daily bills directory not found:\n{daily_bills_dir}")

        # 3. Find all Excel files
        excel_files = [f for f in os.listdir(daily_bills_dir) if f.lower().endswith('.xlsx') and not f.startswith('~$')]
        
        if not excel_files:
            return Result.info(f"No Excel files found in directory:\n{daily_bills_dir}")

        # 4. Unmerge cells in each file
        unmerged_count = 0
        errors = []
        for fname in excel_files:
            file_path = os.path.join(daily_bills_dir, fname)
            try:
                unmerge_cells_in_file(file_path)
                unmerged_count += 1
            except PermissionError:
                errors.append(f"❌ Permission denied for {fname}. File might be open.")
            except Exception as e:
                errors.append(f"❌ Error unmerging {fname}: {e}")
        
        if errors:
            return Result.error(f"Completed with errors. Unmerged {unmerged_count} files. Errors:\n" + "\n".join(errors))
        
        return Result.success(f"✅ Successfully unmerged cells in {unmerged_count} file(s).")
