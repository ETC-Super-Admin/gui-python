import os
from PySide6.QtWidgets import QFileDialog, QMessageBox
from PySide6.QtCore import QStandardPaths, QSettings
from datetime import datetime

# Reportlab imports
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Image, Spacer, Frame, Flowable
from reportlab.lib.colors import HexColor, black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Database and config imports
from src.db.config_queries import get_config

# --- Font Setup ---
FONT_FAMILY = "Helvetica"
FONT_FAMILY_BOLD = "Helvetica-Bold"
try:
    fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'public', 'Sarabun')
    regular_font_path = os.path.join(fonts_dir, 'Sarabun-Regular.ttf')
    bold_font_path = os.path.join(fonts_dir, 'Sarabun-Bold.ttf')

    if os.path.exists(regular_font_path) and os.path.exists(bold_font_path):
        pdfmetrics.registerFont(TTFont('Sarabun-Regular', regular_font_path))
        pdfmetrics.registerFont(TTFont('Sarabun-Bold', bold_font_path))
        FONT_FAMILY = "Sarabun-Regular"
        FONT_FAMILY_BOLD = "Sarabun-Bold"
        print("Sarabun font successfully loaded for PDF generation.")
    else:
        print("Sarabun font not found in public/Sarabun. PDF will use Helvetica.")
except Exception as e:
    print(f"Could not load custom Sarabun font: {e}")

class Line(Flowable):
    """A simple horizontal line flowable."""
    def __init__(self, width, color=black):
        Flowable.__init__(self)
        self.width = width
        self.color = color

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(0.5)
        self.canv.line(0, 0, self.width, 0)

def save_widget_as_pdf(parent_widget, label_preview_widget, copies=1):
    settings = QSettings("ProAuto", "App")
    last_dir = settings.value("pdf/last_export_directory", QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    default_filename = f"shipping_label_{timestamp}.pdf"

    file_path, _ = QFileDialog.getSaveFileName(
        parent_widget,
        "Save PDF File",
        os.path.join(last_dir, default_filename),
        "PDF Files (*.pdf)"
    )

    if not file_path:
        return

    settings.setValue("pdf/last_export_directory", os.path.dirname(file_path))

    try:
        page_width, page_height = 150 * mm, 100 * mm
        c = canvas.Canvas(file_path, pagesize=(page_width, page_height))

        sender_address = label_preview_widget.sender_address_label.text()
        sender_tel = label_preview_widget.sender_tel_label.text()
        receiver_name = label_preview_widget.receiver_name_label.text()
        receiver_address = label_preview_widget.receiver_address_label.text()
        receiver_tel = label_preview_widget.receiver_tel_label.text()

        sender_logo_path = get_config("asset_sender_logo", "")
        receiver_logo_path = get_config("asset_receiver_logo", "")

        for i in range(copies):
            draw_label_page(c, page_width, page_height,
                            sender_logo_path, sender_address, sender_tel,
                            receiver_logo_path, receiver_name, receiver_address, receiver_tel,
                            f"{i + 1}/{copies}")
            if i < copies - 1:
                c.showPage()

        c.save()
        QMessageBox.information(parent_widget, "Success", f"Successfully saved {copies} page(s) to\n{file_path}")

    except Exception as e:
        QMessageBox.critical(parent_widget, "Error", f"Failed to save PDF: {e}")


def draw_label_page(c, page_width, page_height,
                    sender_logo_path, sender_address, sender_tel,
                    receiver_logo_path, receiver_name, receiver_address, receiver_tel,
                    copy_text):
    
    # --- Define Layout & Style Constants ---
    margin = 5 * mm
    content_width = page_width - (2 * margin)
    content_height = page_height - (2 * margin)
    
    sender_col_width = content_width * 0.4
    receiver_col_width = content_width * 0.6
    separator_x = margin + sender_col_width + (2 * mm)

    # --- Define Styles ---
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('title', parent=styles['Normal'], fontName=FONT_FAMILY_BOLD, fontSize=10.5, textColor=HexColor("#64748b"))
    address_style = ParagraphStyle('address', parent=styles['Normal'], fontName=FONT_FAMILY, fontSize=10.5, leading=14, textColor=HexColor("#334155"))
    tel_style = ParagraphStyle('tel', parent=address_style, fontName=FONT_FAMILY_BOLD)
    receiver_name_style = ParagraphStyle('receiver_name', parent=styles['Normal'], fontName=FONT_FAMILY_BOLD, fontSize=12, textColor=HexColor("#000000"))

    # --- Build Sender Story (Left Column) ---
    sender_story = []
    if sender_logo_path and os.path.exists(sender_logo_path):
        try:
            img_h = 60
            img_w = img_h * (16/9)
            img = Image(sender_logo_path, width=img_w, height=img_h)
            img.hAlign = 'CENTER'
            sender_story.append(img)
        except Exception as e:
            print(f"Could not draw sender image: {e}")
    
    sender_story.append(Spacer(1, 2.5 * mm))
    sender_story.append(Paragraph("FROM", title_style))
    sender_story.append(Spacer(1, 0.5 * mm))
    sender_story.append(Line(sender_col_width - (4*mm), color=HexColor("#e2e8f0")))
    sender_story.append(Spacer(1, 2.5 * mm))
    sender_story.append(Paragraph(sender_address.replace("\n", "<br/>"), address_style))
    sender_story.append(Spacer(1, 1.5 * mm))
    sender_story.append(Paragraph(sender_tel, tel_style))

    # --- Build Receiver Story (Right Column) ---
    receiver_story = []
    if receiver_logo_path and os.path.exists(receiver_logo_path):
        try:
            img_h = 80
            img_w = img_h * (16/9)
            img = Image(receiver_logo_path, width=img_w, height=img_h)
            img.hAlign = 'CENTER'
            receiver_story.append(img)
        except Exception as e:
            print(f"Could not draw receiver image: {e}")

    receiver_story.append(Spacer(1, 2.5 * mm))
    receiver_story.append(Paragraph("TO", title_style))
    receiver_story.append(Spacer(1, 0.5 * mm))
    receiver_story.append(Line(receiver_col_width - (4*mm), color=HexColor("#e2e8f0")))
    receiver_story.append(Spacer(1, 2.5 * mm))
    receiver_story.append(Paragraph(receiver_name, receiver_name_style))
    receiver_story.append(Spacer(1, 1.5 * mm))
    receiver_story.append(Paragraph(receiver_address.replace("\n", "<br/>"), address_style))
    receiver_story.append(Spacer(1, 1.5 * mm))
    receiver_story.append(Paragraph(receiver_tel, tel_style))

    # --- Create Frames and Draw Stories ---
    frame_height = content_height - (5*mm) # Reserve space at bottom for copy count
    sender_frame = Frame(margin, margin + (5*mm), sender_col_width, frame_height, id='sender', showBoundary=0)
    receiver_frame = Frame(separator_x, margin + (5*mm), receiver_col_width, frame_height, id='receiver', showBoundary=0)

    sender_frame.addFromList(sender_story, c)
    receiver_frame.addFromList(receiver_story, c)

    # --- Draw Absolute-Positioned Elements ---
    # Separator Line
    c.setStrokeColor(HexColor("#e2e8f0"))
    c.setLineWidth(1)
    c.line(separator_x, margin, separator_x, page_height - margin)

    # Copy Count Text
    c.setFont(FONT_FAMILY_BOLD, 10.5)
    c.setFillColor(HexColor("#64748b"))
    c.drawString(margin, margin, copy_text)
