# src/components/tabs/bills_process_tab/components/file_scanner.py
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
            Result: Contains file information on success
        """
        try:
            # Scan for template files
            template_scan_result = self._scan_template_files(year, month)
            if not template_scan_result.success:
                return template_scan_result
            
            template_files = template_scan_result.data['template_files']
            template_file_path = template_scan_result.data['template_file_path']
            template_files_str = template_scan_result.data['template_files_str']
            
            # Scan for daily files
            daily_scan_result = self._scan_daily_files(year, month, day)
            if not daily_scan_result.success:
                # Build error message with template info
                msg = (
                    f"Template file:\n{template_files_str}\n\n"
                    f"{daily_scan_result.message}"
                )
                return Result.error(msg)
            
            daily_files = daily_scan_result.data['daily_files']
            target_dir = daily_scan_result.data['target_dir']
            files_message = daily_scan_result.data['files_message']
            
            return Result.success({
                'template_files': template_files,
                'template_file_path': template_file_path,
                'template_files_str': template_files_str,
                'daily_files': daily_files,
                'target_dir': target_dir,
                'files_message': files_message
            })
            
        except Exception as e:
            msg = f"❌ Error scanning files: {e}"
            from src.components.common.custom_messagebox import CustomMessageBox, MessageType
            if isinstance(e, PermissionError):
                CustomMessageBox.show_error(None, "File Access Error", "❌ ไฟล์แม่แบบถูกเปิดอยู่ กรุณาปิดไฟล์และลองใหม่อีกครั้ง")
                msg = "❌ ไฟล์แม่แบบถูกเปิดอยู่ กรุณาปิดไฟล์และลองใหม่อีกครั้ง"
            return Result.error(msg)
    
    def _scan_template_files(self, year: int, month: int) -> Result:
        """Scan for template files in the month directory."""
        month_dir = os.path.join(
            self.base_path,
            f"Year_{year:04d}",
            f"Month_{month:02d}"
        )
        
        template_files = []
        template_file_path = None
        
        if os.path.exists(month_dir):
            for fname in os.listdir(month_dir):
                fpath = os.path.join(month_dir, fname)
                if os.path.isfile(fpath) and fname.lower().endswith('.xlsx'):
                    template_files.append(fname)
                    # Pick the first template file found
                    if not template_file_path:
                        template_file_path = fpath
        
        template_files_str = "None found" if not template_files else "\n".join(template_files)
        
        return Result.success({
            'template_files': template_files,
            'template_file_path': template_file_path,
            'template_files_str': template_files_str
        })
    
    def _scan_daily_files(self, year: int, month: int, day: int) -> Result:
        """Scan for daily bill files in the day directory."""
        day_folder = f"Day_{day}"
        target_dir = os.path.join(
            self.base_path,
            f"Year_{year:04d}",
            f"Month_{month:02d}",
            "Daily_Bills",
            day_folder
        )
        
        if not os.path.exists(target_dir):
            return Result.error(f"❌ Directory not found:\n{target_dir}")
        
        files = [f for f in os.listdir(target_dir) if f.lower().endswith('.xlsx')]
        
        if not files:
            files_message = "No files found in this directory."
            return Result.warning("No Excel files found in directory.", {
                'daily_files': files,
                'target_dir': target_dir,
                'files_message': files_message
            })
        
        files_message = "Files:\n" + "\n".join(files)
        
        return Result.success({
            'daily_files': files,
            'target_dir': target_dir,
            'files_message': files_message
        })