import tgm
from telegram import InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from storage import storage
from barcode_reader import barCodeReader
from ui_generate_qr import ui_generate_qr_start, ui_generate_qr_handler, ui_receive_qr_numbers
import re

# Текстовые константы
TEXT_SELECT_LOCATION = "Выберите локацию"
TEXT_LOAD_BIRD = "Загрузите птицу"
TEXT_ANIMAL_NUMBER = "Номер животного"
TEXT_CAPTURE_PLACE = "Место отлова"
TEXT_CAPTURE_TIME = "Время отлова"
TEXT_POLLUTION_DEGREE = "Степень загрязнения"
TEXT_WEIGHT = "Вес"
TEXT_NOT_SPECIFIED = "Не указан"
TEXT_SPECIES = "Вид"
TEXT_CLINICAL_CONDITION = "Клиническое состояние"
TEXT_HISTORY = "История"
TEXT_CHANGE_LOCATION = "Смена локации или генерация кода"
TEXT_GENERATE_QR_BUTTON = "🔲 Генерация QR"
TEXT_QR_GENERATION = "📌 Выберите способ генерации QR-кодов:"
TEXT_GENERATING_QR = "⏳ Генерация QR-кодов для {numbers}..."
TEXT_GENERATING_COUNT_QR = "⏳ Генерация {count} QR-кодов..."
TEXT_QR_CODES_READY = "📄 Ваши QR-коды"

CAPTURE_DATETIME_FORMAT = "%d.%m.%y %H:%M"

# Глобальные переменные
ui_welcome_mode = {}
kbd_addr_list = {}

##########################################
# UI menu
##########################################

def add_hdr_item(label, value):
    text = f'{label}: '
    if value:
        text += f'{value}\n'
    else:
        text += '-\n'
    return text

def ui_welcome_get_card(animal_id):
    animal = storage.get_animal_by_id(animal_id)
    if animal:
        text = add_hdr_item(TEXT_ANIMAL_NUMBER, animal["bar_code"])
        text += add_hdr_item(TEXT_CAPTURE_PLACE, animal["place_capture"])
        text += add_hdr_item(TEXT_CAPTURE_TIME, animal["capture_datetime"].strftime(CAPTURE_DATETIME_FORMAT))
        text += add_hdr_item(TEXT_POLLUTION_DEGREE, animal["degree_pollution"])
        text += add_hdr_item(TEXT_WEIGHT, f"{animal['weight']} гр." if animal["weight"] else TEXT_NOT_SPECIFIED)
        text += add_hdr_item(TEXT_SPECIES, animal["species"] if animal["species"] else TEXT_NOT_SPECIFIED)
        text += add_hdr_item(TEXT_CLINICAL_CONDITION, animal["clinical_condition_admission"] if animal["clinical_condition_admission"] else TEXT_NOT_SPECIFIED)
        text += '---------------\n'
        return text
    return None

def ui_welcome(user, key=None, msg=None):
    if not user:
        print('[!!] User not found!')
        return "Ошибка!", None

    if user["location_id"] is None or user["location_name"] is None:
        return welcome_sel_addr(user, key)

    bird = None
    if "bird" in user:
        bird = user["bird"]
    if not bird:
        return ui_load_bird(user, key, msg)

    text = f'Адрес: {user["location_name"]}\n'
    text += ui_welcome_get_card(bird["animal_id"])
    arm_list = storage.get_arms(user["location_id"])
    # todo Очищать welcome_handlers при смене локации
    if arm_list is not None:
        for arm in arm_list:
            key = f"kbd_mode_apm{arm['arm_id']}"
            ui_welcome_mode[key] = arm['arm_name']
            # todo Продумать как убрать хардкод
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
            elif arm['arm_id'] == 5:
                welcome_handlers[key] = ui_nanny_mode

    ui_welcome_mode.update({
        "kbd_history": TEXT_HISTORY,
        "kbd_load_bird": TEXT_LOAD_BIRD,
        "kbd_sel_addr": TEXT_CHANGE_LOCATION,
    })

    return text, tgm.make_inline_keyboard(ui_welcome_mode)

def welcome_sel_addr(user, key=None, msg=None):
    locations = storage.get_location()
    kbd_addr_list.clear()

    if locations:
        for location in locations:
            key = f"kbd_addr_{location['location_id']}"
            kbd_addr_list[key] = location['location_name']
            welcome_handlers[key] = welcome_addr_hndl

    kbd_addr_list["kbd_generate_qr"] = TEXT_GENERATE_QR_BUTTON
    welcome_handlers["kbd_generate_qr"] = ui_generate_qr_start

    return TEXT_SELECT_LOCATION, tgm.make_inline_keyboard(kbd_addr_list)

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
# Callback handlers
##########################################

welcome_handlers = {
    "kbd_sel_addr": welcome_sel_addr,
    "kbd_cancel": ui_welcome,
    "kbd_done": ui_welcome,
}


kbd_addr_list["kbd_generate_qr"] = TEXT_GENERATE_QR_BUTTON
welcome_handlers.update({
    "kbd_generate_qr": ui_generate_qr_start  # Только кнопка для перехода в меню генерации QR
})

from ui_load_bird import *
from ui_apm1 import *
from ui_apm2 import *
# todo Больше не нужно?
# from ui_apm3 import *
from ui_apm4 import *
from ui_apm5 import *
from ui_apm6 import *
from ui_apm_nanny import *
from ui_history import *

welcome_handlers.update({
    "kbd_load_bird": ui_load_bird,
    "kbd_history": ui_history_mode,
})

##########################################
# Main callback process
##########################################

async def ui_message_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update["message"]["from"]["username"]
    user = storage.get_user(user_id)
    
    if not user:
        print(f'[..] New user {user_id}')
        storage.add_user(user_id)
        user = storage.get_user(user_id)

    # Проверка: ожидается ли ввод номеров для QR-кодов
    if context.user_data.get("awaiting_qr_numbers"):
        await ui_receive_qr_numbers(update, context)
        return  # Завершаем выполнение, чтобы другие хендлеры не перехватывали

    if not user["mode"]:
        text, keyboard = ui_welcome(user)
    elif user["mode"] in welcome_handlers:
        text, keyboard = welcome_handlers[user["mode"]](user, msg=update.message.text)
    else:
        print(f'[!!] Got unknown msg entry {user["mode"]}')
        text, keyboard = ui_welcome(user)

    await update.message.reply_text(f'{text}', reply_markup=InlineKeyboardMarkup(keyboard))

async def ui_button_pressed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user_id = query["from_user"]["username"]
    user = storage.get_user(user_id)
    if not user:
        storage.add_user(user_id)
        user = storage.get_user(user_id)

    # Проверяем, если это кнопка из меню генерации QR-кодов
    if query.data.startswith("kbd_generate_"):
        await ui_generate_qr_handler(update=update, context=context)
        return

    if query.data in welcome_handlers:
        handler = welcome_handlers[query.data]
        text, keyboard = handler(user, query.data, msg=query.message.text)
    else:
        text, keyboard = ui_welcome(user)

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


