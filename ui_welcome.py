import tgm
from telegram import InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, ContextTypes, filters
from storage import storage
from barcode_reader import barCodeReader

welcome_text_sel_addr = 'Выберите локацию'
welcome_text_sel_bird = 'Загрузите птицу'
sex_male = "муж"
sex_female = "жен"
capture_datetime_format = "%d.%m.%y %H:%M"

ui_welcome_mode = {
    "kbd_mode_apm2":"Первичка перед мойкой (АРМ2)",
    "kbd_mode_apm3":"Мойка (АРМ3)",
    "kbd_mode_apm4":"Прием в стационар (АРМ4)",
    "kbd_mode_apm5":"Первичка в стационаре (АРМ5)",
    "kbd_mode_apm6":"Мед.обслуживание - Врач (АРМ6)",
    "kbd_feeding":"Кормление", 
    "kbd_mass":"Изменить вес",
    "kbd_history":"История", 
    "kbd_load_bird":"Загрузить птицу",
    "kbd_sel_addr":"Сменить локацию", 
}

kbd_addr_list = {
    "kbd_addr1" : "Жемчужная",
    "kbd_addr3" : "Полярные зори",
}

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
        if animal["female"] is not None:
            if animal["female"] == b'1':
                text += add_hdr_item("Пол", sex_female)
            else:
                text += add_hdr_item("Пол", sex_male)
        else:
            text += add_hdr_item("Пол", "Не указан")
        if animal["clinical_condition_admission"] is not None:
            text += add_hdr_item("Клиническое состояние", animal["clinical_condition_admission"])
        else:
            text += add_hdr_item("Клиническое состояние", "Не указано")
        text += '---------------\n'            
    return text 

def ui_welcome(user, key = None, msg=None):
    if not user:
        print('[!!] User not found!')
        return "Ошибка!", None
    if not user["addr"]:
        return welcome_sel_addr(user, key)

    text = f'Адрес: {user["addr"]}\n'
    bird = None
    if "bird" in user:
        bird = user["bird"]
    if not bird:
        return ui_load_bird(user, key, msg)
    
    text += ui_welcome_get_card(bird["bar_code"])
    for num in range(2,7):
        id = f'kbd_mode_apm{num}'
        if id in ui_welcome_mode:
            stage_num = f'stage{num}'
            if stage_num in bird:
                text += '✅ '
            else:
                text += '❌ '
            text += f'{ui_welcome_mode[id]}:\n'
    return text, tgm.make_inline_keyboard(ui_welcome_mode)


def welcome_sel_addr(user, key=None, msg=None):
    text = welcome_text_sel_addr
    keyboard = tgm.make_inline_keyboard(kbd_addr_list)
    return text, keyboard

def welcome_addr_hndl(user, key=None, msg=None):
    if key in kbd_addr_list:
        user["addr"] = kbd_addr_list[key]
    else:
        user["addr"] = None
    if "bird" in user:
        return ui_welcome(user)
    return ui_load_bird(user, key, msg)

##########################################
# Callback handlers
##########################################
welcome_handlers = {
    "kbd_sel_addr":welcome_sel_addr,
    "kbd_cancel":ui_welcome,
    "kbd_done":ui_welcome,
}

from ui_load_bird import *
from ui_apm1 import *
from ui_apm2 import *
from ui_apm3 import *
from ui_apm4 import *
from ui_apm5 import *
from ui_apm6 import *
from ui_feeding import *
from ui_mass import *
from ui_history import *

welcome_handlers["kbd_load_bird"] = ui_load_bird
welcome_handlers["kbd_addr1"] = welcome_addr_hndl
welcome_handlers["kbd_addr3"] = welcome_addr_hndl

welcome_handlers["kbd_mode_apm1"] = ui_apm1_mode
welcome_handlers["kbd_mode_apm2"] = ui_apm2_mode
welcome_handlers["kbd_mode_apm3"] = ui_apm3_mode
welcome_handlers["kbd_mode_apm4"] = ui_apm4_mode
welcome_handlers["kbd_mode_apm5"] = ui_apm5_mode
welcome_handlers["kbd_mode_apm6"] = ui_apm6_mode
welcome_handlers["kbd_feeding"] = ui_feeding_mode
welcome_handlers["kbd_mass"] = ui_mass_entry_mode
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
            text, keyboard = welcome_handlers[query.data](user, query.data,msg=query.message.text)
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
        file_name = new_file.file_path.split('/')[-1]
        await new_file.download_to_drive()
        code = barCodeReader(file_name)
        if len(code) == 1:
            text, keyboard = ui_load_bird_barcode(user, msg=code[0])
        else:
            text, keyboard = ui_load_bird_barcode(user, msg='')
    await update.message.reply_text(f'{text}', reply_markup=InlineKeyboardMarkup(keyboard))
    return None
