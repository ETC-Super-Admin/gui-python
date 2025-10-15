from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QPainter, QFont, QPixmap, QColor, QPageSize, QTextDocument
from PySide6.QtCore import Qt, QRectF, QSizeF, QPointF
import os

from src.db.config_queries import get_config

# --- Font Setup ---
FONT_FAMILY = "Tahoma"
FONT_FALLBACK = "Arial"

def _get_font(point_size, bold=False):
    """Helper to create a QFont object with fallback."""
    font = QFont(FONT_FAMILY, point_size)
    if bold:
        font.setBold(True)
    if font.family() != FONT_FAMILY:
        font.setFamily(FONT_FALLBACK)
    return font

def page_setup(parent, printer):
    """Opens the printer configuration dialog."""
    printer.setPageSize(QPrinter.PageSize.A6)
    printer.setPageMargins(0, 0, 0, 0, QPrinter.Unit.Millimeter)
    dialog = QPrintDialog(printer, parent)
    if dialog.exec() == QPrintDialog.Accepted:
        pass

def direct_print(parent, label_preview_widget, printer, copies=1):
    """Renders the label content directly to the printer using QPainter."""
    if not label_preview_widget.receiver_name_label.text() or label_preview_widget.receiver_name_label.text() == "N/A":
        QMessageBox.warning(parent, "Missing Data", "Please select a receiver before printing.")
        return

    dialog = QPrintDialog(printer, parent)
    if dialog.exec() == QPrintDialog.Accepted:
        # Set the custom page size BEFORE beginning the painter
        PAGE_WIDTH_MM = 150
        PAGE_HEIGHT_MM = 100
        custom_page_size = QPageSize(QSizeF(PAGE_WIDTH_MM, PAGE_HEIGHT_MM), QPageSize.Unit.Millimeter, "CustomLabel", QPageSize.ExactMatch)
        printer.setPageSize(custom_page_size)

        try:
            painter = QPainter()
            if not painter.begin(printer):
                raise RuntimeError("Failed to open printer for painting.")

            for i in range(copies):
                if i > 0:
                    printer.newPage()
                copy_text = f"{i + 1}/{copies}"
                _draw_label_on_painter(painter, printer, label_preview_widget, copy_text)

            painter.end()
            QMessageBox.information(parent, "Success", f"Sent {copies} page(s) to the printer.")
        except Exception as e:
            QMessageBox.critical(parent, "Printing Error", f"An error occurred while printing: {e}")

