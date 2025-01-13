import tgm
from telegram import InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, ContextTypes, filters
from storage import storage

from logs import log

template_yes = '✅ '
template_no = '❌ '

def add_hdr_item(label, value):
    text = f'{label}: '
    if value:
        text += f'{value}\n'
    else:
        text += '-\n'
    return text


def welcome_menu(username):
    user = storage.get_user(username)

    if not user:
        return "Пожалуйста войдите в систему!", None
    text = ''

    bird = None
    if user["code"]:
        bird = storage.get_bird(user["code"])

    # Check selected address
    if not user["location"]:
        text += 'Выберите локацию'
        keyboard = tgm.make_inline_keyboard(keyboard_addr_list)
        return text, keyboard
    text += f'Адрес: {user["location"]}\n'

    # Check bird in list
    if not bird:
        text += 'ДОБАВЬТЕ/ВЫБЕРИТЕ ПТИЦУ'
        return text, tgm.make_inline_keyboard(keyboard_menu_select_base)
    
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


    # Поступление
    if bird["stage0"]:
        text += template_yes
    else:
        text += template_no
    text += f'{keyboard_menu_select_mode["menu_mode_apm0"]}:\n'

    # Мойка
    if bird["stage1"]:
        text += template_yes
    else:
        text += template_no
    text += f'{keyboard_menu_select_mode["menu_mode_apm1"]}\n'

    # Первичка
    if bird["stage2"]:
        text += template_yes
    else:
        text += template_no
    text += f'{keyboard_menu_select_mode["menu_mode_apm2"]}\n'

    # Стационар
    if bird["stage3"]:
        text += template_yes
    else:
        text += template_no
    text += f'{keyboard_menu_select_mode["menu_mode_apm3"]}\n'

    # Врач
    if bird["stage4"]:
        text += template_yes
    else:
        text += template_no
    text += f'{keyboard_menu_select_mode["menu_mode_apm4"]}\n'

    # Нянька
    if bird["stage5"]:
        text += template_yes
    else:
        text += template_no
    text += f'{keyboard_menu_select_mode["menu_mode_apm5"]}\n'

    # Загон
    if bird["stage6"]:
        text += template_yes
    else:
        text += template_no
    text += f'{keyboard_menu_select_mode["menu_mode_apm6"]}'

    return text, tgm.make_inline_keyboard(keyboard_menu_select_mode)


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
    
#     text += f'Номер животного: {user["code"]}\n'

#     # Поступление
#     if bird["stage0"]:
#         text += template_yes
#         text += f'{keyboard_menu_select_mode["menu_mode_apm0"]}:\n'
#         if bird["capture_place"] and bird["capture_date"] and bird["polution"]:
#             text += f'\t\tМесто отлова: {bird["capture_place"]}\n'
#             text += f'\t\tВремя отлова: {bird["capture_date"]}\n'
#             text += f'\t\tСтепень загрязнения: {bird["polution"]}\n'
#     else:
#         text += template_no
#         text += f'{keyboard_menu_select_mode["menu_mode_apm0"]}\n'

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
#         if bird["mass"]:
#             text += f'{keyboard_menu_select_mode["menu_mode_apm3"]}:\n'
#             text += f'\t\tМасса животного: {bird["mass"]}\n'
#     else:
#         text += template_no
#         text += f'{keyboard_menu_select_mode["menu_mode_apm3"]}\n'

#     # Врач
#     if bird["stage4"]:
#         text += template_yes
#         text += f'{keyboard_menu_select_mode["menu_mode_apm4"]}:\n'
#         if bird["species"] and bird["sex"] and bird["clinic_state"]:
#             text += f'\t\tВид: {bird["species"]}\n'
#             text += f'\t\tПол: {bird["sex"]}\n'
#             text += f'\t\tКлиническое состояние: {bird["clinic_state"]}\n'
#     else:
#         text += template_no
#         text += f'{keyboard_menu_select_mode["menu_mode_apm4"]}\n'

#     # Нянька
#     if bird["stage5"]:
#         text += template_yes
#         if bird["nanny"]:
#             text += f'{keyboard_menu_select_mode["menu_mode_apm5"]}: {bird["nanny"]}\n'
#         else:
#             text += f'{keyboard_menu_select_mode["menu_mode_apm5"]}:\n'
#     else:
#         text += template_no
#         text += f'{keyboard_menu_select_mode["menu_mode_apm5"]}\n'

#     # Загон
#     if bird["stage6"]:
#         text += template_yes
#     else:
#         text += template_no
#     text += f'{keyboard_menu_select_mode["menu_mode_apm6"]}'

#     return text, tgm.make_inline_keyboard(keyboard_menu_select_mode)


