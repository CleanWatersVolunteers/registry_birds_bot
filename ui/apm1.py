# Поступление

from database import Database as db
from datetime import datetime

apm1_text_place = 'Введите место отлова'
apm1_text_date = 'Введите дату и время отлова в формате ДД.ММ.ГГГГ ЧЧ:ММ'
apm1_text_time = 'Введите время отлова в формате ЧЧ:ММ'
apm1_text_polution = 'Укажите степень загрязнения'

apm1_polution_grade = {
    "apm1_polution_0": "менее 25%",
    "apm1_polution_1": "25%",
    "apm1_polution_2": "50%",
    "apm1_polution_3": "75%",
    "apm1_polution_4": "100%",
    "entry_cancel": "Отмена",
}

##################################
# Global API
##################################

def apm1_start(username, text, key=None):
	user = db.get_user(username)

	if user["animal_id"] == None:
		user["animal_id"] = db.get_animal_id(text)	
	# barcode
	if key == None:
		code = text
		if user["animal_id"] != None:
			return (
				f'❌ Животное с номером {code} уже зарегистрировано\!', 
				{"OK": "entry_cancel"},
				None
			)
		user["code"] = code
		user["animal_id"] = 0
		return (
			apm1_text_place,
			{"Отмена": "entry_cancel"},
			'apm1_place'
		)	
	if key == 'apm1_place':
		user['place'] = text
		return (
			apm1_text_date,
			{"Сегодня": "apm1_today", "Отмена": "entry_cancel"},
			'apm1_date'
		)
	if key == 'apm1_date':
		user['date'] = text # todo incorrect for today button
		kbd = {}
		for key in apm1_polution_grade:
			kbd[apm1_polution_grade[key]] = key
			apm1_text_date,
		return (
			apm1_text_polution,
			kbd,
			'apm1_polution'
		)	
	if key == 'apm1_polution':
		user["polution"] = text
		text = f'✅ Животное: {user["code"]}\n'
		text += f'✅ Место отлова: {user["place"]}\n'
		text += f'✅ Время отлова: {user["date"]}\n'
		text += f'✅ Степень загрязнения: {user["polution"]}\n'
		return text, {"Готово": "apm1_done", "Отмена": "entry_cancel"},None
	return None, None

def apm1_entry(username, msg, key):
	user = db.get_user(username)
	if key == 'apm1_today':
		user['date'] = datetime.now().strftime("%d.%m.%Y")
		return (
			apm1_text_time,
			{"Отмена": "entry_cancel"},
		)	
	keys = key.split('_')
	if keys[1] == 'polution':
		user["polution"] = apm1_polution_grade[key]
		text = f'✅ Животное: {user["code"]}\n'
		text += f'✅ Место отлова: {user["place"]}\n'
		text += f'✅ Время отлова: {user["date"]}\n'
		text += f'✅ Степень загрязнения: {user["polution"]}\n'
		return text, {"Готово": "apm1_done", "Отмена": "entry_cancel"}
	if key == 'apm1_done':
		db.insert_animal(user)
	return None, None

