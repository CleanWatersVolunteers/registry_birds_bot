from database import Database as Db
from ui.apm1 import apm1_start, apm1_button
from ui.apm2 import apm2_start, apm2_button
from ui.apm3 import apm3_start, apm3_button
from ui.apm4 import apm4_start, apm4_button
from ui.apm5 import apm5_start, apm5_button
from ui.apm6 import apm6_start, apm6_button
from ui.apm7 import apm7_start, apm7_button
from ui.apm8 import apm8_start, apm8_button
from ui.code import *

WELLCOME = 'Здравствуйте {username}!\n⚠ Введите пароль'
SUPERVISOR_ARM = 7

apm_start_list = {
	1: apm1_start,
	2: apm2_start,
	3: apm3_start,
	4: apm4_start,
	5: apm5_start,
	6: apm6_start,
	7: apm7_start,
	8: apm8_start,
}
apm_button_list = {
	"apm1": apm1_button,
	"apm2": apm2_button,
	"apm3": apm3_button,
	"apm4": apm4_button,
	"apm5": apm5_button,
	"apm6": apm6_button,
	"apm7": apm7_button,
	"apm8": apm8_button,
}


def get_arm_name(user):
	if 'location_name' in user['apm']:
		return f'{user["apm"]["arm_name"]} - {user["apm"]["location_name"]}\n'
	else:  # todo У разработчика пока нет location_name
		return f'{user["apm"]["arm_name"]}\n'


def show_apm(user, arm_list, user_id):
	kbd = {}
	user["apm_list"] = arm_list
	user["apm"] = None
	user["key"] = None
	user["animal_id"] = None
	if len(arm_list) > 1:
		text = f'Выберите АРМ из списка ниже:\n'
		if arm_list is not None:
			for arm in arm_list:
				kbd[arm['arm_name']] = f'entry_apm{arm["arm_id"]}'
			kbd[const.text_exit] = 'entry_exit'
		return text, kbd
	elif len(arm_list) == 1:
		user["apm"] = arm_list[0]
		if user["apm"]["place_id"] == SUPERVISOR_ARM:
			key = 'entry_apm7'
			text, kbd, user["key"] = apm7_button(user, None, key)
			return text, kbd
		text, kbd, valid = code_request(user)
		if valid is False:
			Db.clear_user(user_id)
			return text, kbd
		return f'{get_arm_name(user)}{text}', kbd
	else:
		kbd[const.text_exit] = 'entry_exit'
		return 'APM не найдены!', kbd


##################################
# Global API
##################################

def entry_start(username, user_id, text, key=None):
	arm_list = {}
	user = Db.get_user(user_id)
	if not user:
		file = open('developer.txt', 'r')
		developer_name = file.read()
		file.close()
		if developer_name == username:
			location_id = 0  # Пока хардкод, можно потом вынести в developer.txt
			arm_list = Storage.get_arms(location_id)
			user = Db.create_user(user_id, username, location_id)
		else:
			if text is not None and text != "":
				arm_list = Storage.get_arm_access(now_db(), password=text)
				my_logger.info(f'get_arm_access {now_db()}')
				if len(arm_list) > 0:
					user = Db.create_user(user_id, username, arm_list[0]["location_id"], password=text)
					my_logger.info(f'Вход: {username}')
				else:
					my_logger.info(f'Пароль не верный: {username}')
					return f'Здравствуйте {username}!\nПароль не верный\n⚠ Введите пароль', None
			else:
				return f'Здравствуйте {username}!\n⚠ Введите пароль', None  # Нужно для первого входа
	if not user:
		return f'{WELLCOME.format(username=username)}', None
	else:
		if user["apm"]:
			if not 'animal_id' in user:
				code = code_parse(text)
				if code == 0:
					text, kbd, valid = code_request(user)
					if valid is False:
						Db.clear_user(user_id)
						return text, kbd
					return f'{get_arm_name(user)}❌ Неверный ввод: {code}\n{text}', kbd
			text, kbd, user["key"] = apm_start_list[user["apm"]["place_id"]](user_id, text, user["key"])
			return f'{get_arm_name(user)}{text}', kbd
		return show_apm(user, arm_list, user_id)


def entry_photo(username, user_id, data):
	user = Db.get_user(user_id)
	if not user:
		return f'{WELLCOME.format(username=username)}', None
	else:
		if user["apm"]:
			code = code_parse(data)
			if code == 0:
				text, kbd, valid = code_request(user)
				if valid is False:
					Db.clear_user(user_id)
					return text, kbd
				return f'{get_arm_name(user)}❌ Неверный ввод: {code}\n{text}', kbd
			# todo Local variable 'code' might be referenced before assignment
			text, kbd, user["key"] = apm_start_list[user["apm"]["place_id"]](username, str(code), user["key"])
			return f'{get_arm_name(user)}{text}', kbd
		return show_apm(user, user["apm_list"], user_id)


def entry_button(username, user_id, text, key):
	if key == 'entry_exit':
		Db.clear_user(user_id)

	user = Db.get_user(user_id)
	if not user:
		return f'{WELLCOME.format(username=username)}', None
	if key == 'entry_cancel':
		user["key"] = None
		user["animal_id"] = None
		text, kbd, valid = code_request(user)
		if valid is False:
			Db.clear_user(user_id)
			return text, kbd
		return f'{get_arm_name(user)}{text}', kbd

	if key == 'entry_menu':
		return show_apm(user, user["apm_list"], username)

	if key == 'entry_apm7':  # Старший смены
		if user["apm"] is None:
			user["apm"] = dict({"arm_name": "Старший смены", "place_id": 7})
		text, kbd, user["key"] = apm7_button(user, None, key)
		return text, kbd

	# select item menu
	keys = key.split('_')
	if keys[0] == 'entry':
		apm_id = int(keys[1][-1])
		for apm in user["apm_list"]:
			if apm['arm_id'] == apm_id:
				user["apm"] = dict(apm)
				text, kbd, valid = code_request(user)
				if valid is False:
					Db.clear_user(user_id)
					return text, kbd
				return f'{get_arm_name(user)}{text}', kbd
	if keys[0] in apm_button_list:
		text, kbd, user["key"] = apm_button_list[keys[0]](user, text, key)
		if not text:
			user["key"] = None
			user["animal_id"] = None
			text, kbd, valid = code_request(user)
			if valid is False:
				Db.clear_user(user_id)
				return text, kbd
		return f'{get_arm_name(user)}{text}', kbd
	my_logger.error("Error key", key)
	return text, None
