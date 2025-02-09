# Прием в стационар

from database import Database as db

apm3_text = f"Введите массу животного в граммах"

##################################
# Global API
##################################

def apm3_start(username, text, key=None):
	user = db.get_user(username)
	if user["animal_id"] == None:
		user["animal_id"] = db.get_animal_id(text)	
		if user["animal_id"] == None:
			return (
				f'❌ Животное с номером {text} не найдено!',
				{"Отмена": "entry_cancel"}, None
			)
	if key == 'apm3_mass':
		if not text.isdigit():
			return (
				f'❌ Неверный ввод: {text}\n{apm3_text}',
				{"Отмена": "entry_cancel"}, 'apm3_mass'
			)
		user['mass'] = text
		return (
				f'✅ Масса животного: {text} грамм',
				{"Готово":"apm3_done", "Отмена":"entry_cancel"},
				None
			)
	return (
		apm3_text,
		{"Отмена": "entry_cancel"},
		'apm3_mass'
	)

def apm3_entry(username, msg, key):
	user = db.get_user(username)
	if key == "apm3_done":
		db.update_animal(user["animal_id"], weight = user['mass'])
	return None, None