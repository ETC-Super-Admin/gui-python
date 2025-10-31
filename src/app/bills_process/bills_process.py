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
        left_widget = QGroupBox("บันทึกการประมวลผล")
        left_widget.setObjectName("Card")
        left_layout = QVBoxLayout(left_widget)
        
        self.log_display = QTextEdit()
        self.log_display.setObjectName("LogDisplay")
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
        actions_group = QGroupBox("การดำเนินการ")
        actions_group.setObjectName("Card")
        actions_layout = QVBoxLayout(actions_group)
        actions_layout.setSpacing(10)

        actions_layout.addWidget(QLabel("เลือกวันที่:"))
        self.date_select = QDateEdit(QDate.currentDate())
        self.date_select.setCalendarPopup(True)
        self.date_select.setFixedHeight(35)

        actions_layout.addWidget(self.date_select)
        actions_layout.addSpacing(15)

        self.process_button = self.create_action_button(
            "ประมวลผลไฟล์", 'fa5s.cogs', "SuccessButton"
        )
        self.rearrange_button = self.create_action_button(
            "จัดเรียงแถวใหม่", 'fa5s.sort-amount-down', "WarningButton"
        )
        self.update_formulas_button = self.create_action_button(
            "อัปเดตสูตร", 'fa5s.calculator', "SuccessOutlineButton", icon_color='#22c55e'
        )
        self.open_report_button = self.create_action_button(
            "เปิดรายงานประจำเดือน", 'fa5s.folder-open'
        )

        actions_layout.addWidget(self.process_button)
        actions_layout.addWidget(self.update_formulas_button)
        actions_layout.addSpacing(20)
        actions_layout.addWidget(self.rearrange_button)
        actions_layout.addWidget(self.open_report_button)
        actions_layout.addStretch()
        
        right_layout.addWidget(actions_group)
        right_layout.addStretch(1)

        # Danger Zone Group
        danger_group = QGroupBox("โซนอันตราย")
        danger_group.setObjectName("Card")
        danger_layout = QVBoxLayout(danger_group)
        
        self.clear_process_state_button = self.create_action_button(
            "ล้างสถานะการประมวลผล", 'fa5s.trash-alt', "DangerOutlineButton", icon_color='#ef4444'
        )
        danger_layout.addWidget(self.clear_process_state_button)
        
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
        self.rearrange_button.clicked.connect(self.on_rearrange_rows)
        self.update_formulas_button.clicked.connect(self.on_update_formulas)
        self.open_report_button.clicked.connect(self.on_open_report)
        self.clear_process_state_button.clicked.connect(self.on_clear_process_state)
        self.date_select.dateChanged.connect(self.on_date_changed)

    def on_process_files(self):
        self.log_display.clear()
        self.log_display.setPlainText("⏳ กำลังเริ่มต้นประมวลผลไฟล์...\nอาจใช้เวลาสักครู่")
        self.process_button.setEnabled(False)
        self.process_button.setText("กำลังประมวลผล...")

        date = self.date_select.date()
        
        def task(**kwargs):
            orchestrator = Orchestrator(date)
            return orchestrator.run_process_files(**kwargs)

        worker = Worker(task)
        worker.signals.result.connect(self._on_processing_complete)
        worker.signals.error.connect(self._on_processing_error)
        worker.signals.progress.connect(self._on_process_progress)
        self.threadpool.start(worker)

    def _on_process_progress(self, message):
        self.log_display.append(message)

    def _on_processing_complete(self, result):
        self.log_display.append(f"\n--- ผลลัพธ์ ---\n{result.message}")
        self.process_button.setEnabled(True)
        self.process_button.setText(" ประมวลผลไฟล์")

    def _on_processing_error(self, error_tuple):
        exctype, value, traceback_str = error_tuple
        self.log_display.append(f"\n--- ข้อผิดพลาดร้ายแรง ---\n{value}\n\n{traceback_str}")
        # Reset all buttons that could have been disabled
        self.process_button.setEnabled(True)
        self.process_button.setText(" ประมวลผลไฟล์")
        self.rearrange_button.setEnabled(True)
        self.rearrange_button.setText(" จัดเรียงแถวใหม่")
        self.update_formulas_button.setEnabled(True)
        self.update_formulas_button.setText(" อัปเดตสูตร")
        self.open_report_button.setEnabled(True)
        self.open_report_button.setText(" เปิดรายงานประจำเดือน")
        self.clear_process_state_button.setEnabled(True)
        self.clear_process_state_button.setText(" ล้างสถานะการประมวลผล")

    def on_rearrange_rows(self):
        self.log_display.clear()
        self.log_display.setPlainText("⏳ กำลังจัดเรียงแถวใหม่...")
        self.rearrange_button.setEnabled(False)
        self.rearrange_button.setText("กำลังจัดเรียง...")

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
        self.log_display.append(f"\n--- ผลลัพธ์การจัดเรียงแถว ---\n{result.message}")
        self.rearrange_button.setEnabled(True)
        self.rearrange_button.setText(" จัดเรียงแถวใหม่")

    def on_update_formulas(self):
        self.log_display.clear()
        self.log_display.setPlainText("⏳ กำลังอัปเดตสูตร...")
        self.update_formulas_button.setEnabled(False)
        self.update_formulas_button.setText("กำลังอัปเดต...")

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
        self.log_display.append(f"\n--- ผลลัพธ์การอัปเดตสูตร ---\n{result.message}")
        self.update_formulas_button.setEnabled(True)
        self.update_formulas_button.setText(" อัปเดตสูตร")

    def on_open_report(self):
        self.log_display.clear()
        self.log_display.setPlainText("⏳ กำลังเปิดรายงานประจำเดือน...")
        self.open_report_button.setEnabled(False)
        self.open_report_button.setText("กำลังเปิด...")

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
        self.log_display.append(f"\n--- ผลลัพธ์การเปิดรายงาน ---\n{result.message}")
        self.open_report_button.setEnabled(True)
        self.open_report_button.setText(" เปิดรายงานประจำเดือน")

    def on_clear_process_state(self):
        from PySide6.QtWidgets import QMessageBox

        msg_box = QMessageBox(QMessageBox.Warning,
            "ยืนยันการล้างสถานะการประมวลผล",
            "คุณแน่ใจหรือไม่ว่าต้องการล้างสถานะการประมวลผลสำหรับวันนี้?\nการดำเนินการนี้จะทำให้สามารถประมวลผลไฟล์ทั้งหมดสำหรับวันนี้ได้อีกครั้งตั้งแต่ต้น",
            QMessageBox.Yes | QMessageBox.No,
            self
        )
        msg_box.setDefaultButton(QMessageBox.No)
        
        yes_button = msg_box.button(QMessageBox.Yes)
        if yes_button:
            yes_button.setObjectName("DangerDialogButton")

        reply = msg_box.exec()

        if reply == QMessageBox.No:
            self.log_display.append("\nยกเลิกการล้างสถานะการประมวลผลแล้ว.")
            return

        self.log_display.clear()
        self.log_display.setPlainText("⏳ กำลังล้างสถานะการประมวลผล...")
        self.clear_process_state_button.setEnabled(False)
        self.clear_process_state_button.setText("กำลังล้าง...")

        date = self.date_select.date()
        year, month, day = date.year(), date.month(), date.day()
        
        def task(**kwargs):
            cache_manager = CacheManager()
            return cache_manager.clear_process_cache(year, month, day)

        worker = Worker(task)
        worker.signals.result.connect(self._on_clear_process_state_complete)
        worker.signals.error.connect(self._on_processing_error)
        self.threadpool.start(worker)

    def _on_clear_process_state_complete(self, result):
        self.log_display.append(f"\n--- ผลลัพธ์การล้างสถานะการประมวลผล ---\n{result.message}")
        self.clear_process_state_button.setEnabled(True)
        self.clear_process_state_button.setText(" ล้างสถานะการประมวลผล")

    def on_date_changed(self):
        self.log_display.clear()
        self.log_display.setPlainText(f"วันที่เปลี่ยนเป็น: {self.date_select.date().toString(Qt.ISODate)}")
