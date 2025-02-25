# Медицинский прием

from const import const
from database import Database as db
from storage import storage

apm5_text_species = "Введите вид животного"
apm5_text_clinic_state = "Введите клиническое состояние"


##################################
# Global API
##################################

def apm5_start(username, text, key=None):
	user = db.get_user(username)
	if key is None:
		animal = storage.get_animal_by_bar_code(text)
		if animal is None:
			return (
				const.animal_not_found.format(code=text),
				{const.text_ok: "entry_cancel"},
				None
			)
		user["animal_id"] = animal['animal_id']
		user["bar_code"] = text
		return (
			f'{const.text_animal_number} {text}\n{apm5_text_species}',
			{const.text_cancel: "entry_cancel"},
			'apm5_species'
		)
	if key == 'apm5_species':
		user["species"] = text
		return (
			f'{const.text_animal_number} {text}\n{apm5_text_clinic_state}',
			{const.text_cancel: "entry_cancel"},
			'apm5_clinic_state'
		)
	if key == 'apm5_clinic_state':
		user["clinic_state"] = text
		text = f'{const.text_animal_number} {user["bar_code"]}\n'
		text += f'{const.text_data_check}\n'
		text += f'❓ Вид: {user["species"]}\n'
		text += f'❓ Клиническое состояние: {user["clinic_state"]}\n'
		return text, {const.text_done: "apm5_done", const.text_cancel: "entry_cancel"}, None

	return (
		apm5_text_species,
		{const.text_cancel: "entry_cancel"},
		'apm5_species'
	)


def apm5_button(username, text, key):
	user = db.get_user(username)
	if key == 'apm5_done':
		storage.update_animal(
			animal_id=user["animal_id"],
			species=user["species"],
			clinical_condition_admission=user["clinic_state"]
		)

	return None, None, None
