import os
from PySide6.QtWidgets import QMessageBox
from .result import Result
from .config_manager import ConfigManager
from src.utils.unmerge_xlsx import unmerge_cells_in_file
from src.db.unmerged_files_queries import add_unmerged_file, is_file_unmerged, clear_unmerged_files_for_day

class FileUnmerger:
    """
    Handles unmerging cells in daily bill Excel files.
    """
    
    def __init__(self):
        self.config_manager = ConfigManager()

    def unmerge_daily_bills_files(self, year: int, month: int, day: int, **kwargs) -> Result:
        """
        Unmerges cells in all daily bills .xlsx files for the specified date, skipping already unmerged files.
        """
        progress_callback = kwargs.get('progress_callback')

        def report_progress(msg):
            if progress_callback:
                progress_callback.emit(msg)

        # 1. Get configuration
        report_progress("กำลังโหลดการตั้งค่า...")
        config_result = self.config_manager.load_config()
        if not config_result.success:
            return config_result
        config = config_result.data
        base_path = config['base_path']
        report_progress("✅ โหลดการตั้งค่าเสร็จสมบูรณ์")

        # 2. Construct path to the daily bills directory
        daily_bills_dir = os.path.join(
            base_path,
            f"Year_{year:04d}",
            f"Month_{month:02d}",
            "Daily_Bills",
            f"Day_{day}"
        )
        report_progress(f"ℹ️ ไดเรกทอรีเป้าหมาย: {daily_bills_dir}")
        
        if not os.path.exists(daily_bills_dir):
            return Result.warning(f"❌ ไม่พบไดเรกทอรีบิลรายวัน:\n{daily_bills_dir}")

        # 3. Find all Excel files and filter out already unmerged ones
        try:
            report_progress("กำลังสแกนหาไฟล์ในไดเรกทอรี...")
            all_excel_files = [f for f in os.listdir(daily_bills_dir) if f.lower().endswith('.xlsx') and not f.startswith('~$')]
            report_progress(f"พบไฟล์ Excel ทั้งหมด {len(all_excel_files)} ไฟล์")
        except Exception as e:
            return Result.error(f"❌ ไม่สามารถอ่านไดเรกทอรี: {daily_bills_dir}\n{e}")
        
        if not all_excel_files:
            return Result.info(f"ไม่พบไฟล์ Excel ในไดเรกทอรี:\n{daily_bills_dir}")

        report_progress("กำลังตรวจสอบฐานข้อมูลสำหรับไฟล์ที่แยกเซลล์แล้ว...")
        files_to_process = [f for f in all_excel_files if not is_file_unmerged(os.path.join(daily_bills_dir, f))]
        skipped_count = len(all_excel_files) - len(files_to_process)
        report_progress(f"พบไฟล์ใหม่ {len(files_to_process)} ไฟล์ที่ต้องประมวลผล")

        if not files_to_process:
            return Result.success(f"✅ ไฟล์ {skipped_count} ไฟล์สำหรับวันนี้ได้รับการแยกเซลล์แล้ว")

        # 4. Unmerge new files
        unmerged_files = []
        errors = []
        for fname in files_to_process:
            file_path = os.path.join(daily_bills_dir, fname)
            report_progress(f"--- กำลังประมวลผล: {fname} ---")
            try:
                report_progress(f"  > กำลังแยกเซลล์...")
                if unmerge_cells_in_file(file_path):
                    report_progress(f"  > แยกเซลล์สำเร็จ กำลังเพิ่มลงในฐานข้อมูล...")
                    add_unmerged_file(file_path)
                    unmerged_files.append(fname)
                    report_progress(f"  > เสร็จสิ้น")
                else:
                    errors.append(f"❌ ไม่สามารถแยกเซลล์ {fname} ได้ ไฟล์อาจถูกเปิดอยู่หรือเสียหาย")
            except Exception as e:
                errors.append(f"❌ เกิดข้อผิดพลาดร้ายแรงขณะประมวลผล {fname}: {e}")
        
        # 5. Format and return result
        report_lines = []
        if unmerged_files:
            report_lines.append(f"✅ แยกเซลล์ไฟล์ใหม่ {len(unmerged_files)} ไฟล์สำเร็จ:\n" + "\n".join(unmerged_files))
        
        if skipped_count > 0:
            report_lines.append(f"ℹ️ ข้ามไฟล์ {skipped_count} ไฟล์ที่ได้รับการแยกเซลล์แล้ว")

        if errors:
            report_lines.insert(0, "เสร็จสิ้นพร้อมข้อผิดพลาดบางประการ:")
            report_lines.append("\nข้อผิดพลาด:\n" + "\n".join(errors))
            return Result.error("\n".join(report_lines))

        return Result.success("\n".join(report_lines))

    def clear_unmerged_cache(self, year: int, month: int, day: int) -> Result:
        """Clears the unmerged file cache for a specific day."""
        success, message = clear_unmerged_files_for_day(year, month, day)
        if success:
            return Result.success(message)
        else:
            return Result.error(f"ข้อผิดพลาดฐานข้อมูลขณะล้างแคชไฟล์ที่แยกเซลล์: {e}")
