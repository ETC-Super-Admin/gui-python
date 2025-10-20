import os
import subprocess
import sys
from .result import Result
from .config_manager import ConfigManager

class FileOpener:
    """
    Handles opening files with the system's default application.
    """
    
    def __init__(self):
        self.config_manager = ConfigManager()

    def open_monthly_report_file(self, year: int, month: int) -> Result:
        """
        Opens the monthly report .xlsx file for the selected year/month.
        """
        # 1. Get configuration
        config_result = self.config_manager.load_config()
        if not config_result.success:
            return config_result
        config = config_result.data
        base_path = config['base_path']

        # 2. Build the file path
        folder = os.path.join(base_path, f"Year_{year:04d}")
        filename = f"Monthly_Report_{month}_{year}.xlsx"
        file_path = os.path.join(folder, filename)
        
        if not os.path.exists(file_path):
            return Result.warning(f"❌ Monthly report file not found:\n{file_path}")
        
        # 3. Open the file with the default application
        try:
            self._open_file_with_system(file_path)
            return Result.success(f"✅ Successfully opened file:\n{file_path}")
            
        except Exception as e:
            return Result.error(f"❌ Could not open file: {e}")
    
    def _open_file_with_system(self, file_path):
        """Opens a file with the system's default application."""
        if sys.platform.startswith('darwin'): # macOS
            subprocess.call(('open', file_path))
        elif os.name == 'nt': # Windows
            os.startfile(file_path)
        elif os.name == 'posix': # Linux, Unix
            subprocess.call(('xdg-open', file_path))
        else:
            raise OSError("Unsupported operating system for opening files.")
