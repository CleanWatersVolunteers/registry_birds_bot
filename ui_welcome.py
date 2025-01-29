import tgm
from telegram import InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler, ContextTypes
from storage import storage
from barcode_reader import barCodeReader
import re

welcome_text_sel_addr = 'Выберите локацию'
welcome_text_sel_bird = 'Загрузите птицу'
capture_datetime_format = "%d.%m.%y %H:%M"

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

def ui_welcome_get_card(bar_code):
    text = add_hdr_item("Номер животного", bar_code)
    animal = storage.get_animal_by_bar_code(bar_code)
    if animal is not None:
        text += add_hdr_item("Место отлова", animal["place_capture"])
        text += add_hdr_item("Время отлова", animal["capture_datetime"].strftime(capture_datetime_format))
        text += add_hdr_item("Степень загрязнения", animal["degree_pollution"])
        if animal["weight"] is not None:
            text += add_hdr_item("Вес", str(animal["weight"]) + " гр.")
        else:
            text += add_hdr_item("Вес", "Не указан")
        if animal["species"] is not None:
            text += add_hdr_item("Вид", animal["species"])
        else:
            text += add_hdr_item("Вид", "Не указан")
        if animal["clinical_condition_admission"] is not None:
            text += add_hdr_item("Клиническое состояние", animal["clinical_condition_admission"])
        else:
            text += add_hdr_item("Клиническое состояние", "Не указано")
        text += '---------------\n'
    return text

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
    text += ui_welcome_get_card(bird["bar_code"])
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
                welcome_handlers[key] = ui_apm7_mode

    # ui_welcome_mode["kbd_feeding"] = "Кормление"
    # ui_welcome_mode["kbd_mass"] = "Взвешивание"
    ui_welcome_mode["kbd_history"] = "История"
    ui_welcome_mode["kbd_load_bird"] = "Загрузить птицу"
    ui_welcome_mode["kbd_sel_addr"] = "Сменить локацию"
    return text, tgm.make_inline_keyboard(ui_welcome_mode)

def welcome_sel_addr(user, key=None, msg=None):
    locations = storage.get_location()
    if locations is not None:
        for location in locations:
            # Прячем идентификатор адреса
            key = f"kbd_addr_{location['location_id']}"
            kbd_addr_list[key] = location['location_name']
            welcome_handlers[key] = welcome_addr_hndl
    text = welcome_text_sel_addr
    keyboard = tgm.make_inline_keyboard(kbd_addr_list)
    return text, keyboard

def welcome_addr_hndl(user, key=None, msg=None):
    if key in kbd_addr_list:
        # Извлекаем припрятанный идентификатор адреса
        match = re.search(r'\d+$', key)
        if match:
            user["location_id"] = int(match.group())
            user["location_name"] = kbd_addr_list[key]
        else:
            print("Число не найдено.")
    else:
        user["location_id"] = None
        user["location_name"] = None
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

from ui_load_bird import *
from ui_apm1 import *
from ui_apm2 import *
# todo Больше не нужно?
# from ui_apm3 import *
from ui_apm4 import *
from ui_apm5 import *
from ui_apm6 import *
from ui_apm7 import *
# from ui_feeding import *
# from ui_mass import *
from ui_history import *

welcome_handlers["kbd_load_bird"] = ui_load_bird
# welcome_handlers["kbd_feeding"] = ui_feeding_mode
# welcome_handlers["kbd_mass"] = ui_mass_entry_mode
welcome_handlers["kbd_history"] = ui_history_mode


##########################################
# Main callback process
##########################################

async def ui_message_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # print(update.message)
    user_id = update["message"]["from"]["username"]
    user = storage.get_user(user_id)
    if not user:
        print(f'[..] New user {user_id}')
        storage.add_user(user_id)
        user = storage.get_user(user_id)

    if not user["mode"]:
        text, keyboard = ui_welcome(user)
    elif user["mode"] in welcome_handlers:
        text, keyboard = welcome_handlers[user["mode"]](user, msg=update.message.text)
    else:
        print(f'[!!] Got unknown msg entry {user["mode"]}')
        text, keyboard = ui_welcome(user)

    await update.message.reply_text(f'{text}', reply_markup=InlineKeyboardMarkup(keyboard))
    return None


async def ui_button_pressed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user_id = query["from_user"]["username"]
    user = storage.get_user(user_id)
    if not user:
        print(f'[..] New user {user_id}')
        storage.add_user(user_id)
        user = storage.get_user(user_id)
        text, keyboard = ui_welcome(user)
    else:
        if query.data in welcome_handlers:
            text, keyboard = welcome_handlers[query.data](user, query.data, msg=query.message.text)
        else:
            print(f'[!!] Got unknown kbd entry {query.data}')
            text, keyboard = ui_welcome(user)

    await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))
    return None

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