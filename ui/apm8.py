# Старший смены
import random

from const import const
from database import Database as db
from storage import storage
from timetools import TimeTools
from ui.gen import (
	qr_cmd_gen24,
	qr_cmd_gen48,
	qr_cmd_gen72,
	qr_cmd_old
)

apm8_text_line = '------------------------'
apm8_text_create_duty = 'Создать смену'
apm8_text_tomorrow = 'Завтра'
apm8_text_start_date = 'Выберите дату начала смены'
apm8_text_start_time = 'Введите время начала смены'
apm8_text_end_date = 'Выберите дату окончания смены'
apm8_text_end_time = 'Введите время окончания смены'
apm8_text_invalid_start_time = 'Время начала новой смены не может быть внутри существующей.'
apm8_text_invalid_end_time = 'Время окончания новой смены не может быть внутри существующей.'
apm8_wrong_start_after_end = 'Время окончания новой смены не может быть раньше времени начала или совпадать с ним'


def get_duty_info(item):
	return f'\nПароль: {item["password"]}\nНачало: {item["start_date"].strftime(const.datetime_short_format)}\nОкончание: {item["end_date"].strftime(const.datetime_short_format)}'


def get_new_duty_info(start_date, end_date):
	return f'\nНачало: {TimeTools.getDateTime(start_date).strftime(const.datetime_short_format)}\nОкончание: {TimeTools.getDateTime(end_date).strftime(const.datetime_short_format)}'


def create_duty(user, place_id):
	arm_id = storage.get_arm_id(place_id, user["location_id"])
	user['duty_arm_id'] = arm_id
	return (
		f'{user['place_name']}\n{apm8_text_start_date}',
		{
			const.text_today: "apm8_start_today",
			apm8_text_tomorrow: "apm8_start_tomorrow",
			const.text_cancel: "entry_apm7"
		},
		None
	)


def getEndDate(user):
	return (
		f'{user['place_name']}\n{apm8_text_end_date}',
		{
			const.text_today: "apm8_end_today",
			apm8_text_tomorrow: "apm8_end_tomorrow",
			const.text_cancel: "entry_apm7"
		},
		None
	)


def getStartTime(user):
	return (
		f'{user['place_name']}\n{apm8_text_start_time}',
		{const.text_cancel: "entry_apm7"},
		'apm8_start_time_validate'
	)


def getEndTime(user):
	return (
		f'{user['place_name']}\n{apm8_text_end_time}',
		{const.text_cancel: "entry_apm7"},
		'apm8_end_time_validate'
	)


def arm_info(user, place_id):
	data = storage.access_data(place_id, user['location_id'])
	if data:
		text = f'{apm8_text_line}\n'
		has_place_name = False
		for item in data:
			if not has_place_name:
				text += f'{item["name"]}\n{apm8_text_line}{get_duty_info(item)}'
				has_place_name = True
				user['place_name'] = item["name"]
			else:
				text += f'{get_duty_info(item)}'
			text += f'\n{apm8_text_line}'
		kbd = {
			apm8_text_create_duty: f'apm8_create_{place_id}',
			const.text_cancel: 'entry_apm7'
		}
		return text, kbd, None
	else:
		return (
			f'Нет данных', {
				apm8_text_create_duty: f'apm8_create_{place_id}',
				const.text_cancel: "entry_apm7"
			},
			None
		)


# Проверка времени начала смены
def apm8_start_time_validate(msg, user):
	start_time = TimeTools.getTime(msg)  # '10:15'
	if not start_time:
		return (
			f'{const.text_incorrect} {msg}\n{apm8_text_start_time}',
			{const.text_cancel: "entry_apm7"},
			'apm8_start_time_validate'
		)
	return validate_start_datetime(user, user["start_duty_date"], start_time)


# Проверка времени начала смены
def apm8_end_time_validate(msg, user):
	end_time = TimeTools.getTime(msg)  # '10:15'
	if not end_time:
		return (
			f'{const.text_incorrect} {msg}\n{apm8_text_end_time}',
			{const.text_cancel: "entry_apm7"},
			'apm8_end_time_validate'
		)
	return validate_end_datetime(user, user["end_duty_date"], end_time)


