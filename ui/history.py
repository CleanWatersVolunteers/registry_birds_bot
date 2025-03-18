# История

from const import const
from logs import my_logger
from storage import storage
from timetools import TimeTools

text_weight_change = 'Изменение веса'


##################################
# Global API
##################################

def history_get_info(animal_id, start_date, dead_info=None):
	numerical_history = storage.get_animal_values_history(animal_id, start_date)
	history = storage.get_animal_history(animal_id, start_date)
	place_history = storage.get_place_history(animal_id, start_date)
	my_logger.info(f'history_get_info: {start_date}')

	combined_history = (numerical_history + history + place_history)
	if dead_info is not None:
		combined_history += dead_info
	# todo Shadows name 'item' from outer scope
	sorted_history = sorted(combined_history, key=lambda history_item: history_item['datetime'])
	result_string = ""
	current_date = None
	text = ''
	for item in sorted_history:
		formatted_date = item['datetime'].strftime(const.date_format)
		if current_date != formatted_date:
			if current_date is not None:
				result_string += "\n"
			result_string += f"{formatted_date}\n"
			current_date = formatted_date
		if 'type_name' in item:  # Элемент из values_history
			if item['type_units'] is None:
				result_string += f"{item['datetime'].strftime(const.time_format)} - {item['type_name']}: {item['value']} - {item['tg_nickname']}\n"
			else:
				result_string += f"{item['datetime'].strftime(const.time_format)} - {item['type_name']}: {item['value']} {item['type_units']} - {item['tg_nickname']}\n"
		elif 'manipulation_name' in item:  # Элемент из history
			result_string += f"{item['datetime'].strftime(const.time_format)} - {item['manipulation_name']} - {item['tg_nickname']}\n"
		elif 'animal_id' in item:  # dead_info
			result_string += f"{item['datetime'].strftime(const.time_format)} - Гибель ({TimeTools.formatTimeInterval(item['datetime'])}) - {item['tg_nickname']}\n"
		else:
			result_string += f"{item['datetime'].strftime(const.time_format)} - {item['place_name']} - {item['location_name']}\n"
	if result_string == "":
		text += const.text_manipulations_not_found
	else:
		text += result_string.strip()
	return text


def get_diff_values_history(animal_id, type_id):
	diff = storage.get_diff_values_history(animal_id, type_id)
	if diff is not None:
		if diff > 0:
			return f'{text_weight_change}: + {diff}\n'
		else:
			return f'{text_weight_change}: {diff}\n'
	else:
		return None
