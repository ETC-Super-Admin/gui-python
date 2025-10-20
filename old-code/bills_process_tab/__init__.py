from PyQt5.QtWidgets import QWidget
from src.components.settings.bills.models import BillsConfigManager
from src.components.common.custom_messagebox import CustomMessageBox, MessageType
import os

from src.components.tabs.bills_process_tab.components.update_formula import update_formula
from src.components.tabs.bills_process_tab.components import (
    setup_ui,
    DateHandler,
    BillsProcessor,
    FileUnmerger,
    FileOpener,
    CacheManager,
    process_template_file,
    rearrange_template_rows
)

class BillsProcessTab(QWidget):
    def __init__(self):
        super().__init__()
        
        # Initialize configuration paths
        self._init_config_paths()
        
        # Setup UI
        setup_ui(self)
        
        # Initialize handlers
        self._init_handlers()
        
        # Connect signals
        self._connect_signals()

        # Initial processing
        self.process_bills(show_popup=False)
    
    def _init_config_paths(self):
        """Initialize configuration file paths."""
        self.app_dir = BillsConfigManager().app_dir
        self.file1_path = os.path.join(self.app_dir, "template_path_settings.json")
        self.file2_path = os.path.join(self.app_dir, "bills_settings_config.json")
    
    def _init_handlers(self):
        """Initialize handler classes."""
        self.date_handler = DateHandler(self.date_input)
        self.bills_processor = BillsProcessor(self, self.app_dir, self.file1_path, self.file2_path)
        self.file_unmerger = FileUnmerger(self, self.file1_path)
        self.file_opener = FileOpener(self, self.file1_path)
        self.cache_manager = CacheManager(self, self.app_dir, self.file1_path)
    
    def _connect_signals(self):
        """Connect button signals to their respective handlers."""
        self.unmerge_btn.clicked.connect(self.unmerge_daily_bills_files)
        self.open_file_btn.clicked.connect(self.open_monthly_report_file)
        self.clear_cache_btn.clicked.connect(self.clear_process_cache_handler)
        self.rearrange_btn.clicked.connect(self.rearrange_template_rows_handler)
        self.process_template_btn.clicked.connect(self.process_template_file_handler)
        self.update_formula_btn.clicked.connect(self.update_formula_handler)  # <-- connect new button
    
    def get_selected_date(self):
        """Return the currently selected date as QDate."""
        return self.date_handler.get_selected_date()
    
    def process_bills(self, show_popup=True):
        """Process bills and display results in the log area."""
        year, month, day = self.date_handler.get_date_components()
        
        message_text, message_type_str = self.bills_processor.process_bills(year, month, day, show_popup=show_popup)
        
        # Apply appropriate style based on the result type
        style_type = self._get_message_type(message_type_str)
        self.log_display.setStyleSheet(CustomMessageBox.get_text_display_style(style_type))
        self.log_display.setPlainText(message_text)
    
    def unmerge_daily_bills_files(self):
        """Unmerge cells in all daily bills .xlsx files."""
        year, month, day = self.date_handler.get_date_components()
        
        result_message, message_type = self.file_unmerger.unmerge_daily_bills_files(year, month, day)
        
        # Apply appropriate style
        style_type = self._get_message_type(message_type)
        self.log_display.setStyleSheet(CustomMessageBox.get_text_display_style(style_type))
        self.log_display.setPlainText(result_message)
    
    def open_monthly_report_file(self):
        """Open the monthly report .xlsx file for the selected year/month."""
        year, month, _ = self.date_handler.get_date_components()
        
        result_message, message_type = self.file_opener.open_monthly_report_file(year, month)
        
        # Apply appropriate style
        style_type = self._get_message_type(message_type)
        self.log_display.setStyleSheet(CustomMessageBox.get_text_display_style(style_type))
        self.log_display.setPlainText(result_message)
    
    def process_template_file_handler(self):
        """Process template file and display result."""
        year, month, day = self.date_handler.get_date_components()
        message_text, message_type_str = process_template_file(year, month, day, parent=self)
        style_type = self._get_message_type(message_type_str)
        self.log_display.setStyleSheet(CustomMessageBox.get_text_display_style(style_type))
        self.log_display.setPlainText(message_text)
    
    def rearrange_template_rows_handler(self):
        """Rearrange rows in the template file by province/zone (column E)."""
        year, month, day = self.date_handler.get_date_components()
        message_text, message_type_str = rearrange_template_rows(year, month, day, self.file1_path, parent=self)
        style_type = self._get_message_type(message_type_str)
        self.log_display.setStyleSheet(CustomMessageBox.get_text_display_style(style_type))
        self.log_display.setPlainText(message_text)
    
    def clear_process_cache_handler(self):
        """Clear the processing state cache for the selected date."""
        year, month, day = self.date_handler.get_date_components()
        message_text, message_type_str = self.cache_manager.clear_process_cache(year, month, day)
        style_type = self._get_message_type(message_type_str)
        self.log_display.setStyleSheet(CustomMessageBox.get_text_display_style(style_type))
        self.log_display.setPlainText(message_text)
    
    def update_formula_handler(self):
        """Handle Update Formula button click."""
        year, month, day = self.date_handler.get_date_components()
        message_text, message_type_str = update_formula(year, month, day, parent=self)
        style_type = self._get_message_type(message_type_str)
        self.log_display.setStyleSheet(CustomMessageBox.get_text_display_style(style_type))
        self.log_display.setPlainText(message_text)
    
    def _get_message_type(self, message_type_str):
        """Convert string message type to MessageType enum."""
        type_mapping = {
            "success": MessageType.SUCCESS,
            "error": MessageType.ERROR,
            "warning": MessageType.WARNING,
            "info": MessageType.INFO
        }
        return type_mapping.get(message_type_str, MessageType.INFO)