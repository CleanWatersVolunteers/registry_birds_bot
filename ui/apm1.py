# Поступление

import re
from datetime import datetime

import pytz

from const import const
from database import Database as db
from storage import storage
from timetools import TimeTools

GET_TIME = lambda text: re.search(r'\d{1,2}:\d{1,2}', text)
GET_DATE = lambda text: re.search(r'\d{2}\.\d{2}\.\d{4}', text)
GET_DATETIME = lambda text: re.search(r'\d{2}\.\d{2}\.\d{4} \d{1,2}:\d{1,2}', text)
GET_NOW_TIME = lambda: datetime.utcnow().astimezone(pytz.timezone('Etc/GMT-6')).strftime(const.datetime_format)

apm1_text_place = 'Введите место отлова'
apm1_text_date = 'Введите дату и время отлова в формате ДД.ММ.ГГГГ ЧЧ:ММ'
apm1_text_time = 'Введите время отлова в формате ЧЧ:ММ'
apm1_wrong_time_input = "Ошибка, дата отлова не может быть раньше 24 часов или позже текущего времени"
apm1_text_pollution = 'Укажите степень загрязнения'

apm1_pollution_grade = {
	"apm1_pollution_0": "менее 25%",
	"apm1_pollution_1": "25%",
	"apm1_pollution_2": "50%",
	"apm1_pollution_3": "75%",
	"apm1_pollution_4": "100%",
	"entry_cancel": const.text_cancel,
}


def validate_datetime(user, date_input, time_input):
	"""
	Проверяет, соответствует ли время следующим условиям:
		1 - Текущее время не раньше, чем указанное время
		2 - Текущее время не позже 24 часов, чем указанное время
	"""
	time_now = GET_NOW_TIME()
	user_time = TimeTools.createFullDate(date_input, time_input)

	time1 = TimeTools.getDateTime(time_now)
	time2 = TimeTools.getDateTime(user_time)
	time_diff = time1 - time2

	if time1 < time2 or time_diff.days > 0:
		return (
			f'{const.text_incorrect} {user_time} \n{apm1_wrong_time_input} \n{apm1_text_date}',
			{const.text_today: "apm1_today", const.text_cancel: "entry_cancel"},
			'apm1_manual_date'
		)
	else:
		user['capture_datetime'] = user_time
		return apm1_get_pollution(user["code"])


# Проверка времени
def apm1_time_validate(msg, user):
	time = TimeTools.getTime(msg)  # '10:15'
	if not time:
		return (
			f'{const.text_incorrect} {msg}\n{apm1_text_time}',
			{const.text_cancel: "entry_cancel"},
			'apm1_time_validate'
		)
	return validate_datetime(user, user["capture_datetime"], time)


# Проверка даты и времени
def apm1_manual_data_validate(msg, user):
	date = TimeTools.getDate(msg)  # '16.01.2025'
	time = TimeTools.getTime(msg)  # '10:15'
	if not time or not date:
		return (
			f'{const.text_incorrect} {msg}\n{apm1_text_date}',
			{const.text_today: "apm1_today", const.text_cancel: "entry_cancel"},
			'apm1_manual_date'
		)
	return validate_datetime(user, date, time)


def apm1_get_place(code):
	return (
		f'{const.text_animal_number} {code}\n{apm1_text_place}',
		{const.text_cancel: "entry_cancel"},
		'apm1_place'
	)


# Ввод времени
def apm1_get_time(code):
	return (
		f'{const.text_animal_number} {code}\n{apm1_text_time}',
		{const.text_cancel: "entry_cancel"},
		'apm1_time_validate'
	)


# Ввод даты и времени полностью или сегодняшней даты
def apm1_get_date(code):
	return (
		f'{const.text_animal_number} {code}\n{apm1_text_date}',
		{const.text_today: "apm1_today", const.text_cancel: "entry_cancel"},
		'apm1_manual_date'
	)


def apm1_get_pollution(code):
	kbd = {}
	for key in apm1_pollution_grade:
		kbd[apm1_pollution_grade[key]] = key
	return (
		f'{const.text_animal_number} {code}\n{apm1_text_pollution}',
		kbd,
		'apm1_pollution'
	)


def show_result(user):
	text = f'✅ {const.text_animal_number} {user["code"]}\n'
	text += f'✅ {const.text_capture_place}: {user["place"]}\n'
	text += f'✅ {const.text_capture_time}: {user["capture_datetime"]}\n'
	text += f'✅ Степень загрязнения: {user["pollution"]}\n'
	return text, {const.text_done: "apm1_done", const.text_cancel: "entry_cancel"}, None


##################################
# Global API
##################################


def apm1_start(username, text, key=None):
	user = db.get_user(username)
	if key is None:
		animal = storage.get_animal_by_bar_code(text)
		if animal is not None:
			return (
				f'❌ Животное с номером {text} уже зарегистрировано!',
				{const.text_ok: "entry_cancel"},
				None
			)
		user["code"] = text
		# todo Кажется костыль. По крайней мере в этом АРМ: animal_id быть не может, т.к. запись появится в базе после завершения работы над животным
		user["animal_id"] = 0
		return apm1_get_place(user["code"])
	if key == 'apm1_place':
		user['place'] = text
		return apm1_get_date(user["code"])
	if key == 'apm1_date':
		user['capture_datetime'] = text  # todo incorrect for today button
		return apm1_get_pollution(user["code"])
	if key == 'apm1_manual_date':
		return apm1_manual_data_validate(text, user)
	if key == 'apm1_time_validate':
		return apm1_time_validate(text, user)
	if key == 'apm1_pollution':
		# todo Если пользователь ввел буквами, вывести ошибку и заставить нажать кнопки
		user["pollution"] = text
		return show_result(user)
	return None, None


def apm1_button(username, msg, key):
	user = db.get_user(username)
	if key == 'apm1_today':
		user['capture_datetime'] = const.today
		return apm1_get_time(user["code"])
	keys = key.split('_')
	if keys[1] == 'pollution':
		user["pollution"] = apm1_pollution_grade[key]
		text = f'{const.text_data_check}'
		text += f'✅ {const.text_animal_number} {user["code"]}\n'
		text += f'✅ {const.text_capture_place}: {user["place"]}\n'
		text += f'✅ {const.text_capture_time}: {user["capture_datetime"]}\n'
		text += f'✅ Степень загрязнения: {user["pollution"]}\n'
		return text, {const.text_done: "apm1_done", const.text_cancel: "entry_cancel"}, None

	if key == 'apm1_done':
		storage.insert_animal(code=user["code"], capture_datetime=user["capture_datetime"], place=user["place"],
							  pollution=user["pollution"])
	return None, None, None
