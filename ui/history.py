# История

from const import const
from storage import storage

history_text_pollution_degree = "Степень загрязнения"
history_text_weight = "Вес"
history_text_not_specified = "Не указан"
history_text_species = "Вид"
history_text_clinical_condition = "Клиническое состояние"
history_manipulations_not_found = "Манипуляции не найдены"


##################################
# Global API
##################################

def history_get_info(animal):
	numerical_history = storage.get_animal_numerical_history(animal["animal_id"], const.yesterday_db)
	history = storage.get_animal_history(animal["animal_id"], const.yesterday_db)
	place_history = storage.get_place_history(animal["animal_id"], const.yesterday_db)

	combined_history = numerical_history + history + place_history
	# todo Shadows name 'item' from outer scope
	sorted_history = sorted(combined_history, key=lambda item: item['datetime'])
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
		if 'type_name' in item:  # Элемент из numerical_history
			result_string += f"{item['datetime'].strftime(const.time_format)} - {item['type_name']}: {item['value']} {item['type_units']} - {item['tg_nickname']}\n"
		elif 'manipulation_name' in item:  # Элемент из history
			result_string += f"{item['datetime'].strftime(const.time_format)} - {item['manipulation_name']} - {item['tg_nickname']}\n"
		else:
			result_string += f"{item['datetime'].strftime(const.time_format)} - {item['place_name']} - {item['location_name']}\n"
	if result_string == "":
		text += history_manipulations_not_found
	else:
		text += result_string.strip()
	return text
