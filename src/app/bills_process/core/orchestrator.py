from .config_manager import ConfigManager
from .file_scanner import FileScanner
from .data_collector import DataCollector
from .excel_processor import ExcelProcessor
from .result import Result

class Orchestrator:
    """
    Orchestrates the entire bills processing workflow.
    """
    def __init__(self, date):
        self.date = date
        self.year = date.year()
        self.month = date.month()
        self.day = date.day()

    def run_process_files(self) -> Result:
        """
        Executes the main 'Process Files' workflow.
        """
        try:
            # 1. Load Config
            config_manager = ConfigManager()
            config_result = config_manager.load_config()
            if not config_result.success:
                return config_result
            config = config_result.data
            
            # 2. Scan for files
            file_scanner = FileScanner(config['base_path'])
            scan_result = file_scanner.scan_files(self.year, self.month, self.day)
            if not scan_result.success:
                return scan_result
            
            files_data = scan_result.data
            template_path = files_data['template_file_path']
            daily_files = files_data['daily_files']
            target_dir = files_data['target_dir']

            if not daily_files:
                return Result.info("No new daily files to process.")

            # 3. Collect data
            data_collector = DataCollector()
            collection_result = data_collector.collect_from_files(daily_files, target_dir)
            if not collection_result.success:
                return collection_result
            collected_data = collection_result.data

            # 4. Process Excel
            excel_processor = ExcelProcessor(
                template_path=template_path,
                data=collected_data,
                date=self.date,
                inventory_code=config['inventory_code'],
                target_dir=target_dir,
                daily_files=daily_files
            )
            process_result = excel_processor.process()

            return process_result
        except Exception as e:
            return Result.error(f"An unexpected error occurred in the orchestrator: {e}")
