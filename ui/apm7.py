# Старший смены
import random

from const import const
from database import Database as db
from logs import my_logger
from storage import storage
from timetools import TimeTools
from ui.gen import (
	qr_cmd_gen24,
	qr_cmd_gen48,
	qr_cmd_gen72,
	qr_cmd_old
)

apm7_text_create_duty = 'Создать смену'
apm7_text_tomorrow = 'Завтра'
apm7_text_start_date = 'Выберите дату начала'
apm7_text_start_time = 'Введите время начала'
apm7_text_end_date = 'Выберите дату окончания'
apm7_text_end_time = 'Введите время окончания'
apm7_text_invalid_start_time = 'Время начала новой смены не может быть внутри существующей.'
apm7_text_invalid_end_time = 'Время окончания новой смены не может быть внутри существующей.'
apm7_wrong_start_after_end = 'Время окончания новой смены не может быть раньше времени начала или совпадать с ним'
apm7_text_duty_title = 'Смена № {number}'
apm7_text_delete_duty = 'Удалить смену № {number}'
apm7_text_no_duty = 'Нет смен'
apm7_text_create_duty_title = 'Создание смены:'
apm7_text_delete_duty_confirmation = '❓ Действительно удалить смену:'


def get_duty_info(item, duty_number):
	return f'\n{apm7_text_duty_title.format(number=duty_number)}\nПароль: {item["password"]}\nНачало: {item["start_date"].strftime(const.datetime_short_format)}\nОкончание: {item["end_date"].strftime(const.datetime_short_format)}'


def get_new_duty_info(start_date, end_date):
	return f'\nНачало: {TimeTools.getDateTime(start_date).strftime(const.datetime_short_format)}\nОкончание: {TimeTools.getDateTime(end_date).strftime(const.datetime_short_format)}'


def delete_duty_confirmation(user, access_id):
	return (
		f'{apm7_text_delete_duty_confirmation} {user['place_name']}',
		{f'{const.text_ok}': f'apm7_delete_{access_id}', f'{const.text_cancel}': "entry_apm7"},
		None
	)


def delete_duty(user, access_id):
	storage.delete_duty(access_id)
	return get_first_screen(user)


def create_duty(user, place_id):
	user['duty_arm_id'] = storage.get_arm_id(place_id, user["location_id"])
	user['place_name'] = storage.get_place_name(place_id)
	return (
		f'{apm7_text_create_duty_title} {user['place_name']}\n{apm7_text_start_date}',
		{
			const.text_today: "apm7_start_today",
			apm7_text_tomorrow: "apm7_start_tomorrow",
			const.text_cancel: "entry_apm7"
		},
		None
	)


def getEndDate(user):
	return (
		f'{apm7_text_create_duty_title} {user['place_name']}\n{apm7_text_end_date}',
		{
			const.text_today: "apm7_end_today",
			apm7_text_tomorrow: "apm7_end_tomorrow",
			const.text_cancel: "entry_apm7"
		},
		None
	)


def getStartTime(user):
	return (
		f'{apm7_text_create_duty_title} {user['place_name']}\n{apm7_text_start_time}',
		{const.text_cancel: "entry_apm7"},
		'apm7_start_time_validate'
	)


def getEndTime(user):
	return (
		f'{apm7_text_create_duty_title} {user['place_name']}\n{apm7_text_end_time}',
		{const.text_cancel: "entry_apm7"},
		'apm7_end_time_validate'
	)


def show_duty_list(user, place_id):
	data = storage.access_data(place_id, user['location_id'])
	user['place_id'] = place_id
	user['place_name'] = storage.get_place_name(place_id)
	text = ''
	kbd = {}
	if data:
		text += f'{const.text_line}\n'
		has_place_name = False
		duty_number = 1
		for item in data:
			if not has_place_name:
				text += f'{user['place_name']}\n{const.text_line}{get_duty_info(item, duty_number)}'
				has_place_name = True
			else:
				text += f'{get_duty_info(item, duty_number)}'
			text += f'\n{const.text_line}'
			kbd[f'{apm7_text_delete_duty.format(number=duty_number)}'] = f'apm7_confirmdelete_{item['id']}'
			duty_number += duty_number
	else:
		text = f'{user['place_name']}: {apm7_text_no_duty}'
	kbd[apm7_text_create_duty] = f'apm7_create_{place_id}'
	kbd[const.text_cancel] = 'entry_apm7'
	return text, kbd, None


# Проверка времени начала смены
def apm7_start_time_validate(msg, user):
	start_time = TimeTools.getTime(msg)  # '10:15'
	if not start_time:
		return (
			f'{const.text_incorrect} {msg}\n{apm7_text_start_time}',
			{const.text_cancel: "entry_apm7"},
			'apm7_start_time_validate'
		)
	return validate_start_datetime(user, user["start_duty_date"], start_time)