def _draw_label_on_painter(painter, printer, widget, copy_text):
    """Draws the entire label layout onto the provided QPainter object."""
    MARGIN_MM = 5
    
    page_rect_px = printer.pageRect(QPrinter.Unit.DevicePixel)
    
    dpi = printer.resolution()
    def mm_to_px(mm): return (mm / 25.4) * dpi

    margin_px = mm_to_px(MARGIN_MM)
    content_rect = QRectF(page_rect_px.x() + margin_px, page_rect_px.y() + margin_px, page_rect_px.width() - 2 * margin_px, page_rect_px.height() - 2 * margin_px)

    sender_col_width = content_rect.width() * 0.4
    receiver_col_width = content_rect.width() * 0.6
    separator_x = content_rect.x() + sender_col_width + mm_to_px(2)

    sender_address = widget.sender_address_label.text()
    sender_tel = widget.sender_tel_label.text()
    receiver_name = widget.receiver_name_label.text()
    receiver_address = widget.receiver_address_label.text()
    receiver_tel = widget.receiver_tel_label.text()
    receiver_delivery_by = widget.receiver_delivery_by_label.text() if hasattr(widget, 'receiver_delivery_by_label') else ""
    receiver_note = widget.receiver_note_label.text() if hasattr(widget, 'receiver_note_label') else ""
    sender_pixmap = widget.sender_asset_label.pixmap()
    receiver_pixmap = widget.receiver_asset_label.pixmap()

    painter.setRenderHint(QPainter.Antialiasing)

    # --- Helper for drawing plain text ---
    def draw_plain_text(p, y_pos, rect, text, font, color, flags, spacing_after_mm):
        p.setFont(font)
        p.setPen(color)
        draw_rect = QRectF(rect.x(), y_pos, rect.width(), rect.height() - (y_pos - rect.y()))
        bounding_rect = p.drawText(draw_rect, flags, text)
        return y_pos + bounding_rect.height() + mm_to_px(spacing_after_mm)

    # --- 1. Draw Sender Column (Left) ---
    sender_rect = QRectF(content_rect.x(), content_rect.y(), sender_col_width, content_rect.height())
    current_y = sender_rect.y()

    if sender_pixmap and not sender_pixmap.isNull():
        logo_height = int(mm_to_px(15))
        scaled_pixmap = sender_pixmap.scaledToHeight(logo_height, Qt.SmoothTransformation)
        logo_x = sender_rect.x() + (sender_rect.width() - scaled_pixmap.width()) / 2
        painter.drawPixmap(int(logo_x), int(current_y), scaled_pixmap)
        current_y += scaled_pixmap.height() + mm_to_px(2.5)

    current_y = draw_plain_text(painter, current_y, sender_rect, "ผู้ส่ง", _get_font(10.5, bold=True), QColor("#64748b"), Qt.AlignLeft, 0)
    
    painter.setPen(QColor("#e2e8f0"))
    painter.drawLine(QPointF(sender_rect.x(), current_y + mm_to_px(1)), QPointF(sender_rect.right(), current_y + mm_to_px(1)))
    current_y += mm_to_px(3.5)

    # Use QTextDocument for rich text (address)
    doc = QTextDocument()
    doc.setDefaultFont(_get_font(10.5))
    doc.setHtml(f'<span style="color: #334155;">{sender_address}</span>')
    doc.setTextWidth(sender_rect.width())
    doc.drawContents(painter, QRectF(QPointF(sender_rect.x(), current_y), doc.size()))
    current_y += doc.size().height() + mm_to_px(2.5)

    current_y = draw_plain_text(painter, current_y, sender_rect, sender_tel, _get_font(10.5, bold=True), QColor("#334155"), Qt.TextWordWrap, 0)

    # --- 2. Draw Receiver Column (Right) ---
    receiver_rect = QRectF(separator_x, content_rect.y(), receiver_col_width, content_rect.height())
    current_y = receiver_rect.y()

    if receiver_pixmap and not receiver_pixmap.isNull():
        logo_height = int(mm_to_px(25))
        scaled_pixmap = receiver_pixmap.scaledToHeight(logo_height, Qt.SmoothTransformation)
        logo_x = receiver_rect.x() + (receiver_rect.width() - scaled_pixmap.width()) / 2
        painter.drawPixmap(int(logo_x), int(current_y), scaled_pixmap)
        current_y += scaled_pixmap.height() + mm_to_px(2.5)

    current_y = draw_plain_text(painter, current_y, receiver_rect, "ผู้รับ", _get_font(10.5, bold=True), QColor("#64748b"), Qt.AlignLeft, 0)

    painter.setPen(QColor("#e2e8f0"))
    painter.drawLine(QPointF(receiver_rect.x(), current_y + mm_to_px(1)), QPointF(receiver_rect.right(), current_y + mm_to_px(1)))
    current_y += mm_to_px(3.5)

    current_y = draw_plain_text(painter, current_y, receiver_rect, receiver_name, _get_font(12, bold=True), QColor("#000000"), Qt.TextWordWrap, 3.5)
    
    # Use QTextDocument for rich text (address)
    doc.setDefaultFont(_get_font(10.5))
    doc.setHtml(f'<span style="color: #334155;">{receiver_address}</span>')
    doc.setTextWidth(receiver_rect.width())
    doc.drawContents(painter, QRectF(QPointF(receiver_rect.x(), current_y), doc.size()))
    current_y += doc.size().height() + mm_to_px(2.5)

    current_y = draw_plain_text(painter, current_y, receiver_rect, receiver_tel, _get_font(10.5, bold=True), QColor("#334155"), Qt.TextWordWrap, 2.5)
    current_y = draw_plain_text(painter, current_y, receiver_rect, receiver_delivery_by, _get_font(10.5, bold=True), QColor("#334155"), Qt.TextWordWrap, 2.5)
    if receiver_note and receiver_note != "Note: ":
        note_font = _get_font(9.5)
        note_font.setItalic(True)
        draw_plain_text(painter, current_y, receiver_rect, receiver_note, note_font, QColor("#ef4444"), Qt.TextWordWrap, 0)

    # --- 3. Draw Absolute-Positioned Elements ---
    painter.setPen(QColor("#e2e8f0"))
    painter.drawLine(QPointF(separator_x - mm_to_px(1), content_rect.y()), QPointF(separator_x - mm_to_px(1), content_rect.bottom()))

    painter.setFont(_get_font(10.5, bold=True))
    painter.setPen(QColor("#64748b"))
    copy_rect = QRectF(content_rect.x(), content_rect.bottom() - mm_to_px(10), sender_col_width, mm_to_px(10))
    painter.drawText(copy_rect, Qt.AlignLeft | Qt.AlignVCenter, copy_text)