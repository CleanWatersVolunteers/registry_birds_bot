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
from ui.apm8 import apm8_start, apm8_entry
from storage import storage
from ui.gen import (
	qr_cmd_gen24,
	qr_cmd_gen48,
	qr_cmd_gen72,
	qr_cmd_old
)

NOW = lambda: datetime.utcnow().astimezone(pytz.timezone('Etc/GMT-6')).strftime("%Y.%m.%d %H:%M")

apm_start_list = {
	0: apm1_start,
	1: apm2_start,
	2: apm3_start,
	3: apm4_start,
	4: apm5_start,
	5: apm6_start,
	6: apm7_start,
	7: apm8_start,
}
apm_button_list = {
	"apm1": apm1_entry,
	"apm2": apm2_entry,
	"apm3": apm3_entry,
	"apm4": apm4_entry,
	"apm5": apm5_entry,
	"apm6": apm6_entry,
	"apm7": apm7_entry,
	"apm8": apm8_entry,
}


def show_apm(user, arm_list):
	kbd = {}
	user["apm_list"] = arm_list
	user["apm"] = None
	user["key"] = None
	user["animal_id"] = None
	if len(arm_list) > 1:
		#  todo Когда-нибудь История переедет в мед. приём
		arm_list.append({'arm_id': 6, 'arm_name': 'История', 'place_id': 6})
		text = f'Выберите АРМ из списка ниже:\n'
		text += f'/{qr_cmd_gen24} - генерация 24 новых QR-кодов\n'
		text += f'/{qr_cmd_gen48} - генерация 48 новых QR-кодов\n'
		text += f'/{qr_cmd_gen72} - генерация 72 новых QR-кодов\n'
		text += f'/{qr_cmd_old} N1,N2 - получение существующих N1,N2,.. QR-кодов\n'
		if arm_list is not None:
			for arm in arm_list:
				kbd[arm['arm_name']] = f'entry_apm{arm["arm_id"]}'
			kbd[const.text_exit] = 'entry_exit'
		return text, kbd
	elif len(arm_list) == 1:
		user["apm"] = arm_list[0]
		text, kbd = code_request(user["apm_list"])
		return f'{user["apm"]["arm_name"]}\n{text}', kbd
	else:
		kbd[const.text_exit] = 'entry_exit'
		return 'APM не найдены!', kbd


##################################
# Global API
##################################

def entry_start(username, text, key=None):
	kbd = {}
	arm_list = {}
	user = db.get_user(username)
	if not user:
		file = open('developer.txt', 'r')
		developer_name = file.read()
		file.close()
		if developer_name == username:
			location_id = 0  # Пока хардкод, можно потом вынести в developer.txt
			arm_list = storage.get_arms(location_id)
			user = db.create_user(username, location_id)
		else:
			arm_list = storage.get_arm_access(NOW(), password=text)
			if len(arm_list) > 0:
				user = db.create_user(username, arm_list[0]["location_id"])
			else:
				return f'Здравствуйте {username}!\nПароль не верный\n⚠ Введите пароль', None
	if not user:
		return f'Здравствуйте {username}!\n⚠ Введите пароль', None
	else:
		if user["apm"]:
			if not 'animal_id' in user:
				code = code_parse(text)
				if code == 0:
					txt, kbd = code_request(user["apm_list"])
					return f'{user["apm"]["arm_name"]}\n❌ Неверный ввод: {code}\n{txt}', kbd
			text, kbd, user["key"] = apm_start_list[user["apm"]["place_id"]](username, text, user["key"])
			return f'{user["apm"]["arm_name"]}\n{text}', kbd
		return show_apm(user, arm_list)


def entry_photo(username, data):
	kbd = {}
	user = db.get_user(username)
	code = code_parse(data)
	if not user:
		return f'Здравствуйте  {username}!\n⚠ Введите пароль', None
	else:
		if user["apm"]:
			if not 'animal_id' in user:
				if code == 0:
					txt, kbd = code_request(user["apm_list"])
					return f'{user["apm"]["arm_name"]}\n❌ Неверный ввод: {code}\n{txt}', kbd
			text, kbd, user["key"] = apm_start_list[user["apm"]["place_id"]](username, str(code), user["key"])
			return f'{user["apm"]["arm_name"]}\n{text}', kbd
		return show_apm(user, user["apm_list"])


def entry_button(username, text, key):
	if key == 'entry_exit':
		db.clear_user(username)

	user = db.get_user(username)
	if not user:
		return f'Здравствуйте {username}!\n⚠ Введите пароль', None
	if key == 'entry_cancel':
		user["key"] = None
		user["animal_id"] = None
		text, kbd = code_request(user["apm_list"])
		return f'{user["apm"]["arm_name"]}\n{text}', kbd

	if key == 'entry_menu':
		return show_apm(user, user["apm_list"])

	if key == 'entry_apm7':  # Старший смены
		if user["apm"] is None:
			user["apm"] = dict({"arm_name": "Старший смены"})
		text, kbd, user["key"] = apm8_entry(username, text, key)
		return text, kbd

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
		text, kbd, user["key"] = apm_button_list[keys[0]](username, text, key)
		if not text:
			user["key"] = None
			user["animal_id"] = None
			text, kbd = code_request(user["apm_list"])

		return f'{user["apm"]["arm_name"]}\n{text}', kbd
	print("[!!] Error key", key)
	return text, None