# Проверка времени начала смены
def apm7_end_time_validate(msg, user):
	end_time = TimeTools.getTime(msg)  # '10:15'
	if not end_time:
		return (
			f'{const.text_incorrect} {msg}\n{apm7_text_end_time}',
			{const.text_cancel: "entry_apm7"},
			'apm7_end_time_validate'
		)
	return validate_end_datetime(user, user["end_duty_date"], end_time)


def validate_start_datetime(user, date, time):
	start_time = TimeTools.createFullDate(date, time)
	if storage.check_duty_date(user['duty_arm_id'], start_time):
		user['duty_start_date_time'] = start_time
		return getEndDate(user)
	else:
		return (
			apm7_text_invalid_start_time,
			{const.text_ok: "entry_apm7"},
			None
		)


def validate_end_datetime(user, date, time):
	end_time = TimeTools.createFullDate(date, time)
	end = TimeTools.getDateTime(end_time)
	start = TimeTools.getDateTime(user['duty_start_date_time'])
	if start >= end:
		return (
			f'{const.text_incorrect} {start.strftime(const.datetime_short_format)} -> {end.strftime(const.datetime_short_format)}\n{apm7_wrong_start_after_end}',
			{const.text_ok: "entry_apm7"},
			None
		)

	if storage.check_duty_date(user['duty_arm_id'], end_time):
		user['duty_end_date_time'] = end_time
		return check_data(user)
	else:
		return (
			apm7_text_invalid_end_time,
			{const.text_ok: "entry_apm7"},
			None
		)


def check_data(user):
	return (
		f'{apm7_text_create_duty_title} {user['place_name']}\n{get_new_duty_info(user['duty_start_date_time'], user['duty_end_date_time'])}\n{const.text_data_check}',
		{const.text_done: "apm7_done", const.text_cancel: "entry_apm7"},
		None
	)


def get_first_screen(user):
	kbd = {}
	text = f'/{qr_cmd_gen24} - генерация 24 новых QR-кодов\n'
	text += f'/{qr_cmd_gen48} - генерация 48 новых QR-кодов\n'
	text += f'/{qr_cmd_gen72} - генерация 72 новых QR-кодов\n'
	text += f'/{qr_cmd_old} N1,N2 - получение существующих N1,N2,.. QR-кодов\n\n'

	text += f'{const.text_line}\nЖивотные:\n'
	place_counts = storage.get_place_count(0)
	for item in place_counts:
		text += f'{item['name']} - {item['count']}\n'

	text += f'{const.text_line}\nРабочие смены:'
	arm_list = storage.get_arms(user['location_id'])
	if arm_list is not None:
		for arm in arm_list:
			kbd[arm["arm_name"]] = f'apm7_place_{arm["place_id"]}'
		kbd[const.text_exit] = 'entry_exit'
	return text, kbd, None


##################################
# Global API
##################################

def apm7_start(username, text, key=None):
	user = db.get_user(username)
	if key == 'apm7_start_time':
		user['duty_start_time'] = text
		return getEndDate(user)

	if key == 'apm7_start_time_validate':
		return apm7_start_time_validate(text, user)

	if key == 'apm7_end_time_validate':
		return apm7_end_time_validate(text, user)

	if key == 'apm7_end_time':
		user['duty_end_date'] = text
		return text, {const.text_done: "apm7_done", const.text_cancel: "entry_apm7"}, None


def apm7_button(user, text, key):
	if isinstance(user, str):
		user = db.get_user(user)
	if 'place_' in key:
		return show_duty_list(user, key.split('_')[2])
	if 'create_' in key:
		return create_duty(user, key.split('_')[2])
	if 'confirmdelete_' in key:
		return delete_duty_confirmation(user, key.split('_')[2])
	if 'delete_' in key:
		return delete_duty(user, key.split('_')[2])
	if 'apm7_start_today' in key:
		user['start_duty_date'] = const.today
		my_logger.info(f'start_duty_date today: {user['start_duty_date']}')
		return getStartTime(user)
	if 'apm7_start_tomorrow' in key:
		user['start_duty_date'] = const.tomorrow
		my_logger.info(f'start_duty_date tomorrow: {user['start_duty_date']}')
		return getStartTime(user)
	if 'apm7_end_today' in key:
		user['end_duty_date'] = const.today
		return getEndTime(user)
	if 'apm7_end_tomorrow' in key:
		user['end_duty_date'] = const.tomorrow
		return getEndTime(user)
	if 'apm7_done' in key:
		# random.seed(42)
		password = str(random.randint(10000, 99999))
		# todo проверить наличие такого пароля в базе и выдать другой если он существует.
		start = TimeTools.getDateTime(user['duty_start_date_time'])
		end = TimeTools.getDateTime(user['duty_end_date_time'])
		storage.create_duty(user['duty_arm_id'], start, end, password)
		return get_first_screen(user)
	if key == 'entry_apm7':
		return get_first_screen(user)
	return None, None, None
