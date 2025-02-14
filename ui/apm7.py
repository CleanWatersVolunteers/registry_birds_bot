# История

from storage import storage
from const import const

apm7_text_capture_place = "Место отлова"
apm7_text_capture_time = "Время отлова"
apm7_text_pollution_degree = "Степень загрязнения"
apm7_text_weight = "Вес"
apm7_text_not_specified = "Не указан"
apm7_text_species = "Вид"
apm7_text_clinical_condition = "Клиническое состояние"
apm7_manipulations_not_found = "Манипуляции не найдены"

apm7_capture_datetime_format = "%d.%m.%y %H:%M"
apm7_time_format = "%H:%M"
apm7_date_format = "%d.%m.%y"


def add_hdr_item(label, value):
	text = f'{label}: '
	if value:
		text += f'{value}\n'
	else:
		text += '-\n'
	return text


def ui_welcome_get_card(animal_id):
	animal = storage.get_animal_by_id(animal_id)
	if animal:
		text = add_hdr_item(const.text_animal_number, animal["bar_code"])
		text += add_hdr_item(apm7_text_capture_place, animal["place_capture"])
		text += add_hdr_item(apm7_text_capture_time, animal["capture_datetime"].strftime(apm7_capture_datetime_format))
		text += add_hdr_item(apm7_text_pollution_degree, animal["degree_pollution"])
		text += add_hdr_item(apm7_text_weight,
							 f"{animal['weight']} гр." if animal["weight"] else apm7_text_not_specified)
		text += add_hdr_item(apm7_text_species, animal["species"] if animal["species"] else apm7_text_not_specified)
		text += add_hdr_item(apm7_text_clinical_condition, animal["clinical_condition_admission"] if animal[
			"clinical_condition_admission"] else apm7_text_not_specified)
		text += '---------------\n'
		return text
	return None


##################################
# Global API
##################################

def apm7_start(username, text, key=None):
	animal = storage.get_animal_by_bar_code(text)
	if animal is None:
		return (
			const.animal_not_found.format(code=text),
			{const.text_ok: "entry_cancel"},
			None
		)

	text = ui_welcome_get_card(animal["animal_id"])
	numerical_history = storage.get_animal_numerical_history(animal["animal_id"])
	history = storage.get_animal_history(animal["animal_id"])
	place_history = storage.get_place_history(animal["animal_id"])

	combined_history = numerical_history + history + place_history
	sorted_history = sorted(combined_history, key=lambda item: item['datetime'])
	result_string = ""
	current_date = None
	for item in sorted_history:
		formatted_date = item['datetime'].strftime(apm7_date_format)
		if current_date != formatted_date:
			if current_date is not None:
				result_string += "\n"
			result_string += f"{formatted_date}\n"
			current_date = formatted_date
		if 'type_name' in item:  # Элемент из numerical_history
			result_string += f"{item['datetime'].strftime(apm7_time_format)} - {item['type_name']}: {item['value']} {item['type_units']} - {item['tg_nickname']}\n"
		elif 'manipulation_name' in item:  # Элемент из history
			result_string += f"{item['datetime'].strftime(apm7_time_format)} - {item['manipulation_name']} - {item['tg_nickname']}\n"
		else:
			result_string += f"{item['datetime'].strftime(apm7_time_format)} - {item['place_name']} - {item['location_name']}\n"
	if result_string == "":
		text += apm7_manipulations_not_found
	else:
		text += result_string.strip()
	return text, {const.text_done: "entry_cancel"}, None


def apm7_entry(username, text, key):
	return None, None