def validate_start_datetime(user, date, time):
	start_time = TimeTools.createFullDate(date, time)
	if storage.check_duty_date(user['duty_arm_id'], start_time):
		user['duty_start_date_time'] = start_time
		return getEndDate(user)
	else:
		return (
			apm8_text_invalid_start_time,
			{const.text_ok: "entry_apm7"},
			None
		)


def validate_end_datetime(user, date, time):
	end_time = TimeTools.createFullDate(date, time)
	end = TimeTools.getDateTime(end_time)
	start = TimeTools.getDateTime(user['duty_start_date_time'])
	if start >= end:
		return (
			f'{const.text_incorrect} {start.strftime(const.datetime_short_format)} -> {end.strftime(const.datetime_short_format)}\n{apm8_wrong_start_after_end}',
			{const.text_ok: "entry_apm7"},
			None
		)

	if storage.check_duty_date(user['duty_arm_id'], end_time):
		user['duty_end_date_time'] = end_time
		return check_data(user)
	else:
		return (
			apm8_text_invalid_end_time,
			{const.text_ok: "entry_apm7"},
			None
		)


def check_data(user):
	return (
		f'{user['place_name']}\n{get_new_duty_info(user['duty_start_date_time'], user['duty_end_date_time'])}\n{const.text_data_check}',
		{const.text_done: "apm8_done", const.text_cancel: "entry_apm7"},
		None
	)


def get_first_screen(user):
	kbd = {}
	text = f'/{qr_cmd_gen24} - генерация 24 новых QR-кодов\n'
	text += f'/{qr_cmd_gen48} - генерация 48 новых QR-кодов\n'
	text += f'/{qr_cmd_gen72} - генерация 72 новых QR-кодов\n'
	text += f'/{qr_cmd_old} N1,N2 - получение существующих N1,N2,.. QR-кодов\n\n'
	text += 'Рабочие смены:'
	arm_list = storage.get_arms(user['location_id'])
	if arm_list is not None:
		for arm in arm_list:
			kbd[arm["arm_name"]] = f'apm8_place_{arm["place_id"]}'
		kbd[const.text_exit] = 'entry_exit'
	return text, kbd, None


##################################
# Global API
##################################

def apm8_start(username, text, key=None):
	user = db.get_user(username)
	if key == 'apm8_start_time':
		user['duty_start_time'] = text
		return getEndDate(user)

	if key == 'apm8_start_time_validate':
		return apm8_start_time_validate(text, user)

	if key == 'apm8_end_time_validate':
		return apm8_end_time_validate(text, user)

	if key == 'apm8_end_time':
		user['duty_end_date'] = text
		return text, {const.text_done: "apm8_done", const.text_cancel: "entry_apm7"}, None


def apm8_entry(user, text, key):
	if isinstance(user, str):
		user = db.get_user(user)
	if 'place_' in key:
		return arm_info(user, key.split('_')[2])
	if 'create_' in key:
		return create_duty(user, key.split('_')[2])
	if 'apm8_start_today' in key:
		user['start_duty_date'] = const.today
		return getStartTime(user)
	if 'apm8_start_tomorrow' in key:
		user['start_duty_date'] = const.tomorrow
		return getStartTime(user)
	if 'apm8_end_today' in key:
		user['end_duty_date'] = const.today
		return getEndTime(user)
	if 'apm8_end_tomorrow' in key:
		user['end_duty_date'] = const.tomorrow
		return getEndTime(user)
	if 'apm8_done' in key:
		# random.seed(42)
		password = str(random.randint(10000, 99999))
		# todo проверить наличие такого пароля в базе и выдать другой если он существует.
		start = TimeTools.getDateTime(user['duty_start_date_time'])
		end = TimeTools.getDateTime(user['duty_end_date_time'])
		storage.create_duty(user['duty_arm_id'], start, end, password)
		user['duty_arm_id'] = ''
		user['place_name'] = ''
		user['duty_start_date_time'] = ''
		user['duty_end_date_time'] = ''
		user['duty_start_time'] = ''
		user['duty_end_date'] = ''
		user['start_duty_date'] = ''
		user['end_duty_date'] = ''
		return get_first_screen(user)
	if key == 'entry_apm7':
		return get_first_screen(user)
	return None, None, None
