# Поступление

from datetime import datetime
import pytz
import re
from database import Database as db
from storage import storage

GET_TIME = lambda text: re.search(r'\d{1,2}:\d{1,2}', text)
GET_DATE = lambda text: re.search(r'\d{2}\.\d{2}\.\d{4}', text)
GET_NOW = lambda: datetime.utcnow().astimezone(pytz.timezone('Etc/GMT-6')).strftime("%d.%m.%Y")

apm1_text_header = "Добавление птицы:"
apm1_text_place = 'Введите место отлова'
apm1_text_date = 'Введите дату и время отлова в формате ДД.ММ.ГГГГ ЧЧ:ММ'
apm1_text_time = 'Введите время отлова в формате ЧЧ:ММ'
apm1_text_pollution = 'Укажите степень загрязнения'
apm1_text_incorrect = "Неверный ввод:"
apm1_text_ok = 'OK'
apm1_text_done = 'Готово'
apm1_text_cancel = 'Отмена'
apm1_text_today = 'Сегодня'

apm1_pollution_grade = {
    "apm1_pollution_0": "менее 25%",
    "apm1_pollution_1": "25%",
    "apm1_pollution_2": "50%",
    "apm1_pollution_3": "75%",
    "apm1_pollution_4": "100%",
    "entry_cancel": apm1_text_cancel,
}


##################################
# Global API
##################################




def apm1_start(username, text, key=None):
	user = db.get_user(username)
	animal = storage.get_animal_by_bar_code(text)
	if animal is not None:
		user["animal_id"] = animal['animal_id']

	if user["animal_id"] is None:
		user["animal_id"] = db.get_animal_id(text)	
	# barcode
	if key is None:
		code = text
		if user["animal_id"] is not None:
			return (
				f'❌ Животное с номером {code} уже зарегистрировано!',
				{apm1_text_ok: "entry_cancel"},
				None
			)
		user["code"] = code
		user["animal_id"] = 0
		return apm1_get_place(code)
	if key == 'apm1_place':
		user['place'] = text
		return apm1_get_date(user["code"])
	if key == 'apm1_date':
		user['date'] = text # todo incorrect for today button
		return apm1_get_pollution(user["code"])
	if key == 'apm1_manual_date':
		return apm1_manual_data_validate(text, user)
	if key == 'apm1_today':
		user['date'] = GET_NOW()
		return apm1_get_time(text)
	if key == 'apm1_time_validate':
		return apm1_time_validate(text, user)
	if key == 'apm1_pollution':
		user["pollution"] = text
		return show_result(user)
	return None, None

def apm1_time_validate(msg, user):
	time = get_time(msg)  # '10:15'
	if not time:
		return (
			f'{apm1_text_incorrect} {msg}\n{apm1_text_time}',
			{apm1_text_cancel: "entry_cancel"},
			'apm1_time_validate'
		)
	user['date'] = f'''{user['date']} {time}'''
	return apm1_get_pollution(user["code"])

def apm1_manual_data_validate(msg, user):
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
		return (
			f'{apm1_text_incorrect} {msg}\n{apm1_text_date}',
			{apm1_text_today: "apm1_today", apm1_text_cancel: "entry_cancel"},
			'apm1_pollution'
		)
	user['date'] = f'{date} {time}'
	return apm1_get_pollution(user["code"])

def apm1_get_place(code):
	return (
        f'{apm1_text_header} {code}\n{apm1_text_place}',
        {apm1_text_cancel: "entry_cancel"},
        'apm1_place'
    )


def apm1_get_time(code):
	return (
		f'{apm1_text_header} {code}\n{apm1_text_time}',
		{apm1_text_cancel: "entry_cancel"},
		'apm1_time_validate'
	)

def apm1_get_date(code):
	return (
		f'{apm1_text_header} {code}\n{apm1_text_date}',
		{apm1_text_today: "apm1_today", apm1_text_cancel: "entry_cancel"},
		'apm1_manual_date'
	)


def apm1_get_pollution(code):
	kbd = {}
	for key in apm1_pollution_grade:
		kbd[apm1_pollution_grade[key]] = key
	return (
		f'{apm1_text_header} {code}\n{apm1_text_pollution}',
		kbd,
		'apm1_pollution'
	)

# 10.02.2025 02:43
def show_result(user):
	text = f'✅ Животное: {user["code"]}\n'
	text += f'✅ Место отлова: {user["place"]}\n'
	text += f'✅ Время отлова: {user["date"]}\n'
	text += f'✅ Степень загрязнения: {user["pollution"]}\n'
	return text, {apm1_text_done: "apm1_done", apm1_text_cancel: "entry_cancel"},None

def apm1_entry(username, msg, key):
	user = db.get_user(username)
	if key == 'apm1_today':
		user['date'] = GET_NOW()
		return apm1_get_pollution('333333333')
	keys = key.split('_')
	if keys[1] == 'pollution':
		user["pollution"] = apm1_pollution_grade[key]
		text = f'✅ Животное: {user["code"]}\n'
		text += f'✅ Место отлова: {user["place"]}\n'
		text += f'✅ Время отлова: {user["date"]}\n'
		text += f'✅ Степень загрязнения: {user["pollution"]}\n'
		return text, {apm1_text_done: "apm1_done", apm1_text_cancel: "entry_cancel"}
	if key == 'apm1_done':
		db.insert_animal(user)
	return None, None


def get_time(time):
	time = GET_TIME(time)
	if time:
		time = time[0]
	t = time.split(':')
	if int(t[0]) > 23 or int(t[1]) > 59:
		time = None
	return time
