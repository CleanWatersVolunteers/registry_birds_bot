# Медицинский прием

from database import Database as db

apm5_text_species = "Введите вид животного"
apm5_text_clinic_state = "Введите клиническое состояние"

##################################
# Global API
##################################

def apm5_start(username, text, key=None):
	user = db.get_user(username)
	if user["animal_id"] == None:
		user["animal_id"] = db.get_animal_id(text)	
		if user["animal_id"] == None:
			return (
				f'❌ Животное с номером {text} не найдено!',
				{"Отмена": "entry_cancel"}, None
			)
		user["code"] = text
	if key == 'apm5_species':
		user["species"] = text
		return (
			apm5_text_clinic_state,
			{"Отмена": "entry_cancel"},
			'apm5_clinic_state'
		)
	if key == 'apm5_clinic_state':
		user["clinic_state"] = text
		text = f'✅ Животное: {user["code"]}\n'
		text += f'✅ Вид: {user["species"]}\n'
		text += f'✅ Клиническое состояние: {user["clinic_state"]}\n'
		return text, {"Готово": "apm5_done", "Отмена": "entry_cancel"},None
	
	return (
			apm5_text_species,
			{"Отмена": "entry_cancel"},
			'apm5_species'
		)

def apm5_entry(username, text, key):
	user = db.get_user(username)
	if key == 'apm5_done':
		db.update_animal(user["animal_id"], species=user["species"], clinical_condition_admission=user["clinic_state"])
	return None, None