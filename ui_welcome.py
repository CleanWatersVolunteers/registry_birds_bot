import tgm
from telegram import InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, ContextTypes, filters
from storage import storage
from barcode_reader import barCodeReader

welcome_text_sel_addr = 'Выберите локацию'
welcome_text_sel_bird = 'Добавьте/Выберите птицу'


ui_welcome_mode = {
    "kbd_mode_apm1":"Поступление (АРМ1)",
    "kbd_mode_apm2":"Первичка перед мойкой (АРМ2)",
    "kbd_mode_apm3":"Мойка (АРМ3)",
    "kbd_mode_apm4":"Прием в стационар (АРМ4)",
    "kbd_mode_apm5":"Первичка в стационаре (АРМ5)",
    "kbd_mode_apm6":"Мед.обслуживание - Врач (АРМ6)",
    # "kbd_mode_apm7":"Нянька (АРМ7)",
    # "kbd_mode_apm7":"Загон (АРМ8)",
    "kbd_add_bird":"Добавить птицу",
    "kbd_sel_bird":"Выбрать птицу",
    "kbd_sel_addr":"Сменить локацию", 
    "kbd_feeding":"Кормление", 
    "kbd_history":"История", 
}

ui_welcome_cancel = {
    "kbd_cancel":"Отмена", 
}
ui_welcome_done = {
    "kbd_done":"Готово",
    "kbd_cancel":"Отмена",
}

kbd_addr_list = {
    "kbd_addr1" : "Жемчужная",
    "kbd_addr2" : "Аристей",
    "kbd_addr3" : "Полярные зори",
    # "kbd_cancel":"Отмена",
}
kbd_menu_base = {
    "kbd_add_bird":"Добавить птицу",
    "kbd_sel_bird":"Выбрать птицу",
    "kbd_sel_addr":"Сменить локацию",  
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

def ui_welcome(user, key = None, msg=None):
    text = ''

    if not user:
        print('[!!] User not found!')
        return "Ошибка!", None
    
    # Check selected address
    if not user["addr"]:
        return welcome_sel_addr(user, key)

    text += f'Адрес: {user["addr"]}\n'

    # Check bird in list
    bird = None
    if user["code"]:
        bird = storage.get_bird(user["code"])
    if not bird:
        text += welcome_text_sel_bird
        return text, tgm.make_inline_keyboard(kbd_menu_base)
    

    text += add_hdr_item("Номер животного", user["code"])
    text += add_hdr_item("Место отлова", bird["capture_place"])
    text += add_hdr_item("Время отлова", bird["capture_date"])
    text += add_hdr_item("Степень загрязнения", bird["polution"])
    if bird["mass"]:
        text += add_hdr_item("Масса животного", bird["mass"] + "гр.")
    else:
        text += add_hdr_item("Масса животного", None)
    text += add_hdr_item("Вид", bird["species"])
    text += add_hdr_item("Пол", bird["sex"])
    text += add_hdr_item("Клиническое состояние", bird["clinic_state"])

    template_yes = '✅ '
    template_no = '❌ '

    for num in range(1,7):
        if bird[f'stage{num}']:
            text += template_yes
        else:
            text += template_no
        id = f'kbd_mode_apm{num}'
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
    return ui_welcome(user, key)

##########################################
# Callback handlers
##########################################
welcome_handlers = {
    "kbd_addr1":welcome_addr_hndl,
    "kbd_addr2":welcome_addr_hndl,
    "kbd_addr3":welcome_addr_hndl,

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
from ui_history import *

welcome_handlers["kbd_add_bird"] = ui_load_bird_add
welcome_handlers["kbd_sel_bird"] = ui_load_bird_sel

welcome_handlers["kbd_mode_apm1"] = ui_apm1_mode
welcome_handlers["kbd_mode_apm2"] = ui_apm2_mode
welcome_handlers["kbd_mode_apm3"] = ui_apm3_mode
welcome_handlers["kbd_mode_apm4"] = ui_apm4_mode
welcome_handlers["kbd_mode_apm5"] = ui_apm5_mode
welcome_handlers["kbd_mode_apm6"] = ui_apm6_mode
welcome_handlers["kbd_feeding"] = ui_feeding_mode
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
