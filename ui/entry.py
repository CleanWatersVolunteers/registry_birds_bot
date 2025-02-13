from database import Database as db
from datetime import datetime
import pytz
from ui.code import *
from ui.apm1 import apm1_start, apm1_entry
from ui.apm2 import apm2_start, apm2_entry
from ui.apm3 import apm3_start, apm3_entry
from ui.apm4 import apm4_start, apm4_entry
from ui.apm5 import apm5_start, apm5_entry
from ui.apm6 import apm6_start, apm6_entry
from ui.apm7 import apm7_start, apm7_entry
from storage import storage

NOW = lambda: datetime.utcnow().astimezone(pytz.timezone('Etc/GMT-6')).strftime("%Y.%m.%d %H:%M")

apm_start_list = {
	0: apm1_start,
	1: apm2_start,
	2: apm3_start,
	3: apm4_start,
	4: apm5_start,
	5: apm6_start,
	6: apm7_start,
}
apm_button_list = {
	"apm1": apm1_entry,
	"apm2": apm2_entry,
	"apm3": apm3_entry,
	"apm4": apm4_entry,
	"apm5": apm5_entry,
	"apm6": apm6_entry,
	"apm7": apm7_entry,
}


def show_apm(username):
	kbd = {}
	# todo Подставлять реальный location_id полученный из авторизации
	location_id = 0
	arm_list = storage.get_arms(location_id)
	user = db.get_user(username)
	user["apm_list"] = arm_list
	user["apm"] = None
	user["key"] = None
	user["animal_id"] = None

	if len(arm_list) > 1:
		#  todo Когда-нибудь История переедет в мед. приём
		arm_list.append({'arm_id': 6, 'arm_name': 'История', 'id': 9})
		text = f'Выберите АРМ из списка ниже:'
		if arm_list is not None:
			for arm in arm_list:
				kbd[arm['arm_name']] = f'entry_apm{arm["arm_id"]}'
			kbd['Выход'] = 'entry_exit'
		return text, kbd
	elif len(arm_list) == 1:
		user["apm"] = arm_list[0]
		text, kbd = code_request(user["apm_list"])
		return f'{user["apm"]["arm_name"]}\n{text}', kbd
	else:
		kbd['Выход'] = 'entry_exit'
		return 'APM не найдены!', kbd


##################################
# Global API
##################################

def entry_start(username, text, key=None):
	kbd = {}

	user = db.get_user(username)
	if not user:
		# todo Доделать авторизацию сохранив данные для дальнейшей работы
		print(f'{storage.get_arm_access(NOW(), text)}')
		if db.login(username, text):
			user = db.get_user(username)
	if not user:
		return f'Здравствуйте  {username}!\n⚠ Введите пароль', None
	else:
		if user["apm"]:
			if user["animal_id"] == None:
				code = code_parse(text)
				if code > 0:
					text, kbd, user["key"] = apm_start_list[user["apm"]["arm_id"]](username, code, user["key"])
					return f'{user["apm"]["arm_name"]}\n{text}', kbd
				else:
					txt, kbd = code_request(user["apm_list"])
					return f'{user["apm"]["arm_name"]}\n❌ Неверный ввод: {text}\n{txt}', kbd
			else:
				text, kbd, user["key"] = apm_start_list[user["apm"]["arm_id"]](username, text, user["key"])
				return f'{user["apm"]["arm_name"]}\n{text}', kbd
		return show_apm(username)


def entry_button(username, text, key):
	if key == 'entry_exit':
		db.clear_user(username)

	user = db.get_user(username)
	if not user:
		return f'Здравствуйте  {username}!\n⚠ Введите пароль', None
	if key == 'entry_cancel':
		user["key"] = None
		user["animal_id"] = None
		text, kbd = code_request(user["apm_list"])
		return f'{user["apm"]["arm_name"]}\n{text}', kbd

	if key == 'entry_menu':
		return show_apm(username)

	# select item menu
	keys = key.split('_')
	if keys[0] == 'entry':
		apm_id = int(keys[1][-1])
		for apm in user["apm_list"]:
			if apm['arm_id'] == apm_id:
				user["apm"] = dict(apm)
				text, kbd = code_request(user["apm_list"])
				return f'{user["apm"]["arm_name"]}\n{text}', kbd
	if keys[0] in apm_button_list:
		text, kbd = apm_button_list[keys[0]](username, text, key)
		if not text:
			user["key"] = None
			user["animal_id"] = None
			text, kbd = code_request(user["apm_list"])

		return f'{user["apm"]["arm_name"]}\n{text}', kbd
	print("[!!] Error key", key)
	return text, None
