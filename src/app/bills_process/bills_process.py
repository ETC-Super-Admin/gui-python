from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QDateEdit, QGroupBox, QTextEdit, QSizePolicy, QToolButton
from PySide6.QtGui import QIcon
from PySide6.QtCore import QDate, Qt, QThreadPool
import qtawesome as qta
import os


from src.components.async_worker import Worker
from .core.orchestrator import Orchestrator
from .core.cache_manager import CacheManager
from .core.file_opener import FileOpener
from .core.file_unmerger import FileUnmerger
from .core.row_rearranger import RowRearranger
from .core.formula_updater import FormulaUpdater

class BillsProcess(QWidget):
    def __init__(self):
        super().__init__()
        self.threadpool = QThreadPool()
        self.setup_ui()
        self.connect_signals()
        self.log_display.setPlainText("Select a date and click an action to begin.")

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # --- Left side (Log Display) ---
        left_widget = QGroupBox("Processing Log")
        left_widget.setObjectName("Card")
        left_layout = QVBoxLayout(left_widget)
        
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setLineWrapMode(QTextEdit.NoWrap)
        self.log_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_layout.addWidget(self.log_display)

        # --- Right side (Controls) ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)

        # Actions Group
        actions_group = QGroupBox("Actions")
        actions_group.setObjectName("Card")
        actions_layout = QVBoxLayout(actions_group)
        actions_layout.setSpacing(10)

        actions_layout.addWidget(QLabel("Select Date:"))
        self.date_select = QDateEdit(QDate.currentDate())
        self.date_select.setCalendarPopup(True)
        self.date_select.setFixedHeight(35)

        actions_layout.addWidget(self.date_select)
        actions_layout.addSpacing(15)

        self.process_button = self.create_action_button(
            "Process Files", 'fa5s.cogs', "SuccessButton"
        )
        self.unmerge_button = self.create_action_button(
            "Unmerge Daily Files", 'fa5s.th-large', "SuccessOutlineButton", icon_color='#22c55e'
        )
        self.rearrange_button = self.create_action_button(
            "Rearrange Rows", 'fa5s.sort-amount-down', "WarningButton"
        )
        self.update_formulas_button = self.create_action_button(
            "Update Formulas", 'fa5s.calculator', "SuccessOutlineButton", icon_color='#22c55e'
        )
        self.open_report_button = self.create_action_button(
            "Open Monthly Report", 'fa5s.folder-open'
        )

        actions_layout.addWidget(self.unmerge_button)
        actions_layout.addWidget(self.process_button)
        actions_layout.addWidget(self.update_formulas_button)
        actions_layout.addSpacing(20)
        actions_layout.addWidget(self.rearrange_button)
        actions_layout.addWidget(self.open_report_button)
        actions_layout.addStretch()
        
        right_layout.addWidget(actions_group)
        right_layout.addStretch(1)

        # Danger Zone Group
        danger_group = QGroupBox("Danger Zone")
        danger_group.setObjectName("Card")
        danger_layout = QVBoxLayout(danger_group)
        
        self.clear_unmerge_cache_button = self.create_action_button(
            "Clear Unmerge Cache", 'fa5s.trash-alt', "DeleteUserButton"
        )
        danger_layout.addWidget(self.clear_unmerge_cache_button)
        
        right_layout.addWidget(danger_group)

        right_widget.setMinimumWidth(280)
        right_widget.setMaximumWidth(320)
        
        # Add main widgets to layout
        main_layout.addWidget(left_widget, 7)
        main_layout.addWidget(right_widget, 3)

    def create_action_button(self, text, icon_name, object_name=None, icon_color='white'):
        button = QPushButton(qta.icon(icon_name, color=icon_color), f" {text}")
        if object_name:
            button.setObjectName(object_name)
        return button

    def connect_signals(self):
        self.process_button.clicked.connect(self.on_process_files)
        self.unmerge_button.clicked.connect(self.on_unmerge_files)
        self.rearrange_button.clicked.connect(self.on_rearrange_rows)
        self.update_formulas_button.clicked.connect(self.on_update_formulas)
        self.open_report_button.clicked.connect(self.on_open_report)
        self.clear_unmerge_cache_button.clicked.connect(self.on_clear_unmerge_cache)
        self.date_select.dateChanged.connect(self.on_date_changed)

    def on_process_files(self):
        self.log_display.clear()
        self.log_display.setPlainText("⏳ Starting file processing...\nThis may take a moment.")
        self.process_button.setEnabled(False)
        self.process_button.setText("Processing...")

        date = self.date_select.date()
        
        def task(**kwargs):
            orchestrator = Orchestrator(date)
            return orchestrator.run_process_files()

        worker = Worker(task)
        worker.signals.result.connect(self._on_processing_complete)
        worker.signals.error.connect(self._on_processing_error)
        self.threadpool.start(worker)

    def _on_processing_complete(self, result):
        self.log_display.append(f"\n--- Result ---\n{result.message}")
        self.process_button.setEnabled(True)
        self.process_button.setText(" Process Files")

    def _on_processing_error(self, error_tuple):
        exctype, value, traceback_str = error_tuple
        self.log_display.append(f"\n--- CRITICAL ERROR ---\n{value}\n\n{traceback_str}")
        # Reset all buttons that could have been disabled
        self.process_button.setEnabled(True)
        self.process_button.setText(" Process Files")
        self.unmerge_button.setEnabled(True)
        self.unmerge_button.setText(" Unmerge Daily Files")
        self.rearrange_button.setEnabled(True)
        self.rearrange_button.setText(" Rearrange Rows")
        self.update_formulas_button.setEnabled(True)
        self.update_formulas_button.setText(" Update Formulas")
        self.open_report_button.setEnabled(True)
        self.open_report_button.setText(" Open Monthly Report")
        self.clear_unmerge_cache_button.setEnabled(True)
        self.clear_unmerge_cache_button.setText(" Clear Unmerge Cache")

    def on_unmerge_files(self):
        self.log_display.clear()
        self.log_display.setPlainText("⏳ Starting file unmerge...")
        self.unmerge_button.setEnabled(False)
        self.unmerge_button.setText("Unmerging...")

        date = self.date_select.date()
        year, month, day = date.year(), date.month(), date.day()
        
        def task(**kwargs):
            file_unmerger = FileUnmerger()
            return file_unmerger.unmerge_daily_bills_files(year, month, day, **kwargs)

        worker = Worker(task)
        worker.signals.result.connect(self._on_unmerge_files_complete)
        worker.signals.error.connect(self._on_processing_error)
        worker.signals.progress.connect(self._on_unmerge_progress)
        self.threadpool.start(worker)

    def _on_unmerge_progress(self, message):
        self.log_display.append(message)

    def _on_unmerge_files_complete(self, result):
        self.log_display.append(f"\n--- Unmerge Result ---\n{result.message}")
        self.unmerge_button.setEnabled(True)
        self.unmerge_button.setText(" Unmerge Daily Files")

    def on_rearrange_rows(self):
        self.log_display.clear()
        self.log_display.setPlainText("⏳ Starting row rearrangement...")
        self.rearrange_button.setEnabled(False)
        self.rearrange_button.setText("Rearranging...")

        date = self.date_select.date()
        year, month, day = date.year(), date.month(), date.day()
        
        def task(**kwargs):
            row_rearranger = RowRearranger()
            return row_rearranger.rearrange_template_rows(year, month, day)

        worker = Worker(task)
        worker.signals.result.connect(self._on_rearrange_rows_complete)
        worker.signals.error.connect(self._on_processing_error)
        self.threadpool.start(worker)

    def _on_rearrange_rows_complete(self, result):
        self.log_display.append(f"\n--- Rearrange Rows Result ---\n{result.message}")
        self.rearrange_button.setEnabled(True)
        self.rearrange_button.setText(" Rearrange Rows")

    def on_update_formulas(self):
        self.log_display.clear()
        self.log_display.setPlainText("⏳ Starting formula update...")
        self.update_formulas_button.setEnabled(False)
        self.update_formulas_button.setText("Updating...")

        date = self.date_select.date()
        year, month, day = date.year(), date.month(), date.day()
        
        def task(**kwargs):
            formula_updater = FormulaUpdater()
            return formula_updater.update_formulas(year, month, day)

        worker = Worker(task)
        worker.signals.result.connect(self._on_update_formulas_complete)
        worker.signals.error.connect(self._on_processing_error)
        self.threadpool.start(worker)

    def _on_update_formulas_complete(self, result):
        self.log_display.append(f"\n--- Update Formulas Result ---\n{result.message}")
        self.update_formulas_button.setEnabled(True)
        self.update_formulas_button.setText(" Update Formulas")

    def on_open_report(self):
        self.log_display.clear()
        self.log_display.setPlainText("⏳ Opening monthly report...")
        self.open_report_button.setEnabled(False)
        self.open_report_button.setText("Opening...")

        date = self.date_select.date()
        year, month = date.year(), date.month()

        def task(**kwargs):
            file_opener = FileOpener()
            return file_opener.open_monthly_report_file(year, month)

        worker = Worker(task)
        worker.signals.result.connect(self._on_open_report_complete)
        worker.signals.error.connect(self._on_processing_error)
        self.threadpool.start(worker)

    def _on_open_report_complete(self, result):
        self.log_display.append(f"\n--- Open Report Result ---\n{result.message}")
        self.open_report_button.setEnabled(True)
        self.open_report_button.setText(" Open Monthly Report")

    def on_clear_unmerge_cache(self):
        from PySide6.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            self,
            "Confirm Clear Unmerge Cache",
            "Are you sure you want to clear the unmerge history for this date?\nThis will allow all files for the day to be unmerged again.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.No:
            self.log_display.append("\nCache clearing cancelled.")
            return

        self.log_display.clear()
        self.log_display.setPlainText("⏳ Clearing unmerge cache...")
        self.clear_unmerge_cache_button.setEnabled(False)
        self.clear_unmerge_cache_button.setText("Clearing...")

        date = self.date_select.date()
        year, month, day = date.year(), date.month(), date.day()
        
        def task(**kwargs):
            file_unmerger = FileUnmerger()
            return file_unmerger.clear_unmerged_cache(year, month, day)

        worker = Worker(task)
        worker.signals.result.connect(self._on_clear_unmerge_cache_complete)
        worker.signals.error.connect(self._on_processing_error)
        self.threadpool.start(worker)

    def _on_clear_unmerge_cache_complete(self, result):
        self.log_display.append(f"\n--- Unmerge Cache Clear Result ---\n{result.message}")
        self.clear_unmerge_cache_button.setEnabled(True)
        self.clear_unmerge_cache_button.setText(" Clear Unmerge Cache")

    def on_date_changed(self):
        self.log_display.clear()
        self.log_display.setPlainText(f"Date changed to: {self.date_select.date().toString(Qt.ISODate)}")
