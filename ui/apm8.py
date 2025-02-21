# Старший смены
from database import Database as db
from storage import storage
from const import const
from ui.gen import (
	qr_cmd_gen24,
	qr_cmd_gen48,
	qr_cmd_gen72,
	qr_cmd_old
)

apm8_text_line = '------------------------'


def get_duty_info(item):
	return f'\nПароль: {item["password"]}\nНачало: {item["start_date"].strftime(const.datetime_short_format)}\nОкончание: {item["end_date"].strftime(const.datetime_short_format)}'


def arm_info(location_id, place_id):
	data = storage.access_data(place_id, location_id)
	if data:
		text = f'{apm8_text_line}\n'
		has_place_name = False
		for item in data:
			if not has_place_name:
				text += f'{item["name"]}\n{apm8_text_line}{get_duty_info(item)}'
				has_place_name = True
			else:
				text += f'{get_duty_info(item)}'
			text += f'\n{apm8_text_line}'
		kbd = {const.text_done: 'entry_apm7'}
		return text, kbd, None
	else:
		return (
			f'Нет данных',
			{const.text_done: "entry_apm7"},
			None
		)


##################################
# Global API
##################################

def apm8_start(username, text, key=None):
	return None, None, None


def apm8_entry(user, text, key):
	if isinstance(user, str):
		user = db.get_user(user)
	if 'place_' in key:
		return arm_info(user['location_id'], key.split('_')[2])
	if key == 'entry_apm7':
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
	return None, None, None
