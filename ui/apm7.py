# История

from database import Database as db


##################################
# Global API
##################################

def apm7_start(username, text, key=None):
	user = db.get_user(username)
	if user["animal_id"] == None:
		user["animal_id"] = db.get_animal_id(text)	
		if user["animal_id"] == None:
			return (
				f'❌ Животное с номером {text} не найдено!',
				{"Отмена": "entry_cancel"}, None
			)

	history = db.get_history(user["animal_id"])
	if len(history) == 0:
		return (
			"❌ Манипуляции не найдены!\n",
			{"Готово": "entry_cancel"}, None
		)
	date = history[0]["datetime"].split(' ')[0]
	text = f'{date}:\n'
	for item in history:
		curr_date = item["datetime"].split(' ')[0]
		curr_time = item["datetime"].split(' ')[1]
		if curr_date != date:
			date = curr_date
			text += f'{date}:\n'
		text += f'{curr_time} - {item["manipulation_id"]} - {item["tg_nickname"]}\n'
	return text, {"Готово": "entry_cancel"}, None
	

def apm7_entry(username, text, key):
	return None, None