from typing import Optional
from ui_welcome import welcome_handlers, ui_welcome
from storage import storage
from datetime import datetime
import pytz
import tgm
import re

GET_TIME = lambda text: re.search(r'\d{1,2}:\d{1,2}', text)
GET_DATE = lambda text: re.search(r'\d{2}\.\d{2}\.\d{4}', text)
GET_DATETIME = lambda text: re.search(r'\d{2}\.\d{2}\.\d{4} \d{1,2}:\d{1,2}', text)
GET_NOW_TIME = lambda: datetime.utcnow().astimezone(pytz.timezone('Etc/GMT-6')).strftime("%d.%m.%Y %H:%M")
GET_NOW = lambda: datetime.utcnow().astimezone(pytz.timezone('Etc/GMT-6')).strftime("%d.%m.%Y")

apm1_text_header = "Добавление птицы:"
apm1_text_enter_place = "Введите место отлова"
apm1_text_enter_date = "Введите дату и время отлова в формате ДД.ММ.ГГГГ ЧЧ:ММ"
apm1_text_enter_time = "Введите время отлова в формате ЧЧ:ММ"
apm1_wrong_time_input = "Ошибка, дата отлова не может быть раньше 24 часов или позже текущего времени"
apm1_text_enter_polituon = "Укажите степень загрязнения"
apm1_text_incorrect = "Неверный ввод:"

cancel_button_label = "Отмена"

apm1_date = {
    "kbd_mode_apm1_date_now": "Сегодня",
    "kbd_cancel": cancel_button_label,
}

apm1_cancel_barcode_input = {
    "kbd_back_to_load_barcode": cancel_button_label,
}

apm1_cancel_datetime_input = {
    "kbd_mode_apm1_place": cancel_button_label,
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
    keyboard = tgm.make_inline_keyboard(apm1_cancel_datetime_input)
    return text, keyboard

def is_valid_datetime(date_str, date_format="%d.%m.%Y"):
    """Проверяет, существует ли указанная дата в календаре."""
    try:
        datetime.strptime(date_str, date_format)
        return True
    except ValueError:
        return False
    
def get_time(time) -> str | None:
    time = GET_TIME(time)
    if time:
        time = time[0]
        if not is_valid_datetime(time, '%H:%M'):
            return None
    return time

def get_date(date: str) -> str | None:
    date = GET_DATE(date)
    if date:
        date = date[0]
        if not is_valid_datetime(date, '%d.%m.%Y'): 
            return None
    return date

def generate_time_error_message(msg: str) -> tuple[str,]:
    text = f'{apm1_text_header} {msg}'
    text += apm1_text_enter_time
    keyboard = tgm.make_inline_keyboard(apm1_cancel_datetime_input)
    return text, keyboard

def validate_datetime(user: dict[str, str]) -> Optional[tuple[str,]]:
    """
    Проверяет, соответствует ли время следующим условиям:
        1 - Текущее время не раньше, чем указанное время
        2 - Текущее время не позже 24 часов, чем указанное время
    """
    time_input = user["bird"]["capture_datetime"]
    time_now = GET_NOW_TIME()
    user_time = GET_DATETIME(time_input).string
    
    # Преобразуем строки в формат datetime
    time1 = datetime.strptime(time_now, "%d.%m.%Y %H:%M")
    time2 = datetime.strptime(user_time, "%d.%m.%Y %H:%M")
    time_diff = time1 - time2
    
    if  time1 < time2 or time_diff.days > 0:
        msg = f'{user["bird"]["bar_code"]}\n{apm1_wrong_time_input}.\nТекущее время: {time_now}.\nВведённое время: {user_time}\n'
        text, keyboard = generate_time_error_message(msg)
        
        # оставляем только дату
        user["bird"]["capture_datetime"] = GET_DATE(time_input)[0]
        return text, keyboard

# time from manualy entry
def apm1_time_now_hndl(user, key=None, msg=None) -> (str,):
    time = get_time(msg)  # '10:15'
    if not time:
        current_msg = f'{user["bird"]["bar_code"]}\n{apm1_text_incorrect} {msg}\n'
        return generate_time_error_message(current_msg)
    
    user["bird"]["capture_datetime"] += f' {time}'
    
    validation = validate_datetime(user)
    return apm1_pollution_mode(user) if validation is None else validation


def apm1_pollution_mode(user):
    user["mode"] = "kbd_mode_apm1_pollution"
    text = f'{apm1_text_header} {user["bird"]["bar_code"]}\n{apm1_text_enter_polituon}'
    keyboard = tgm.make_inline_keyboard(apm1_pollution_grade)
    for key, value in apm1_pollution_grade.items():
        welcome_handlers[f"{key}"] = apm1_pollution_hndl
    return text, keyboard


# Full manualy entry
def apm1_date_hndl(user, key=None, msg=None) -> (str,):
    date = get_date(msg)  # '16.01.2025'
    time = get_time(msg)  # '10:15'

    if not time or not date:
        text = f'{apm1_text_header} {user["bird"]["bar_code"]}\n{apm1_text_incorrect} {msg}\n'
        text += apm1_text_enter_date
        keyboard = tgm.make_inline_keyboard(apm1_date)
        return text, keyboard
    user["bird"]["capture_datetime"] = f'{date} {time}'
    validation = validate_datetime(user)
    return apm1_pollution_mode(user) if validation is None else validation


def apm1_pollution_hndl(user, key=None, msg=None) -> (str,):
    user["bird"]["degree_pollution"] = apm1_pollution_grade[key]
    user["bird"]["animal_id"] = storage.insert_animal(user["bird"])
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
