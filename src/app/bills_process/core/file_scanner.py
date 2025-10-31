import os
from typing import List
from .result import Result

class FileScanner:
    """
    Handles scanning for template files and daily bill files in the directory structure.
    """
    
    def __init__(self, base_path: str):
        self.base_path = base_path
    
    def scan_files(self, year: int, month: int, day: int) -> Result:
        """
        Scan for template and daily files based on the given date.
        
        Returns:
            Result: Contains file information on success.
        """
        try:
            # Scan for template file
            template_scan_result = self._scan_template_file(year, month)
            if not template_scan_result.success:
                return template_scan_result
            
            template_file_path = template_scan_result.data['template_file_path']
            
            # Scan for daily files
            daily_scan_result = self._scan_daily_files(year, month, day)
            if not daily_scan_result.success:
                return daily_scan_result
            
            daily_files = daily_scan_result.data['daily_files']
            target_dir = daily_scan_result.data['target_dir']
            
            return Result.success({
                'template_file_path': template_file_path,
                'daily_files': daily_files,
                'target_dir': target_dir,
            })
            
        except Exception as e:
            return Result.error(f"❌ An unexpected error occurred while scanning files: {e}")
    
    def _scan_template_file(self, year: int, month: int) -> Result:
        """Scan for the monthly template file."""
        month_dir = os.path.join(
            self.base_path,
            f"Year_{year:04d}",
            f"Month_{month:02d}"
        )
        
        if not os.path.exists(month_dir):
            return Result.error(f"❌ Month directory not found for template:\n{month_dir}")

        # Construct the expected template filename
        expected_template_filename = f"Monthly_Report_{month}_{year}.xlsx"
        template_file_path = os.path.join(month_dir, expected_template_filename)
        
        if not os.path.exists(template_file_path):
            return Result.error(f"❌ Expected template file not found:\n{template_file_path}")

        return Result.success({
            'template_file_path': template_file_path,
        })
    
    def _scan_daily_files(self, year: int, month: int, day: int) -> Result:
        """Scan for daily bill files in the day directory."""
        target_dir = os.path.join(
            self.base_path,
            f"Year_{year:04d}",
            f"Month_{month:02d}",
            "Daily_Bills",
            f"Day_{day}"
        )
        
        if not os.path.exists(target_dir):
            return Result.error(f"❌ Daily bills directory not found:\n{target_dir}")
        
        files = [f for f in os.listdir(target_dir) if f.lower().endswith('.xlsx') and not f.startswith('~$')]
        
        if not files:
            return Result.warning(f"No daily bill Excel files found in directory:\n{target_dir}", {
                'daily_files': [],
                'target_dir': target_dir,
            })
        
        return Result.success({
            'daily_files': files,
            'target_dir': target_dir,
        })
