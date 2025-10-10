from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QPainter, QFont, QColor, QPixmap
from PySide6.QtCore import QRectF, Qt
from PySide6.QtPrintSupport import QPrinter, QPrintDialog, QPageSetupDialog

from src.db.config_queries import get_config


def page_setup(parent_widget, printer):
    """Opens a page setup dialog to configure the given printer object."""
    dialog = QPageSetupDialog(printer, parent_widget)
    dialog.exec()

def direct_print(parent_widget, label_preview_widget, printer):
    """Opens a print dialog and prints the label content as vector graphics."""
    if not label_preview_widget.receiver_name_label.text() or "Select a receiver" in label_preview_widget.receiver_name_label.text():
        QMessageBox.warning(parent_widget, "Missing Data", "Please select a receiver before printing.")
        return

    dialog = QPrintDialog(printer, parent_widget)
    dialog.setWindowTitle("Print Shipping Label")
    if dialog.exec() != QPrintDialog.Accepted:
        return

    # --- Extract data from the preview widget ---
    label_data = {
        "sender_address": label_preview_widget.sender_address_label.text(),
        "sender_tel": label_preview_widget.sender_tel_label.text(),
        "sender_logo_path": get_config("asset_sender_logo", ""),
        "receiver_name": label_preview_widget.receiver_name_label.text(),
        "receiver_address": label_preview_widget.receiver_address_label.text(),
        "receiver_tel": label_preview_widget.receiver_tel_label.text(),
        "receiver_logo_path": get_config("asset_receiver_logo", ""),
        "copy_text": label_preview_widget.copy_count_label.text()
    }

    # --- Start painting ---
    painter = QPainter(printer)
    # Use Point as unit for predictable font and coordinate scaling
    page_rect = printer.pageRect(QPrinter.Unit.Point)
    draw_label_with_qpainter(painter, page_rect, label_data)
    painter.end()
    QMessageBox.information(parent_widget, "Success", "Label sent to printer.")


def draw_label_with_qpainter(painter, page_rect, data):
    """Draws the entire label using QPainter methods for high-quality output."""
    
    # --- Define Layout & Style Constants ---
    margin = 40  # in points
    content_rect = page_rect.adjusted(margin, margin, -margin, -margin)
    
    sender_col_width = content_rect.width() * 0.4
    receiver_col_width = content_rect.width() * 0.6
    separator_x = content_rect.left() + sender_col_width + 20

    # --- Define Fonts & Colors ---
    title_font = QFont("Sarabun-Bold", 10.5)
    address_font = QFont("Sarabun-Regular", 10.5)
    tel_font = QFont("Sarabun-Bold", 10.5)
    receiver_name_font = QFont("Sarabun-Bold", 12)

    title_color = QColor("#64748b")
    text_color = QColor("#334155")
    receiver_name_color = QColor("#000000")
    line_color = QColor("#e2e8f0")

    # --- Draw Separator Line ---
    painter.setPen(line_color)
    painter.drawLine(int(separator_x), content_rect.top(), int(separator_x), content_rect.bottom())

    # --- Sender Column (Left) ---
    current_y = content_rect.top()
    sender_content_rect = QRectF(content_rect.left(), current_y, sender_col_width, content_rect.height())

    # Sender Logo
    if data["sender_logo_path"]:
        pixmap = QPixmap(data["sender_logo_path"])
        if not pixmap.isNull():
            target_h = 60
            target_w = target_h * (16/9)
            target_rect = QRectF(0, 0, target_w, target_h)
            # Center it in the column
            target_rect.moveCenter(sender_content_rect.center())
            target_rect.moveTop(current_y)
            painter.drawPixmap(target_rect.toRect(), pixmap)
        current_y += 60 + 15

    # "FROM" Title
    painter.setFont(title_font)
    painter.setPen(title_color)
    painter.drawText(QRectF(sender_content_rect.left(), current_y, sender_content_rect.width(), 20), "FROM")
    current_y += 15
    painter.setPen(line_color)
    painter.drawLine(sender_content_rect.left(), current_y, sender_content_rect.right() - 20, current_y)
    current_y += 15

    # Sender Address & Tel
    painter.setFont(address_font)
    painter.setPen(text_color)
    address_rect = QRectF(sender_content_rect.left(), current_y, sender_content_rect.width(), content_rect.height() - current_y)
    full_sender_text = f'{data["sender_address"]}\n<b>{data["sender_tel"]}</b>'
    painter.drawText(address_rect, Qt.TextWordWrap, full_sender_text)

    # Copy Count
    painter.setFont(title_font)
    painter.setPen(title_color)
    painter.drawText(QRectF(sender_content_rect.left(), content_rect.bottom() - 20, 100, 20), data["copy_text"])

    # --- Receiver Column (Right) ---
    current_y = content_rect.top()
    receiver_content_rect = QRectF(separator_x + 20, current_y, receiver_col_width - 20, content_rect.height())

    # Receiver Logo
    if data["receiver_logo_path"]:
        pixmap = QPixmap(data["receiver_logo_path"])
        if not pixmap.isNull():
            target_h = 80
            target_w = target_h * (16/9)
            target_rect = QRectF(0, 0, target_w, target_h)
            target_rect.moveCenter(receiver_content_rect.center())
            target_rect.moveTop(current_y)
            painter.drawPixmap(target_rect.toRect(), pixmap)
        current_y += 80 + 15

    # "TO" Title
    painter.setFont(title_font)
    painter.setPen(title_color)
    painter.drawText(QRectF(receiver_content_rect.left(), current_y, receiver_content_rect.width(), 20), "TO")
    current_y += 15
    painter.setPen(line_color)
    painter.drawLine(receiver_content_rect.left(), current_y, receiver_content_rect.right(), current_y)
    current_y += 15

    # Receiver Name
    painter.setFont(receiver_name_font)
    painter.setPen(receiver_name_color)
    # Use bounding rect to measure height after drawing
    name_rect = painter.drawText(QRectF(receiver_content_rect.left(), current_y, receiver_content_rect.width(), 50), Qt.TextWordWrap, data["receiver_name"])
    current_y += name_rect.height() + 5

    # Receiver Address & Tel
    painter.setFont(address_font)
    painter.setPen(text_color)
    address_rect = QRectF(receiver_content_rect.left(), current_y, receiver_content_rect.width(), content_rect.height() - current_y)
    full_receiver_text = f'{data["receiver_address"]}\n<b>{data["receiver_tel"]}</b>'
    painter.drawText(address_rect, Qt.TextWordWrap, full_receiver_text)