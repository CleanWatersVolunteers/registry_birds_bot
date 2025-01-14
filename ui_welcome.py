import tgm
from telegram import InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, ContextTypes, filters
from storage import storage
from barcode_reader import barCodeReader

welcome_text_sel_addr = 'Выберите локацию'
welcome_text_sel_bird = 'Добавьте/Выберите птицу'


ui_welcome_mode = {
    "kbd_mode_apm0":"Поступление (АРМ1)",
    "kbd_mode_apm1":"Мойка (АРМ1)",
    "kbd_mode_apm2":"Первичка (АРМ2)",
    "kbd_mode_apm3":"Стационар (АРМ3)",
    "kbd_mode_apm4":"Врач (АРМ4)",
    "kbd_mode_apm5":"Нянька (АРМ5)",
    "kbd_mode_apm6":"Загон (АРМ6)",
    "kbd_add_bird":"Добавить птицу",
    "kbd_sel_bird":"Выбрать птицу",
    "kbd_sel_addr":"Сменить локацию", 
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

    user["mode"] = None

    # # Поступление
    # if bird["stage0"]:
    #     text += template_yes
    # else:
    #     text += template_no
    # text += f'{keyboard_menu_select_mode["menu_mode_apm0"]}:\n'

    # # Мойка
    # if bird["stage1"]:
    #     text += template_yes
    # else:
    #     text += template_no
    # text += f'{keyboard_menu_select_mode["menu_mode_apm1"]}\n'

    # # Первичка
    # if bird["stage2"]:
    #     text += template_yes
    # else:
    #     text += template_no
    # text += f'{keyboard_menu_select_mode["menu_mode_apm2"]}\n'

    # # Стационар
    # if bird["stage3"]:
    #     text += template_yes
    # else:
    #     text += template_no
    # text += f'{keyboard_menu_select_mode["menu_mode_apm3"]}\n'

    # # Врач
    # if bird["stage4"]:
    #     text += template_yes
    # else:
    #     text += template_no
    # text += f'{keyboard_menu_select_mode["menu_mode_apm4"]}\n'

    # # Нянька
    # if bird["stage5"]:
    #     text += template_yes
    # else:
    #     text += template_no
    # text += f'{keyboard_menu_select_mode["menu_mode_apm5"]}\n'

    # # Загон
    # if bird["stage6"]:
    #     text += template_yes
    # else:
    #     text += template_no
    # text += f'{keyboard_menu_select_mode["menu_mode_apm6"]}'

    # return text, tgm.make_inline_keyboard(keyboard_menu_select_mode)
    return text, tgm.make_inline_keyboard(kbd_menu_base)

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

from ui_apm0 import *


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
            text, keyboard = apm0_entry(user, msg=code[0])
        else:
            text, keyboard = apm0_entry(user, msg='')
    await update.message.reply_text(f'{text}', reply_markup=InlineKeyboardMarkup(keyboard))
    return None






# template_yes = '✅ '
# template_no = '❌ '

# def add_hdr_item(label, value):
#     text = f'{label}: '
#     if value:
#         text += f'{value}\n'
#     else:
#         text += '-\n'
#     return text


# def welcome_menu(username):
#     user = storage.get_user(username)

#     if not user:
#         return "Пожалуйста войдите в систему!", None
#     text = ''

#     bird = None
#     if user["code"]:
#         bird = storage.get_bird(user["code"])

#     # Check selected address
#     if not user["location"]:
#         text += 'Выберите локацию'
#         keyboard = tgm.make_inline_keyboard(keyboard_addr_list)
#         return text, keyboard
#     text += f'Адрес: {user["location"]}\n'

#     # Check bird in list
#     if not bird:
#         text += 'ДОБАВЬТЕ/ВЫБЕРИТЕ ПТИЦУ'
#         return text, tgm.make_inline_keyboard(keyboard_menu_select_base)
    
#     text += add_hdr_item("Номер животного", user["code"])
#     text += add_hdr_item("Место отлова", bird["capture_place"])
#     text += add_hdr_item("Время отлова", bird["capture_date"])
#     text += add_hdr_item("Степень загрязнения", bird["polution"])
#     if bird["mass"]:
#         text += add_hdr_item("Масса животного", bird["mass"] + "гр.")
#     else:
#         text += add_hdr_item("Масса животного", None)
#     text += add_hdr_item("Вид", bird["species"])
#     text += add_hdr_item("Пол", bird["sex"])
#     text += add_hdr_item("Клиническое состояние", bird["clinic_state"])


#     # Поступление
#     if bird["stage0"]:
#         text += template_yes
#     else:
#         text += template_no
#     text += f'{keyboard_menu_select_mode["menu_mode_apm0"]}:\n'

#     # Мойка
#     if bird["stage1"]:
#         text += template_yes
#     else:
#         text += template_no
#     text += f'{keyboard_menu_select_mode["menu_mode_apm1"]}\n'

#     # Первичка
#     if bird["stage2"]:
#         text += template_yes
#     else:
#         text += template_no
#     text += f'{keyboard_menu_select_mode["menu_mode_apm2"]}\n'

#     # Стационар
#     if bird["stage3"]:
#         text += template_yes
#     else:
#         text += template_no
#     text += f'{keyboard_menu_select_mode["menu_mode_apm3"]}\n'

#     # Врач
#     if bird["stage4"]:
#         text += template_yes
#     else:
#         text += template_no
#     text += f'{keyboard_menu_select_mode["menu_mode_apm4"]}\n'

#     # Нянька
#     if bird["stage5"]:
#         text += template_yes
#     else:
#         text += template_no
#     text += f'{keyboard_menu_select_mode["menu_mode_apm5"]}\n'

#     # Загон
#     if bird["stage6"]:
#         text += template_yes
#     else:
#         text += template_no
#     text += f'{keyboard_menu_select_mode["menu_mode_apm6"]}'

#     return text, tgm.make_inline_keyboard(keyboard_menu_select_mode)


# keyboard_menu_select_mode = {
#     "menu_mode_apm0":"Поступление (АРМ1)",
#     "menu_mode_apm1":"Мойка (АРМ1)",
#     "menu_mode_apm2":"Первичка (АРМ2)",
#     "menu_mode_apm3":"Стационар (АРМ3)",
#     "menu_mode_apm4":"Врач (АРМ4)",
#     "menu_mode_apm5":"Нянька (АРМ5)",
#     "menu_mode_apm6":"Загон (АРМ6)",
#     # "menu_mode_apm7":"Возвращение (АРМ7)",

#     "menu_mode_add_bird":"Добавить птицу",
#     "menu_mode_select_bird":"Выбрать птицу",
#     "menu_select_addr":"Сменить локацию",  
# }
# keyboard_menu_select_base = {
#     "menu_mode_add_bird":"Добавить птицу",
#     "menu_mode_select_bird":"Выбрать птицу",
#     "menu_select_addr":"Сменить локацию",  
# }
# keyboard_menu_cancel ={
#     "menu_cancel":"Отмена",
# }
# keyboard_menu_apm1 ={
#     "menu_apm1_done":"Готово",
#     "menu_cancel":"Отмена",
# }
# keyboard_menu_apm2 ={
#     "menu_apm2_done":"Готово",
#     "menu_cancel":"Отмена",
# }
# keyboard_menu_apm6 ={
#     "menu_apm6_done":"Готово",
#     "menu_cancel":"Отмена",
# }
# keyboard_addr_list = {
#     "menu_addr1" : "Жемчужная",
#     "menu_addr2" : "Аристей",
#     "menu_addr3" : "Полярные зори",
# }

# keyboard_menu_sex ={
#     "menu_male":"муж",
#     "menu_female":"жен",
#     "menu_cancel":"Отмена",
# }

# keyboard_menu_nanny = {
#     "menu_nanny1":"Кормление",
#     "menu_nanny2":"Поение",
#     "menu_nanny3":"Грелка",
#     "menu_cancel":"Отмена",
# }
# def keyboard_menu_addr_handler(query)->(str,[]):
#     user_id = query["from"]["username"]
#     if query.data == 'menu_select_addr':
#         storage.upd_user(user_id, "location", None)
#     if query.data in keyboard_addr_list:
#         storage.upd_user(user_id, "location", keyboard_addr_list[query.data])
#     return welcome_menu(user_id)

# def keyboard_menu_apm_handler(query)->(str,[]):
#     username = query["from_user"]["username"]
#     user = storage.get_user(username)
#     if not user:
#         log.loge(f'User {username} not found!')
#         return welcome_menu(username)

#     user["apm"] = keyboard_menu_select_mode[query.data]

#     text = 'Ошибка!'
#     keyboard = tgm.make_inline_keyboard(keyboard_menu_cancel)
#     if query.data in keyboard_menu_select_mode:
#         text = f'{keyboard_menu_select_mode[query.data]}:\n'
#     if query.data == 'menu_mode_add_bird' or query.data == 'menu_mode_select_bird':
#         text = "Введите бар-код"
#     if query.data == 'menu_mode_apm0':
#         text += "Введите через запятую: \nместо отлова, \nдату и время отлова, \nстепень загрязнения(1-10)"
#     if query.data == 'menu_mode_apm1':
#         text += "Выполните мойку животного и нажмите 'Готово'"
#         keyboard = tgm.make_inline_keyboard(keyboard_menu_apm1)
#     if query.data == 'menu_mode_apm2':
#         text += "Выполните необходимые действия и нажмите 'Готово'"
#         keyboard = tgm.make_inline_keyboard(keyboard_menu_apm2)
#     if query.data == 'menu_mode_apm3':
#         text += "Введите массу животного в граммах"
#     if query.data == 'menu_mode_apm4':
#         # text += "Введите через запятую: \nвид животного, \nпол животного, \nклиническое состояние"
#         text += "Введите через запятую: \nвид животного, \nклиническое состояние"
#     if query.data == 'menu_mode_apm5':
#         text += "Выберите тип операции"
#         keyboard = tgm.make_inline_keyboard(keyboard_menu_nanny)
#     if query.data == 'menu_mode_apm6':
#         text += "Выполните необходимые действия и нажмите 'Готово'"
#         keyboard = tgm.make_inline_keyboard(keyboard_menu_apm6)
#     return text, keyboard

# def keyboard_menu_done_handler(query):
#     username = query["from_user"]["username"]
#     user = storage.get_user(username)
#     bird = storage.get_bird(user["code"])
#     if bird:
#         if query.data == "menu_apm1_done":
#             bird["stage1"] = "+"
#         if query.data == "menu_apm2_done":
#             bird["stage2"] = "+"
#         if query.data == "menu_apm6_done":
#             bird["stage6"] = "+"
#         if query.data.find("menu_nanny") == 0: 
#             bird["stage5"] = "+"
#             bird["nanny"] = keyboard_menu_nanny[query.data]
#     return welcome_menu(username)

# def keyboard_menu_sex_handler(query):
#     username = query["from_user"]["username"]
#     user = storage.get_user(username)
#     if not user:
#         return welcome_menu(username)    
#     bird = storage.get_bird(user["code"])
#     if bird:
#         bird["sex"] = keyboard_menu_sex[query.data]
#         storage.upd_bird(user["code"], "stage4", "+")

#     return welcome_menu(username)

# keyboard_handlers = {
#     "menu_cancel":keyboard_menu_addr_handler,
#     # Location
#     "menu_select_addr":keyboard_menu_addr_handler,
#     "menu_addr1":keyboard_menu_addr_handler,
#     "menu_addr2":keyboard_menu_addr_handler,
#     "menu_addr3":keyboard_menu_addr_handler,
#     # Mode
#     "menu_mode_add_bird":keyboard_menu_apm_handler,
#     "menu_mode_select_bird":keyboard_menu_apm_handler,
#     "menu_mode_apm0":keyboard_menu_apm_handler,
#     "menu_mode_apm1":keyboard_menu_apm_handler,
#     "menu_mode_apm2":keyboard_menu_apm_handler,
#     "menu_mode_apm3":keyboard_menu_apm_handler,
#     "menu_mode_apm4":keyboard_menu_apm_handler,
#     "menu_mode_apm5":keyboard_menu_apm_handler,
#     "menu_mode_apm6":keyboard_menu_apm_handler,
#     # "menu_mode_apm7":keyboard_menu_apm_handler,

#     "menu_apm1_done":keyboard_menu_done_handler,
#     "menu_apm2_done":keyboard_menu_done_handler,
#     "menu_apm6_done":keyboard_menu_done_handler,
    
#     "menu_male":keyboard_menu_sex_handler,
#     "menu_female":keyboard_menu_sex_handler,

#     "menu_nanny1":keyboard_menu_done_handler,
#     "menu_nanny2":keyboard_menu_done_handler,
#     "menu_nanny3":keyboard_menu_done_handler,
# }

# from barcode_reader import barCodeReader

# async def cb_message_barcode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     file_id = update.message.photo[0].file_id
#     new_file = await update.message.effective_attachment[-1].get_file()
#     file_name = new_file.file_path.split('/')[-1]
#     await new_file.download_to_drive()
#     code = barCodeReader(file_name)
 
#     if len(code) == 1:
#         print(f'[..] barcode: {code[0]}')
#         keyboard = tgm.make_inline_keyboard(keyboard_menu_cancel)
#         await update.message.reply_text(f'Получен баркод: {code[0]}', reply_markup=InlineKeyboardMarkup(keyboard))
#         # await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))
#     else:
#         print(f'[!!] barcode error: {code}')
#         keyboard = tgm.make_inline_keyboard(keyboard_menu_cancel)
#         await update.message.reply_text(f'Неправильный ввод!', reply_markup=InlineKeyboardMarkup(keyboard))


# async def cb_message_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     user_id = update["message"]["from"]["username"]
#     user = storage.get_user(user_id)

#     text, keyboard = welcome_menu(user_id)

#     # Entry data
#     if user and user["apm"]:
#         # Выбор птицы
#         if user["apm"] == keyboard_menu_select_mode["menu_mode_add_bird"]:
#             barcode = update.message.text
#             if barcode.isdigit():
#                 storage.add_bird(barcode)
#                 log.logi(f'New bird {barcode}')
#                 user["code"] = barcode
#                 text, keyboard = welcome_menu(user_id)
#             else:
#                 text = f'Некорректный ввод:{barcode}\nВведите бар-код'
#                 keyboard = tgm.make_inline_keyboard(keyboard_menu_cancel)
#         if user["apm"] == keyboard_menu_select_mode["menu_mode_select_bird"]:
#             barcode = update.message.text
#             if barcode.isdigit():
#                 user["code"] = barcode
#                 text, keyboard = welcome_menu(user_id)
#             else:
#                 text = f'Некорректный ввод:{barcode}\nВведите бар-код'
#                 keyboard = tgm.make_inline_keyboard(keyboard_menu_cancel)

#         # Поступление
#         if user["apm"] == keyboard_menu_select_mode["menu_mode_apm0"]:
#             data = update.message.text.split(',')
#             text = f'Некорректный ввод:{update.message.text}\nВведите через запятую: \nместо отлова, \nдату и время отлова, \nстепень загрязнения(1-10)'
#             keyboard = tgm.make_inline_keyboard(keyboard_menu_cancel)
#             if len(data) == 3:
#                 if data[2].isdigit():
#                     storage.upd_bird(user["code"], "capture_place", data[0])
#                     storage.upd_bird(user["code"], "capture_date", data[1])
#                     storage.upd_bird(user["code"], "polution", data[2])
#                     storage.upd_bird(user["code"], "stage0", "+")
#                     text, keyboard = welcome_menu(user_id)

#         # Стационар
#         if user["apm"] == keyboard_menu_select_mode["menu_mode_apm3"]:
#             data = update.message.text
#             text = f'{keyboard_menu_select_mode["menu_mode_apm3"]}:\nНекорректный ввод:{update.message.text}\nВведите массу животного в граммах'
#             keyboard = tgm.make_inline_keyboard(keyboard_menu_cancel)
#             if len(data) > 0 and data.isdigit():
#                 storage.upd_bird(user["code"], "mass", data)
#                 storage.upd_bird(user["code"], "stage3", "+")
#                 text, keyboard = welcome_menu(user_id)

#         # Врач
#         if user["apm"] == keyboard_menu_select_mode["menu_mode_apm4"]:
#             data = update.message.text.split(',')
#             text = f'{keyboard_menu_select_mode["menu_mode_apm3"]}:\nНекорректный ввод:{update.message.text}\nВведите через запятую: \nвид животного, \nклиническое состояние'
#             keyboard = tgm.make_inline_keyboard(keyboard_menu_cancel)
#             if len(data) == 2:
#                 storage.upd_bird(user["code"], "species", data[0])
#                 # storage.upd_bird(user["code"], "sex", data[1])
#                 storage.upd_bird(user["code"], "clinic_state", data[1])
#                 text = f'{keyboard_menu_select_mode["menu_mode_apm3"]}:\n Выберите пол животного'
#                 keyboard = tgm.make_inline_keyboard(keyboard_menu_sex)
#                 # text, keyboard = welcome_menu(user_id)
            
#     # New user
#     if not user:
#         storage.add_user(user_id)
#         log.logi(f'New user {user_id}')
#         text, keyboard = welcome_menu(user_id)
#     if keyboard:
#         await update.message.reply_text(f'{text}', reply_markup=InlineKeyboardMarkup(keyboard))
#     else:
#         await update.message.reply_text(f'{text}')

#     return None

# async def cb_reaction_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     query = update.callback_query
#     await query.answer()
#     if query.data in keyboard_handlers.keys():
#         text, keyboard = keyboard_handlers[query.data](query)
#         if keyboard:
#             await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))
#         else:
#             await query.edit_message_text(text=text)
#     else:
#         print(f"[!!] Got unexpected argument: {query.data}")
#     return


