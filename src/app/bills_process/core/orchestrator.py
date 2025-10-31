from .config_manager import ConfigManager
from .file_scanner import FileScanner
from .data_collector import DataCollector
from .excel_processor import ExcelProcessor
from .result import Result
from .file_unmerger import FileUnmerger
import os

class Orchestrator:
    """
    Orchestrates the entire bills processing workflow.
    """
    def __init__(self, date):
        self.date = date
        self.year = date.year()
        self.month = date.month()
        self.day = date.day()

    def run_process_files(self, **kwargs) -> Result:
        """
        Executes the main 'Process Files' workflow.
        """
        progress_callback = kwargs.get('progress_callback')
        def report_progress(msg):
            if progress_callback:
                progress_callback.emit(msg)
        
        try:
            report_progress("🚀 กำลังเริ่มต้นขั้นตอนการประมวลผลบิล...")

            # 1. Unmerge Files
            report_progress("1/5: กำลังแยกเซลล์ไฟล์บิลรายวัน...")
            file_unmerger = FileUnmerger()
            unmerge_result = file_unmerger.unmerge_daily_bills_files(self.year, self.month, self.day, **kwargs)
            if unmerge_result.message:
                # Sanitize message for display, as it may contain newlines
                sanitized_message = unmerge_result.message.replace(os.linesep, ' | ')
                report_progress(f"  > {sanitized_message}")
            if not unmerge_result.success and unmerge_result.message_type == 'error':
                 return unmerge_result # Stop on critical unmerge error
            report_progress("✅ ขั้นตอนการแยกเซลล์เสร็จสมบูรณ์")

            # 2. Load Config
            report_progress("2/5: กำลังโหลดการตั้งค่า...")
            config_manager = ConfigManager()
            config_result = config_manager.load_config()
            if not config_result.success:
                return config_result
            config = config_result.data
            report_progress("✅ โหลดการตั้งค่าเสร็จสมบูรณ์")
            
            # 3. Scan for files
            report_progress("3/5: กำลังสแกนหาไฟล์...")
            file_scanner = FileScanner(config['base_path'])
            scan_result = file_scanner.scan_files(self.year, self.month, self.day)
            if not scan_result.success:
                # Allow process to continue if scan only returns a warning (e.g., no files found)
                if scan_result.message_type == 'error':
                    return scan_result
            
            files_data = scan_result.data
            template_path = files_data['template_file_path']
            daily_files = files_data['daily_files']
            target_dir = files_data['target_dir']
            report_progress(f"พบไฟล์บิลรายวัน {len(daily_files)} ไฟล์")

            if not daily_files:
                report_progress("ไม่มีไฟล์บิลรายวันใหม่ให้ประมวลผล")
                return Result.info("ไม่มีไฟล์บิลรายวันใหม่ให้ประมวลผล")

            # 4. Collect data
            report_progress("4/5: กำลังรวบรวมข้อมูลจากไฟล์...")
            data_collector = DataCollector()
            collection_result = data_collector.collect_from_files(daily_files, target_dir, **kwargs)
            if not collection_result.success:
                return collection_result
            collected_data = collection_result.data
            report_progress("✅ รวบรวมข้อมูลเสร็จสมบูรณ์")

            # 5. Process Excel
            report_progress("5/5: กำลังประมวลผลไฟล์แม่แบบ Excel...")
            excel_processor = ExcelProcessor(
                template_path=template_path,
                data=collected_data,
                date=self.date,
                inventory_code=config['inventory_code'],
                target_dir=target_dir,
                daily_files=daily_files
            )
            process_result = excel_processor.process(**kwargs)
            report_progress(f"🎉 ขั้นตอนการทำงานเสร็จสิ้น. {process_result.message}")

            return process_result
        except Exception as e:
            return Result.error(f"เกิดข้อผิดพลาดที่ไม่คาดคิดในตัวจัดการ: {e}")
