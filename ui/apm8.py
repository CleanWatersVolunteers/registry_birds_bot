# Старший смены
from storage import storage
from const import const

apm8_location_id = 0  # Пока хардкод


def get_duty_info(item):
	return f'\nПароль: {item["password"]}\nНачало: {item["start_date"].strftime(const.datetime_short_format)}\nОкончание: {item["end_date"].strftime(const.datetime_short_format)}'


def arm_info(place_id):
	data = storage.access_data(place_id, apm8_location_id)
	if data:
		text = '------------------------\n'
		has_place_name = False
		for item in data:
			if not has_place_name:
				text += f'{item["name"]}\n-----------------{get_duty_info(item)}'
				has_place_name = True
			else:
				text += f'{get_duty_info(item)}'
			text += '\n-----------------'
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
	if key is None:
		kbd = {}
		arm_list = storage.get_arms(apm8_location_id)
		if arm_list is not None:
			for arm in arm_list:
				kbd[arm['arm_name']] = f'entry_apm{arm["arm_id"]}'
			kbd[const.text_exit] = 'entry_cancel'
			return text, kbd
	return None, None, None


def apm8_entry(username, text, key):
	if 'place_' in key:
		return arm_info(key.split('_')[2])
	if key == 'entry_apm7':
		kbd = {}
		text = 'Рабочие смены:'
		arm_list = storage.get_arms(apm8_location_id)
		if arm_list is not None:
			for arm in arm_list:
				kbd[arm["arm_name"]] = f'apm8_place_{arm["place_id"]}'
			kbd[const.text_exit] = 'entry_exit'
			return text, kbd, None
	return None, None, None
