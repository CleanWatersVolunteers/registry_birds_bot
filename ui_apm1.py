from ui_welcome import welcome_handlers, ui_welcome
from storage import storage
from datetime import datetime
import pytz
import tgm
import re

GET_TIME = lambda text: re.search(r'\d{1,2}:\d{1,2}', text)
GET_DATE = lambda text: re.search(r'\d{2}\.\d{2}\.\d{4}', text)
# GET_DATE = lambda text: re.search(r'\d{1,2}\.\d{1,2}\.\d{2,4}', text)[0]
# GET_NOW = lambda: datetime.utcnow().astimezone(pytz.timezone('Etc/GMT-6')).strftime("%d.%m.%Y %H:%M")
GET_NOW = lambda: datetime.utcnow().astimezone(pytz.timezone('Etc/GMT-6')).strftime("%d.%m.%Y")

apm1_text_header = "Добавление птицы:"
apm1_text_enter_place = "Введите место отлова"
apm1_text_enter_date = "Введите дату и время отлова в формате ДД.ММ.ГГГГ ЧЧ:ММ"
apm1_text_enter_time = "Введите время отлова в формате ЧЧ:ММ"
apm1_text_enter_polituon = "Укажите степень загрязнения"
apm1_text_incorrect = "Неверный ввод:"

cancel_button_label = "Отмена"

apm1_date = {
    "kbd_mode_apm1_date_now": "Сегодня",
    "kbd_cancel": cancel_button_label,
}
apm1_cancel = {
    "kbd_cancel": cancel_button_label,
}

apm1_cancel_barcode_input = {
    "kbd_back_to_load_barcode": cancel_button_label,
}

apm1_pollution_grade = {
    "pollution_grade_0": "менее 25%",
    "pollution_grade_1": "25%",
    "pollution_grade_2": "50%",
    "pollution_grade_3": "75%",
    "pollution_grade_4": "100%",
}


def apm1_place_hndl(user, key=None, msg=None) -> (str,):
    user["bird"]["place_capture"] = msg
    user["mode"] = "kbd_mode_apm1_date"
    text = f'{apm1_text_header} {user["bird"]["bar_code"]}\n{apm1_text_enter_date}'
    keyboard = tgm.make_inline_keyboard(apm1_date)
    return text, keyboard


# date from button entry
def apm1_date_now_hndl(user, key=None, msg=None) -> (str,):
    user["bird"]["capture_datetime"] = GET_NOW()  # '17.01.2025'
    user["mode"] = "kbd_mode_apm1_time"
    text = f'{apm1_text_header} {user["bird"]["bar_code"]}\n{apm1_text_enter_time}'
    keyboard = tgm.make_inline_keyboard(apm1_cancel)
    return text, keyboard


def get_time(time):
    time = GET_TIME(time)
    if time:
        time = time[0]
    t = time.split(':')
    if int(t[0]) > 23 or int(t[1]) > 59:
        time = None
    return time


# time from manualy entry
def apm1_time_now_hndl(user, key=None, msg=None) -> (str,):
    time = get_time(msg)  # '10:15'
    if not time:
        text = f'{apm1_text_header} {user["bird"]["bar_code"]}\n{apm1_text_incorrect} {msg}\n'
        text += apm1_text_enter_time
        keyboard = tgm.make_inline_keyboard(apm1_cancel)
        return text, keyboard
    user["bird"]["capture_datetime"] += f' {time}'
    return apm1_pollution_mode(user)


def apm1_pollution_mode(user):
    user["mode"] = "kbd_mode_apm1_pollution"
    text = f'{apm1_text_header} {user["bird"]["bar_code"]}\n{apm1_text_enter_polituon}'
    keyboard = tgm.make_inline_keyboard(apm1_pollution_grade)
    for key, value in apm1_pollution_grade.items():
        welcome_handlers[f"{key}"] = apm1_pollution_hndl
    return text, keyboard


# Full manualy entry
def apm1_date_hndl(user, key=None, msg=None) -> (str,):
    date = GET_DATE(msg)  # '16.01.2025'
    now = GET_NOW()  # '17.01.2025'
    time = get_time(msg)  # '10:15'
    if date:
        date = date[0]
        d = date.split('.')  # ['16', '01', '2025']
        n = now.split('.')  # ['17', '01', '2025']
        if n[2] != d[2] or n[1] != d[1] or int(d[0]) < (int(n[0]) - 1) or int(d[0]) > int(n[0]):
            date = None
    if not time or not date:
        text = f'{apm1_text_header} {user["bird"]["bar_code"]}\n{apm1_text_incorrect} {msg}\n'
        text += apm1_text_enter_date
        keyboard = tgm.make_inline_keyboard(apm1_date)
        return text, keyboard
    user["bird"]["capture_datetime"] = f'{date} {time}'
    return apm1_pollution_mode(user)


def apm1_pollution_hndl(user, key=None, msg=None) -> (str,):
    user["bird"]["degree_pollution"] = apm1_pollution_grade[key]
    storage.insert_animal(user["bird"])
    return ui_welcome(user)


############################################
# Global API
############################################
def ui_apm1_mode(user, key=None, msg=None) -> (str,):
    user["mode"] = "kbd_mode_apm1_place"
    text = f'{apm1_text_header} {user["bird"]["bar_code"]}\n{apm1_text_enter_place}'
    keyboard = tgm.make_inline_keyboard(apm1_cancel_barcode_input)
    return text, keyboard


welcome_handlers["kbd_mode_apm1_place"] = apm1_place_hndl

welcome_handlers["kbd_mode_apm1_date"] = apm1_date_hndl
welcome_handlers["kbd_mode_apm1_date_now"] = apm1_date_now_hndl
welcome_handlers["kbd_mode_apm1_time"] = apm1_time_now_hndl
welcome_handlers["kbd_mode_apm1_pollution"] = apm1_pollution_hndl