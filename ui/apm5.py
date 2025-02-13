# Медицинский прием

from database import Database as db
from storage import storage

apm5_text_header = "Животное №:"
apm5_text_species = "Введите вид животного"
apm5_text_clinic_state = "Введите клиническое состояние"
apm5_text_ok = 'OK'
apm5_text_done = 'Готово'
apm5_text_cancel = 'Отмена'
apm5_text_check = f'Проверьте, что данные введены верно и нажмите "{apm5_text_done}"\n'


##################################
# Global API
##################################

def apm5_start(username, text, key=None):
	user = db.get_user(username)
	if key is None:
		code = text
		animal = storage.get_animal_by_bar_code(text)
		if animal is None:
			return (
				f'❌ Животное с номером {code} не найдено!',
				{apm5_text_ok: "entry_cancel"},
				None
			)
		user["animal_id"] = animal['animal_id']
		user["bar_code"] = text
		return (
			f'{apm5_text_header} {text}\n{apm5_text_species}',
			{apm5_text_cancel: "entry_cancel"},
			'apm5_species'
		)
	if key == 'apm5_species':
		user["species"] = text
		return (
			f'{apm5_text_header} {text}\n{apm5_text_clinic_state}',
			{"Отмена": "entry_cancel"},
			'apm5_clinic_state'
		)
	if key == 'apm5_clinic_state':
		user["clinic_state"] = text
		text = f'Животное: {user["bar_code"]}\n'
		text += f'{apm5_text_check}\n'
		text += f'❓ Вид: {user["species"]}\n'
		text += f'❓ Клиническое состояние: {user["clinic_state"]}\n'
		return text, {"Готово": "apm5_done", "Отмена": "entry_cancel"}, None

	return (
		apm5_text_species,
		{"Отмена": "entry_cancel"},
		'apm5_species'
	)


def apm5_entry(username, text, key):
	user = db.get_user(username)
	if key == 'apm5_done':
		storage.update_animal(
			animal_id=user["animal_id"],
			species=user["species"],
			clinical_condition_admission=user["clinic_state"]
		)

	return None, None
