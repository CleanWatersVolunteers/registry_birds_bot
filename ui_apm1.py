from ui_welcome import welcome_handlers,ui_welcome_mode,ui_welcome_cancel,ui_welcome_done,ui_welcome
from storage import storage
from datetime import datetime
import pytz
import tgm
import re

GET_TIME = lambda text: re.search(r'\d{1,2}:\d{1,2}', text)[0]
GET_DATE = lambda text: re.search(r'\d{2}\.\d{2}\.\d{4}', text)[0]
# GET_DATE = lambda text: re.search(r'\d{1,2}\.\d{1,2}\.\d{2,4}', text)[0]
GET_NOW = lambda: datetime.utcnow().astimezone(pytz.timezone('Etc/GMT-6')).strftime("%d.%m.%Y %H:%M")

apm1_text_enter_place = "Введите место отлова"
apm1_text_enter_date = "Введите время отлова в формате ДД.ММ.ГГГГ ЧЧ:ММ"
apm1_text_enter_polituon = "Введите степень загрязнения(1-10)"
apm1_text_incorrect = "Неверный ввод:"

apm1_date = {
    "kbd_date_now":"Сегодня",
    "kbd_cancel":"Отмена",
}
apm1_cancel = {
    "kbd_cancel":"Отмена",
}

def apm1_place_hndl(user, key=None, msg=None)->(str,):
    bird = storage.get_bird(user["code"])
    if not bird:
        user["mode"] = None
        return ui_welcome(user)

    bird["capture_place"] = msg
    user["mode"] = "kbd_mode_apm1_date"
    text = f'{ui_welcome_mode["kbd_mode_apm1"]}:\n{apm1_text_enter_date}'
    keyboard = tgm.make_inline_keyboard(apm1_date)

    return text, keyboard

def apm1_date_now_hndl(user, key=None, msg=None)->(str,):
    bird = storage.get_bird(user["code"])
    if not bird:
        user["mode"] = None
        return ui_welcome(user)
    bird["capture_date"] = GET_NOW()             # '17.01.2025 14:20'
    user["mode"] = "kbd_mode_apm1_polution"
    text = f'{ui_welcome_mode["kbd_mode_apm1"]}:\n{apm1_text_enter_polituon}'
    keyboard = tgm.make_inline_keyboard(apm1_cancel)
    return text, keyboard

def apm1_date_hndl(user, key=None, msg=None)->(str,):
    bird = storage.get_bird(user["code"])
    if not bird:
        user["mode"] = None
        return ui_welcome(user)

    time = GET_TIME(msg)        # '10:15'
    date = GET_DATE(msg)        # '16.01.2025'
    now = GET_NOW()             # '17.01.2025 14:20'
    if date:
        d = date.split('.')     # ['16', '01', '2025']
        n = now.split(' ')      # ['17.01.2025', '14:20']
        n = n[0].split('.')     # ['17', '01', '2025']
        if n[2] != d[2] or n[1] != d[1]:  # compare month and year
            date = None
        else:
            if int(d[0]) < (int(n[0])-1):    # compare day
                date = None
    if not time or not date:
        text = f'{ui_welcome_mode["kbd_mode_apm1"]}:\n{apm1_text_incorrect} {msg}\n'
        text += apm1_text_enter_date
        keyboard = tgm.make_inline_keyboard(apm1_date) 
        return text, keyboard
    bird["capture_date"] = f'{date} {time}'
    user["mode"] = "kbd_mode_apm1_polution"
    text = f'{ui_welcome_mode["kbd_mode_apm1"]}:\n{apm1_text_enter_polituon}'
    keyboard = tgm.make_inline_keyboard(apm1_cancel)
    return text, keyboard

def apm1_polution_hndl(user, key=None, msg=None)->(str,):
    bird = storage.get_bird(user["code"])
    if not bird:
        user["mode"] = None
        return ui_welcome(user)

    if not msg.isdigit():
        text = f'{ui_welcome_mode["kbd_mode_apm1"]}:\n{apm1_text_incorrect} {msg}\n'
        text += apm1_text_enter_polituon
        keyboard = tgm.make_inline_keyboard(apm1_cancel)
        return text, keyboard
    if int(msg) < 1 or int(msg) > 10:
        text = f'{ui_welcome_mode["kbd_mode_apm1"]}:\n{apm1_text_incorrect} {msg}\n'
        text += apm1_text_enter_polituon
        keyboard = tgm.make_inline_keyboard(apm1_cancel)
        return text, keyboard

    bird["polution"] = msg
    bird["stage1"] = 'OK'
    return ui_welcome(user)


############################################
# Global API
############################################
def ui_apm1_mode(user, key=None, msg=None)->(str,):
    if not storage.get_bird(user["code"]):
        return ui_welcome(user)
    user["mode"] = "kbd_mode_apm1_place"
    text = f'{ui_welcome_mode["kbd_mode_apm1"]}:\n{apm1_text_enter_place}'
    keyboard = tgm.make_inline_keyboard(apm1_cancel)
    return text, keyboard

welcome_handlers["kbd_mode_apm1_place"] = apm1_place_hndl
welcome_handlers["kbd_mode_apm1_date"] = apm1_date_hndl
welcome_handlers["kbd_date_now"] = apm1_date_now_hndl
welcome_handlers["kbd_mode_apm1_polution"] = apm1_polution_hndl