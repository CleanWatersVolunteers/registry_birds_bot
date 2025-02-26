# История

from const import const
from storage import storage

history_text_pollution_degree = "Степень загрязнения"
history_text_weight = "Вес"
history_text_not_specified = "Не указан"
history_text_species = "Вид"
history_text_clinical_condition = "Клиническое состояние"
history_manipulations_not_found = "Манипуляции не найдены"


def add_hdr_item(label, value):
	text = f'{label}: '
	if value:
		text += f'{value}\n'
	else:
		text += '-\n'
	return text


def get_animal_card(animal_id):
	animal = storage.get_animal_by_id(animal_id)
	if animal:
		text = add_hdr_item(const.text_animal_number, animal["bar_code"])
		text += add_hdr_item(const.text_capture_place, animal["place_capture"])
		text += add_hdr_item(const.text_capture_time, animal["capture_datetime"].strftime(const.datetime_format))
		text += add_hdr_item(history_text_pollution_degree, animal["degree_pollution"])
		text += add_hdr_item(history_text_weight,
							 f"{animal['weight']} гр." if animal["weight"] else history_text_not_specified)
		text += add_hdr_item(history_text_species,
							 animal["species"] if animal["species"] else history_text_not_specified)
		text += add_hdr_item(history_text_clinical_condition, animal["clinical_condition_admission"] if animal[
			"clinical_condition_admission"] else history_text_not_specified)
		text += '---------------\n'
		return text
	return None


##################################
# Global API
##################################

def history_start(username, text, key=None):
	animal = storage.get_animal_by_bar_code(text)
	if animal is None:
		return (
			const.animal_not_found.format(code=text),
			{const.text_ok: "entry_cancel"},
			None
		)

	text = get_animal_card(animal["animal_id"])
	numerical_history = storage.get_animal_numerical_history(animal["animal_id"])
	history = storage.get_animal_history(animal["animal_id"])
	place_history = storage.get_place_history(animal["animal_id"])

	combined_history = numerical_history + history + place_history
	# todo Shadows name 'item' from outer scope
	sorted_history = sorted(combined_history, key=lambda item: item['datetime'])
	result_string = ""
	current_date = None
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
	return text, {const.text_done: "entry_cancel"}, None
