# Генерация QR

from database import Database as db
from storage import storage

from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics import renderPDF
from PyPDF2 import PdfMerger


# Константы PDF
CM_TO_PT = 28.35
CELL_WIDTH = int(70 * CM_TO_PT / 10)
CELL_HEIGHT = int(37.1 * CM_TO_PT / 10)
QR_SIZE = int(CELL_WIDTH * 0.4)
TEXT_WIDTH = int(CELL_WIDTH * 0.6)
TEXT_HEIGHT = int(CELL_HEIGHT)
FONT_NAME = "Helvetica-Bold"

def merge_pdf_pages(pdf_buffers):
    merger = PdfMerger()
    for pdf_buffer in pdf_buffers:
        merger.append(pdf_buffer)
    combined_pdf = BytesIO()
    merger.write(combined_pdf)
    merger.close()
    combined_pdf.seek(0)
    return combined_pdf

def gen_pdf_page(qr_numbers):
    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=A4)

    # Константы для QR-кодов на листе
    COLUMNS = 3
    ROWS = 8
    X_SPACING = int((A4[0] - COLUMNS * CELL_WIDTH) / (COLUMNS - 1))
    Y_SPACING = int((A4[1] - ROWS * CELL_HEIGHT) / (ROWS - 1))

    for index, data in enumerate(qr_numbers):
        col = index % COLUMNS
        row = index // COLUMNS
        if row >= ROWS:
            break
        x = col * (CELL_WIDTH + X_SPACING)
        y = A4[1] - (row + 1) * CELL_HEIGHT - row * Y_SPACING
        qr = QrCodeWidget(data)
        qr_drawing = Drawing(QR_SIZE * 1.02, QR_SIZE * 1.02)
        qr_drawing.add(qr)
        renderPDF.draw(qr_drawing, pdf, x - 8, y + (CELL_HEIGHT - QR_SIZE) / 2)
        pdf.setFont(FONT_NAME, 20)
        text_width_pt = pdf.stringWidth(data, FONT_NAME, 20)
        scale_factor_x = TEXT_WIDTH / text_width_pt
        scale_factor_y = TEXT_HEIGHT / 20
        pdf.saveState()
        pdf.translate(x + QR_SIZE - 5, y + 20)
        pdf.scale(scale_factor_x, scale_factor_y)
        pdf.drawString(0, 0, data)
        pdf.restoreState()
        pdf.setLineWidth(0.5)
        pdf.rect(x, y, CELL_WIDTH, CELL_HEIGHT)
    pdf.save()
    pdf_buffer.seek(0)
    return pdf_buffer

##################################
# Global API
##################################

qr_cmd_gen24 = 'qr_gen24'
qr_cmd_gen48 = 'qr_gen48'
qr_cmd_gen72 = 'qr_gen72'
qr_cmd_old = 'qr_old'

def gen_pdf(qr_buf):
	qr_numbers = qr_buf 
	pages = []
	for i in range(0,len(qr_numbers),24):
		pages.append(gen_pdf_page(qr_numbers[i:i+24]))
	return f'qr_{sorted(qr_buf)[0]}_{sorted(qr_buf)[-1]}.pdf', merge_pdf_pages(pages)

