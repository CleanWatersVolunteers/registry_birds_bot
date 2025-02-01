import tgm  # Вероятно, кастомный модуль для работы с Telegram
from ui_generate_qr import ui_generate_qr_start  # Импорт модуля меню генерации
from telegram import InlineKeyboardMarkup, Update  # Импортируем клавиатуру и Update из telegram API
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler, ContextTypes  # Обработчики событий
from storage import storage
from barcode_reader import barCodeReader  # Импорт модуля для чтения штрих-кодов
import re


welcome_text_sel_addr = 'Выберите локацию'
welcome_text_sel_genqr = 'Генерация QR-кодов'
welcome_text_sel_bird = 'Загрузите птицу'
capture_datetime_format = "%d.%m.%y %H:%M"

ui_welcome_mode = {}

kbd_addr_list = {}

##########################################
# UI menu (Формирование интерфейса)
##########################################

async def ui_generate_qr_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    # Показываем меню выбора
    text = "📌 Выберите способ генерации QR-кодов:"
    keyboard = tgm.make_inline_keyboard({
        "kbd_generate_old_qr": "Старые QR",
        "kbd_generate_24_qr": "24 новых",
        "kbd_generate_48_qr": "48 новых",
        "kbd_generate_72_qr": "72 новых",
        "kbd_back_qr": "Назад"
    })

    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


def add_hdr_item(label, value):
    text = f'{label}: '
    if value:
        text += f'{value}\n'
    else:
        text += '-\n'
    return text

def ui_welcome_get_card(bar_code):
    text = add_hdr_item("Номер животного", bar_code)
    animal = storage.get_animal_by_bar_code(bar_code)
    if animal is not None:
        text += add_hdr_item("Место отлова", animal["place_capture"])
        text += add_hdr_item("Время отлова", animal["capture_datetime"].strftime(capture_datetime_format))
        text += add_hdr_item("Степень загрязнения", animal["degree_pollution"])

        text += add_hdr_item("Вес", f"{animal['weight']} гр." if animal["weight"] is not None else "Не указан")
        text += add_hdr_item("Вид", animal["species"] if animal["species"] is not None else "Не указан")
        text += add_hdr_item("Клиническое состояние", animal["clinical_condition_admission"] if animal["clinical_condition_admission"] is not None else "Не указано")
        text += '---------------\n'
    return text

def ui_welcome(user, key=None, msg=None):

    if not user:
        print('[!!] User not found!')
        return "Ошибка!", None

    if user["location_id"] is None or user["location_name"] is None:
        return welcome_sel_addr(user, key)

    bird = user.get("bird")
    if not bird:
        return ui_load_bird(user, key, msg)

    text = f'Адрес: {user["location_name"]}\n'
    text += ui_welcome_get_card(bird["bar_code"])

    arm_list = storage.get_arms(user["location_id"])

    if arm_list is not None:
        for arm in arm_list:
            key = f"kbd_mode_apm{arm['arm_id']}"
            ui_welcome_mode[key] = arm['arm_name']

            # nado bu Убрать хардкод обработчиков
            if arm['arm_id'] == 0:
                welcome_handlers[key] = ui_apm1_mode
            elif arm['arm_id'] == 1:
                welcome_handlers[key] = ui_apm2_mode
            elif arm['arm_id'] == 2:
                welcome_handlers[key] = ui_apm4_mode
            elif arm['arm_id'] == 3:
                welcome_handlers[key] = ui_apm5_mode
            elif arm['arm_id'] == 4:
                welcome_handlers[key] = ui_apm6_mode

    ui_welcome_mode.update({
        "kbd_feeding": "Кормление",
        "kbd_mass": "Взвешивание",
        "kbd_history": "История",
        "kbd_load_bird": "Загрузить птицу",
        "kbd_sel_addr": "Выбор локации и QR-коды",
    })

    return text, tgm.make_inline_keyboard(ui_welcome_mode)


def welcome_sel_addr(user, key=None, msg=None):
    locations = storage.get_location()
    kbd_addr_list.clear()

    if locations is not None:
        for location in locations:
            key = f"kbd_addr_{location['location_id']}"
            kbd_addr_list[key] = location['location_name']
            welcome_handlers[key] = welcome_addr_hndl

    # Добавляем кнопку "ГЕНЕРАЦИЯ КОДА"
    kbd_addr_list["kbd_generate_qr"] = "🔲 ГЕНЕРАЦИЯ QR"
    welcome_handlers["kbd_generate_qr"] = ui_generate_qr_start

    return welcome_text_sel_addr, tgm.make_inline_keyboard(kbd_addr_list)

