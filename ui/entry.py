from database import Database as db
import re
from ui.code import *
from ui.apm1 import apm1_start, apm1_entry
from ui.apm2 import apm2_start, apm2_entry
from ui.apm3 import apm3_start, apm3_entry
from ui.apm4 import apm4_start, apm4_entry
from ui.apm5 import apm5_start, apm5_entry
from ui.apm6 import apm6_start, apm6_entry
from ui.apm7 import apm7_start, apm7_entry

entry_apm_list = {
	"apm1": "Поступление",
	"apm2": "Первичка на мойке",
	"apm3": "Прием в стационар",
	"apm4": "Первичка в стационаре",
	"apm5": "Медицинский прием",
	"apm6": "Нянька",
	"apm7": "История",
}

apm_start_list = {
	"apm1":apm1_start,
	"apm2":apm2_start,
	"apm3":apm3_start,
	"apm4":apm4_start,
	"apm5":apm5_start,
	"apm6":apm6_start,
	"apm7":apm7_start,
}
apm_button_list = {
	"apm1":apm1_entry,
	"apm2":apm2_entry,
	"apm3":apm3_entry,
	"apm4":apm4_entry,
	"apm5":apm5_entry,
	"apm6":apm6_entry,
	"apm7":apm7_entry,
}

def show_apm(username):
	kbd = {}
	apm = db.get_apm_list(username)
	user = db.get_user(username)
	user["apm_list"] = apm
	user["apm"] = None
	user["key"] = None
	user["animal_id"] = None
	if len(apm)>1:
		text = f'Выберите АРМ из списка ниже:'
		for item in apm:
			kbd[entry_apm_list[item]] = f'entry_{item}'
		return text, kbd
	elif len(apm) == 1:
		user["apm"] = apm[0]
		text, kbd = code_request(user["apm_list"])
		return f'{entry_apm_list[apm[0]]}\n{text}', kbd
	else:
		return 'APM не найдены!', None


##################################
# Global API
##################################

def entry_start(username, text, key=None):
	kbd = {}

	user = db.get_user(username)
	if not user:
		if db.login(username, text):
			user = db.get_user(username)
	if not user:
		return f'Здравствуйте  {username}!\n⚠ Введите пароль', None
	else:
		if user["apm"]:
			if user["animal_id"] == None:  
				code = code_parse(text)
				if code > 0:
					text,kbd,user["key"] = apm_start_list[user["apm"]](username, code,user["key"])
					return f'{entry_apm_list[user["apm"]]}\n{text}', kbd
				else:
					txt,kbd = code_request(user["apm_list"])
					return f'{entry_apm_list[user["apm"]]}\n❌ Неверный ввод: {text}\n{txt}', kbd
			else:
				text,kbd,user["key"] = apm_start_list[user["apm"]](username, text,user["key"])
				return f'{entry_apm_list[user["apm"]]}\n{text}', kbd
		return show_apm(username)

def entry_button(username, text, key):
	user = db.get_user(username)
	if not user:
		return f'Здравствуйте  {username}!\n⚠ Введите пароль', None

	if key == 'entry_cancel':
		user["key"] = None
		user["animal_id"] = None
		text, kbd = code_request(user["apm_list"])
		return f'{entry_apm_list[user["apm"]]}\n{text}', kbd

	if key == 'entry_menu':
		return show_apm(username)

	# select item menu
	keys = key.split('_')
	if keys[0] == 'entry':
		if keys[1] in entry_apm_list:
			user["apm"] = keys[1]
			text, kbd = code_request(user["apm_list"])
			return f'{entry_apm_list[user["apm"]]}\n{text}', kbd
	if keys[0] in apm_button_list:
		text, kbd = apm_button_list[keys[0]](username, text, key)
		if not text:
			user["key"] = None
			user["animal_id"] = None
			text, kbd = code_request(user["apm_list"])
			# return show_apm(username)
		return f'{entry_apm_list[user["apm"]]}\n{text}', kbd
	return text, None

