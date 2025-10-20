# src/components/tabs/bills_process_tab/components/template_file_processor.py
import os
from src.components.common.custom_messagebox import CustomMessageBox
from .config_manager import TemplateConfigManager
from .file_scanner import FileScanner
from .data_collector import DataCollector
from .excel_processor import ExcelProcessor

def process_template_file(year=None, month=None, day=None, parent=None, app_name="ProAuto", app_author="ETC-ProAuto"):
    """
    Main entry point for template file processing.
    Orchestrates the entire workflow by delegating to specialized components.
    """
    try:
        # 1. Load and validate configuration
        config_manager = TemplateConfigManager(app_name, app_author)
        config_result = config_manager.load_config()
        if not config_result.success:
            return config_result.message, config_result.message_type
        
        config = config_result.data
        
        # 2. Handle case when no date is provided
        if year is None or month is None or day is None:
            msg = f"📄 เส้นทางไฟล์แม่แบบ: {config['path1']}\n🏷️ รหัสสินค้า: {config['inventory_code']}\n\nยังไม่ได้เลือกวันที่"
            return msg, "info"
        
        # 3. Scan for template and daily files
        file_scanner = FileScanner(config['path1'])
        scan_result = file_scanner.scan_files(year, month, day)
        if not scan_result.success:
            return scan_result.message, scan_result.message_type
        
        template_file_path = scan_result.data['template_file_path']
        daily_files = scan_result.data['daily_files']
        template_files_str = scan_result.data['template_files_str']
        files_message = scan_result.data['files_message']
        target_dir = scan_result.data['target_dir']
        
        # 4. Collect data from daily files
        data_collector = DataCollector()
        collection_result = data_collector.collect_from_files(daily_files, target_dir)
        if not collection_result.success:
            msg = _build_status_message(config, year, month, day, template_files_str, files_message, 
                                      collection_result.message)
            return msg, "error"
        
        collected_data = collection_result.data
        
        # 5. Process Excel template
        excel_processor = ExcelProcessor()
        processing_result = excel_processor.process_template(
            template_file_path, day, daily_files, collected_data, config['inventory_code'], 
            target_dir, parent, year, month
        )
        
        # ข้อความสถานะการประมวลผล
        files_message += "\n\n✅ อัปเดตไฟล์แม่แบบเรียบร้อยแล้ว" if processing_result.success else ""
        msg = _build_status_message(
            config, year, month, day, template_files_str, files_message,
            processing_result.message if not processing_result.success else ""
        )
        return msg, "success" if processing_result.success else processing_result.message_type
        
    except Exception as e:
        from src.components.common.custom_messagebox import CustomMessageBox, MessageType
        msg = f"❌ ข้อผิดพลาดที่ไม่คาดคิดในการประมวลผลไฟล์แม่แบบ: {e}"
        if isinstance(e, PermissionError):
            CustomMessageBox.show_error(parent, "File Access Error", "❌ Template file is currently open. Please close the file and try again.")
            msg = "❌ Template file is currently open. Please close the file and try again."
        return msg, "error"

def _build_status_message(config, year, month, day, template_files_str, files_message, error_msg=""):
    """Build the status message shown to user."""
    msg = (
        f"📄 Template Path: {config['path1']}\n"
        f"🏷️ Inventory Code: {config['inventory_code']}\n"
        f"📅 Date: {year:04d}-{month:02d}-{day:02d}\n\n"
        f"Template file:\n{template_files_str}\n\n"
        f"{files_message}"
    )
    if error_msg:
        msg += f"\n\n{error_msg}"
    return msg