def welcome_addr_hndl(user, key=None, msg=None):
    if key in kbd_addr_list:
        match = re.search(r'\d+$', key)
        if match:
            user["location_id"] = int(match.group())
            user["location_name"] = kbd_addr_list[key]
        else:
            print("Число не найдено.")

    if "bird" in user:
        return ui_welcome(user)
    return ui_load_bird(user, key, msg)

##########################################
# Callback handlers (обработчики событий)
##########################################

welcome_handlers = {
    "kbd_sel_addr": welcome_sel_addr,
    "kbd_cancel": ui_welcome,
    "kbd_done": ui_welcome,
}

welcome_handlers["kbd_generate_qr"] = ui_generate_qr_start  # Обработчик перехода в меню qr

# Импортируем обработчики действий
from ui_load_bird import *
from ui_apm1 import *
from ui_apm2 import *
# nado bu Возможно, не нужно?
# from ui_apm3 import *
from ui_apm4 import *
from ui_apm5 import *
from ui_apm6 import *
from ui_feeding import *
from ui_mass import *
from ui_history import *

# Добавляем кнопки в меню
welcome_handlers.update({
    "kbd_load_bird": ui_load_bird,
    "kbd_feeding": ui_feeding_mode,
    "kbd_mass": ui_mass_entry_mode,
    "kbd_history": ui_history_mode,
})


##########################################
# Main callback process (главная логика)
##########################################

async def ui_message_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update["message"]["from"]["username"]
    user = storage.get_user(user_id)

    if not user:
        print(f'[..] New user {user_id}')
        storage.add_user(user_id)
        user = storage.get_user(user_id)

    #Проверяем, ожидается ли ввод QR-кодов
    if context.user_data.get("awaiting_qr_numbers", False):
        await ui_receive_qr_numbers(update, context)  # Передаём управление обработчику QR-кодов
        return  # Выходим, чтобы не выполнять `ui_welcome`

    #Если это обычное сообщение, выполняем стандартный обработчик
    text, keyboard = welcome_handlers.get(user["mode"], ui_welcome)(user, msg=update.message.text)

    await update.message.reply_text(f'{text}', reply_markup=InlineKeyboardMarkup(keyboard))

async def ui_button_pressed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user_id = query["from_user"]["username"]
    user = storage.get_user(user_id)

    if not user:
        print(f'[!!] User not found: {user_id}')
        return

    # Если нажата кнопка "ГЕНЕРАЦИЯ QR"
    if query.data == "kbd_generate_qr":
        await ui_generate_qr_start(update, context)  # Вызов меню генерации QR-кодов
        return

    handler_function = welcome_handlers.get(query.data, ui_welcome)

    # Если обработчик — это функция генерации QR-кодов или возврата, вызываем без `msg`
    if handler_function in [ui_generate_qr_24, ui_generate_qr_48, ui_generate_qr_72, ui_generate_qr_old, ui_generate_qr_back]:
        await handler_function(update, context)
        return  # Выходим, чтобы не выполнять код ниже

    # Если это другая функция, вызываем с `msg`
    text, keyboard = handler_function(user, query.data, msg=query.message.text)

    # Проверяем, что `keyboard` — это словарь, преобразуем в InlineKeyboardMarkup
    if isinstance(keyboard, dict):
        keyboard = [[InlineKeyboardButton(label, callback_data=key)] for key, label in keyboard.items()]

    await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))


# Barcode callback
async def ui_photo_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update["message"]["from"]["username"]
    user = storage.get_user(user_id)

    if not user:
        print(f'[..] New user {user_id}')
        storage.add_user(user_id)
        user = storage.get_user(user_id)
        text, keyboard = ui_welcome(user)
    else:
        file_id = update.message.photo[0].file_id
        new_file = await update.message.effective_attachment[-1].get_file()
        data = await new_file.download_as_bytearray()
        code = barCodeReader(data)
        if len(code) == 1:
            text, keyboard = ui_load_bird_barcode(user, msg=code[0])
        else:
            text, keyboard = ui_load_bird_barcode(user, msg='')
    await update.message.reply_text(f'{text}', reply_markup=InlineKeyboardMarkup(keyboard))
    return None

# Импорт и обработчики для qr
from ui_generate_qr import (
    ui_generate_qr_start,
    ui_generate_qr_old,
    ui_generate_qr_24,
    ui_generate_qr_48,
    ui_generate_qr_72,
    ui_generate_qr_back,
    ui_receive_qr_numbers
)


welcome_handlers.update({
    "kbd_generate_old_qr": ui_generate_qr_old,
    "kbd_generate_24_qr": ui_generate_qr_24,
    "kbd_generate_48_qr": ui_generate_qr_48,
    "kbd_generate_72_qr": ui_generate_qr_72,
    "kbd_back_qr": ui_generate_qr_back
})