keyboard_menu_select_mode = {
    "menu_mode_apm0":"Поступление (АРМ1)",
    "menu_mode_apm1":"Мойка (АРМ1)",
    "menu_mode_apm2":"Первичка (АРМ2)",
    "menu_mode_apm3":"Стационар (АРМ3)",
    "menu_mode_apm4":"Врач (АРМ4)",
    "menu_mode_apm5":"Нянька (АРМ5)",
    "menu_mode_apm6":"Загон (АРМ6)",
    # "menu_mode_apm7":"Возвращение (АРМ7)",

    "menu_mode_add_bird":"Добавить птицу",
    "menu_mode_select_bird":"Выбрать птицу",
    "menu_select_addr":"Сменить локацию",  
}
keyboard_menu_select_base = {
    "menu_mode_add_bird":"Добавить птицу",
    "menu_mode_select_bird":"Выбрать птицу",
    "menu_select_addr":"Сменить локацию",  
}
keyboard_menu_cancel ={
    "menu_cancel":"Отмена",
}
keyboard_menu_apm1 ={
    "menu_apm1_done":"Готово",
    "menu_cancel":"Отмена",
}
keyboard_menu_apm2 ={
    "menu_apm2_done":"Готово",
    "menu_cancel":"Отмена",
}
keyboard_menu_apm6 ={
    "menu_apm6_done":"Готово",
    "menu_cancel":"Отмена",
}
keyboard_addr_list = {
    "menu_addr1" : "Жемчужная",
    "menu_addr2" : "Аристей",
    "menu_addr3" : "Полярные зори",
}

keyboard_menu_nanny = {
    "menu_nanny1":"Кормление",
    "menu_nanny2":"Поение",
    "menu_nanny3":"Грелка",
    "menu_cancel":"Отмена",
}
def keyboard_menu_addr_handler(query)->(str,[]):
    user_id = query["from"]["username"]
    if query.data == 'menu_select_addr':
        storage.upd_user(user_id, "location", None)
    if query.data in keyboard_addr_list:
        storage.upd_user(user_id, "location", keyboard_addr_list[query.data])
    return welcome_menu(user_id)

def keyboard_menu_apm_handler(query)->(str,[]):
    username = query["from_user"]["username"]
    user = storage.get_user(username)
    if not user:
        log.loge(f'User {username} not found!')
        return welcome_menu(username)

    user["apm"] = keyboard_menu_select_mode[query.data]

    text = 'Ошибка!'
    keyboard = tgm.make_inline_keyboard(keyboard_menu_cancel)
    if query.data in keyboard_menu_select_mode:
        text = f'{keyboard_menu_select_mode[query.data]}:\n'
    if query.data == 'menu_mode_add_bird' or query.data == 'menu_mode_select_bird':
        text = "Введите бар-код"
    if query.data == 'menu_mode_apm0':
        text += "Введите через запятую: \nместо отлова, \nдату и время отлова, \nстепень загрязнения(1-10)"
    if query.data == 'menu_mode_apm1':
        text += "Выполните мойку животного и нажмите 'Готово'"
        keyboard = tgm.make_inline_keyboard(keyboard_menu_apm1)
    if query.data == 'menu_mode_apm2':
        text += "Выполните необходимые действия и нажмите 'Готово'"
        keyboard = tgm.make_inline_keyboard(keyboard_menu_apm2)
    if query.data == 'menu_mode_apm3':
        text += "Введите массу животного в граммах"
    if query.data == 'menu_mode_apm4':
        text += "Введите через запятую: \nвид животного, \nпол животного, \nклиническое состояние"
    if query.data == 'menu_mode_apm5':
        text += "Выберите тип операции"
        keyboard = tgm.make_inline_keyboard(keyboard_menu_nanny)
    if query.data == 'menu_mode_apm6':
        text += "Выполните необходимые действия и нажмите 'Готово'"
        keyboard = tgm.make_inline_keyboard(keyboard_menu_apm6)
    return text, keyboard

def keyboard_menu_done_handler(query):
    username = query["from_user"]["username"]
    user = storage.get_user(username)
    bird = storage.get_bird(user["code"])
    if bird:
        if query.data == "menu_apm1_done":
            bird["stage1"] = "+"
        if query.data == "menu_apm2_done":
            bird["stage2"] = "+"
        if query.data == "menu_apm6_done":
            bird["stage6"] = "+"
        if query.data.find("menu_nanny") == 0: 
            bird["stage5"] = "+"
            bird["nanny"] = keyboard_menu_nanny[query.data]
    return welcome_menu(username)

