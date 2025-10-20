# src/components/tabs/bills_process_tab/components/__init__.py
"""
Components for the bills processing tab.

This package contains components that handle different aspects of bills processing:

Original components:
- ui_setup: UI setup functionality
- date_handler: Date handling utilities
- bills_processor: Main bills processing logic
- file_unmerger: File unmerging functionality
- file_opener: File opening utilities

Refactored template processing components:
- result: Result class for operation outcomes
- config_manager: Template configuration management
- file_scanner: File scanning and discovery
- data_collector: Data extraction from Excel files
- excel_processor: Excel template processing and data insertion
- template_file_processor: Main orchestration function
"""

# Original components
from .ui_setup import setup_ui
from .date_handler import DateHandler
from .bills_processor import BillsProcessor
from .file_unmerger import FileUnmerger
from .file_opener import FileOpener
from .cache_manager import CacheManager

# Refactored template processing components
from .result import Result
from .config_manager import TemplateConfigManager
from .file_scanner import FileScanner
from .data_collector import DataCollector
from .excel_processor import ExcelProcessor
from .template_file_processor import process_template_file
from .row_rearranger import rearrange_template_rows

__all__ = [
    # Original components
    'setup_ui',
    'DateHandler',
    'BillsProcessor',
    'FileUnmerger',
    'FileOpener',
    'CacheManager',
    # Refactored template processing components
    'Result',
    'TemplateConfigManager',
    'FileScanner', 
    'DataCollector',
    'ExcelProcessor',
    'process_template_file',
    'rearrange_template_rows'
]