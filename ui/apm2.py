# Первичка на мойке

from database import Database as db

apm2_text = f"Выполните мойку животного и нажмите 'Готово'"

##################################
# Global API
##################################

def apm2_start(username, text, key=None):
	user = db.get_user(username)
	if user["animal_id"] == None:
		user["animal_id"] = db.get_animal_id(text)	
		if user["animal_id"] == None:
			return (
				f'❌ Животное с номером {text} не найдено!',
				{"Отмена": "entry_cancel"}, None
			)
	return (
		apm2_text,
		{"Готово": "apm2_done", "Отмена": "entry_cancel"},
		None
	)

def apm2_entry(username, text, key):
	return None, None