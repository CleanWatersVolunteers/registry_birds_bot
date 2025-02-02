import tgm
from telegram import InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler, ContextTypes, filters
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics import renderPDF
import re
from PyPDF2 import PdfMerger
from storage import QRCodeStorage, storage

# Константы PDF
CM_TO_PT = 28.35
CELL_WIDTH = int(70 * CM_TO_PT / 10)
CELL_HEIGHT = int(37.1 * CM_TO_PT / 10)
QR_SIZE = int(CELL_WIDTH * 0.4)
TEXT_WIDTH = int(CELL_WIDTH * 0.6)
TEXT_HEIGHT = int(CELL_HEIGHT)
FONT_NAME = "Helvetica-Bold"

# Текстовые константы
TEXT_SELECT_QR_GENERATION = "📌 Выберите способ генерации QR-кодов:"
TEXT_ENTER_OLD_QR = "Введите номера старых QR-кодов через запятую (например: 1054, 2404):"
TEXT_ERROR_NO_NUMBERS = "❌ Ошибка: не найдено ни одного числа. Введите номера заново."
TEXT_GENERATING_QR = "⏳ Генерация QR-кодов для {numbers}..."
TEXT_GENERATING_COUNT_QR = "⏳ Генерация {count} QR-кодов..."
TEXT_QR_CODES_READY = "📄 Ваши QR-коды"
FILENAME_QR_CODES = "qr_codes_{user_input}.pdf"
FILENAME_QR_CODES_COUNT = "qr_codes_{count}_{start}-{end}.pdf"

qr_generation_menu = {
    "kbd_generate_old_qr": "Старые QR",
    "kbd_generate_24_qr": "24 новых",
    "kbd_generate_48_qr": "48 новых",
    "kbd_generate_72_qr": "72 новых",
    "kbd_back_qr": "Назад"
}

def merge_pdfs(pdf_buffers):
    merger = PdfMerger()
    for pdf_buffer in pdf_buffers:
        merger.append(pdf_buffer)
    combined_pdf = BytesIO()
    merger.write(combined_pdf)
    merger.close()
    combined_pdf.seek(0)
    return combined_pdf

async def ui_generate_qr_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    keyboard = tgm.make_inline_keyboard(qr_generation_menu)
    try:
        if query:
            await query.answer()
            try:
                await query.message.delete()
            except Exception as e:
                print(f"[!!] Ошибка удаления старого меню: {e}")
            await query.message.reply_text(TEXT_SELECT_QR_GENERATION, reply_markup=InlineKeyboardMarkup(keyboard))
        elif update.message:
            await update.message.reply_text(TEXT_SELECT_QR_GENERATION, reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        print(f"[!!] Ошибка при обновлении меню QR-кодов: {e}")
        await update.message.reply_text(TEXT_SELECT_QR_GENERATION, reply_markup=InlineKeyboardMarkup(keyboard))


async def ui_generate_qr_old(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if query.message:
        try:
            await query.message.delete()
        except Exception as e:
            print(f"[!!] Ошибка удаления старого меню: {e}")
    await query.message.chat.send_message(TEXT_ENTER_OLD_QR)
    context.user_data["awaiting_qr_numbers"] = True

async def ui_receive_qr_numbers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.user_data.get("awaiting_qr_numbers"):
        return
    context.user_data["awaiting_qr_numbers"] = False
    user_input = update.message.text.strip()
    qr_numbers = sorted(set(re.findall(r'\d+', user_input)))
    if not qr_numbers:
        await update.message.reply_text(TEXT_ERROR_NO_NUMBERS)
        context.user_data["awaiting_qr_numbers"] = True
        return
    loading_message = await update.message.reply_text(TEXT_GENERATING_QR.format(numbers=', '.join(qr_numbers)))
    pdf_buffer = generate_qr_pdf(qr_numbers)
    filename = FILENAME_QR_CODES.format(user_input=user_input.replace(' ', ''))
    await loading_message.delete()
    await update.message.reply_document(document=pdf_buffer, filename=filename, caption=TEXT_QR_CODES_READY)
    await ui_generate_qr_start(update, context)

async def ui_generate_qr_common(update: Update, context: ContextTypes.DEFAULT_TYPE, count: int) -> None:
    query = update.callback_query
    await query.answer()

    # Получаем последний использованный QR-код из БД
    start_number = QRCodeStorage.get_qr_start_value()
    if start_number is None:
        print("[!!] Ошибка: Не удалось получить start_number из БД!")
        await query.message.reply_text("❌ Ошибка: невозможно получить начальный номер QR-кодов.")
        return

    start_number += 1
    end_number = start_number + count - 1

    print(f"[..] Генерация QR-кодов с {start_number} по {end_number}")

    loading_message = await query.message.reply_text(TEXT_GENERATING_COUNT_QR.format(count=count))

    pdf_buffers = [generate_qr_pdf([str(start_number + (i * 24) + j) for j in range(24)]) for i in range(count // 24)]
    combined_pdf = merge_pdfs(pdf_buffers) if len(pdf_buffers) > 1 else pdf_buffers[0]
    filename = FILENAME_QR_CODES_COUNT.format(count=count, start=start_number, end=end_number)

    await loading_message.delete()
    await query.message.reply_document(document=combined_pdf, filename=filename, caption=TEXT_QR_CODES_READY)

    QRCodeStorage.set_qr_start_value(end_number)
    print(f"[OK] Последний QR-код обновлен в БД: {end_number}")

    try:
        await query.message.delete()
    except Exception as e:
        print(f"[!!] Ошибка удаления старого меню: {e}")

    await ui_generate_qr_start(update, context)

async def ui_generate_qr_24(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await ui_generate_qr_common(update, context, 24)

async def ui_generate_qr_48(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await ui_generate_qr_common(update, context, 48)

async def ui_generate_qr_72(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await ui_generate_qr_common(update, context, 72)

def generate_qr_pdf(qr_numbers):
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

async def ui_generate_qr_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.username
    user = storage.get_user(user_id)
    from ui_welcome import ui_welcome
    text, keyboard = ui_welcome(user)
    try:
        await query.message.edit_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception:
        await query.message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))