keyboard_handlers = {
    "menu_cancel":keyboard_menu_addr_handler,
    # Location
    "menu_select_addr":keyboard_menu_addr_handler,
    "menu_addr1":keyboard_menu_addr_handler,
    "menu_addr2":keyboard_menu_addr_handler,
    "menu_addr3":keyboard_menu_addr_handler,
    # Mode
    "menu_mode_add_bird":keyboard_menu_apm_handler,
    "menu_mode_select_bird":keyboard_menu_apm_handler,
    "menu_mode_apm0":keyboard_menu_apm_handler,
    "menu_mode_apm1":keyboard_menu_apm_handler,
    "menu_mode_apm2":keyboard_menu_apm_handler,
    "menu_mode_apm3":keyboard_menu_apm_handler,
    "menu_mode_apm4":keyboard_menu_apm_handler,
    "menu_mode_apm5":keyboard_menu_apm_handler,
    "menu_mode_apm6":keyboard_menu_apm_handler,
    # "menu_mode_apm7":keyboard_menu_apm_handler,

    "menu_apm1_done":keyboard_menu_done_handler,
    "menu_apm2_done":keyboard_menu_done_handler,
    "menu_apm6_done":keyboard_menu_done_handler,
    

    "menu_nanny1":keyboard_menu_done_handler,
    "menu_nanny2":keyboard_menu_done_handler,
    "menu_nanny3":keyboard_menu_done_handler,


}


async def cb_message_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update["message"]["from"]["username"]
    user = storage.get_user(user_id)

    text, keyboard = welcome_menu(user_id)

    # Entry data
    if user and user["apm"]:
        # Выбор птицы
        if user["apm"] == keyboard_menu_select_mode["menu_mode_add_bird"]:
            barcode = update.message.text
            if barcode.isdigit():
                storage.add_bird(barcode)
                log.logi(f'New bird {barcode}')
                user["code"] = barcode
                text, keyboard = welcome_menu(user_id)
            else:
                text = f'Некорректный ввод:{barcode}\nВведите бар-код'
                keyboard = tgm.make_inline_keyboard(keyboard_menu_cancel)
        if user["apm"] == keyboard_menu_select_mode["menu_mode_select_bird"]:
            barcode = update.message.text
            if barcode.isdigit():
                user["code"] = barcode
                text, keyboard = welcome_menu(user_id)
            else:
                text = f'Некорректный ввод:{barcode}\nВведите бар-код'
                keyboard = tgm.make_inline_keyboard(keyboard_menu_cancel)

        # Поступление
        if user["apm"] == keyboard_menu_select_mode["menu_mode_apm0"]:
            data = update.message.text.split(',')
            text = f'Некорректный ввод:{update.message.text}\nВведите через запятую: \nместо отлова, \nдату и время отлова, \nстепень загрязнения(1-10)'
            keyboard = tgm.make_inline_keyboard(keyboard_menu_cancel)
            if len(data) == 3:
                if data[2].isdigit():
                    storage.upd_bird(user["code"], "capture_place", data[0])
                    storage.upd_bird(user["code"], "capture_date", data[1])
                    storage.upd_bird(user["code"], "polution", data[2])
                    storage.upd_bird(user["code"], "stage0", "+")
                    text, keyboard = welcome_menu(user_id)

        # Стационар
        if user["apm"] == keyboard_menu_select_mode["menu_mode_apm3"]:
            data = update.message.text
            text = f'{keyboard_menu_select_mode["menu_mode_apm3"]}:\nНекорректный ввод:{update.message.text}\nВведите массу животного в граммах'
            keyboard = tgm.make_inline_keyboard(keyboard_menu_cancel)
            if len(data) > 0:
                storage.upd_bird(user["code"], "mass", data)
                storage.upd_bird(user["code"], "stage3", "+")
                text, keyboard = welcome_menu(user_id)

        # Врач
        if user["apm"] == keyboard_menu_select_mode["menu_mode_apm4"]:
            data = update.message.text.split(',')
            text = f'{keyboard_menu_select_mode["menu_mode_apm3"]}:\nНекорректный ввод:{update.message.text}\nВведите через запятую: \nвид животного, \nпол животного, \nклиническое состояние'
            keyboard = tgm.make_inline_keyboard(keyboard_menu_cancel)
            if len(data) == 3:
                storage.upd_bird(user["code"], "species", data[0])
                storage.upd_bird(user["code"], "sex", data[1])
                storage.upd_bird(user["code"], "clinic_state", data[2])
                storage.upd_bird(user["code"], "stage4", "+")
                text, keyboard = welcome_menu(user_id)
            
    # New user
    if not user:
        storage.add_user(user_id)
        log.logi(f'New user {user_id}')
        text, keyboard = welcome_menu(user_id)
    if keyboard:
        await update.message.reply_text(f'{text}', reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(f'{text}')

    return None

async def cb_reaction_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if query.data in keyboard_handlers.keys():
        text, keyboard = keyboard_handlers[query.data](query)
        if keyboard:
            await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.edit_message_text(text=text)
    else:
        print(f"[!!] Got unexpected argument: {query.data}")
    return


