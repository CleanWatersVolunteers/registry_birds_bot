# Нянька

import re

from const import const
from database import Database as db
from storage import storage
from tools import Tools
from ui.history import history_get_info

apm6_place_id = 6

nanny_minimal_weight = 50
nanny_minimal_fish = 1

# БД manipulations.id
feeding_manipulations_id = 0
weighting_manipulations_id = 7

# БД numerical_history_type.id
feeding_history_type_id = 1
weighting_history_type_id = 2

nanny_text_entry_fish = 'Введите количество съеденных рыб'
nanny_text_weighing_action = 'Введите массу животного в граммах'
nanny_text_incorrect_digit = '❌ Вводите только цифры'
nanny_text_incorrect_fish_number = '❌ Количество должно быть больше 0'
nanny_text_incorrect_weight = f"Вес должен быть от {nanny_minimal_weight} гр."


def nanny_weighing(msg, user, username) -> (str,):
	if not msg.isdigit() or int(msg) < nanny_minimal_weight:
		error_text = nanny_text_incorrect_digit if not msg.isdigit() else nanny_text_incorrect_weight
		return (
			f'{const.text_animal_number} {user["bar_code"]}\n{error_text}\n{nanny_text_weighing_action}',
			{const.text_cancel: "entry_cancel"},
			'apm6_weighing'
		)
	else:
		storage.insert_numerical_history(animal_id=user["animal_id"], type_id=weighting_history_type_id, value=int(msg),
										 tg_nickname=username)
		text, kbd = apm6_show_mpls(user)
		return text, kbd, None


def nanny_feeding(msg, user, username) -> (str,):
	if not msg.isdigit() or int(msg) < nanny_minimal_fish:
		error_text = nanny_text_incorrect_digit if not msg.isdigit() else nanny_text_incorrect_fish_number
		return (
			f'{const.text_animal_number} {user["bar_code"]}\n{error_text}\n{nanny_text_entry_fish}',
			{const.text_cancel: "entry_cancel"},
			'apm6_feeding'
		)
	else:
		storage.insert_numerical_history(animal_id=user["animal_id"], type_id=feeding_history_type_id, value=int(msg),
										 tg_nickname=username)
		text, kbd = apm6_show_mpls(user)
		return text, kbd, None


def apm6_show_mpls(user):
	kbd = dict()
	text = f'{const.text_animal_number} {user['bar_code']}\n{const.text_line}\n'
	history = history_get_info(user['animal_id'])
	if history is not None:
		text += f'{history}\n'
	mpls = storage.get_manipulations(apm6_place_id)
	if len(mpls) > 0:
		text += f'{const.text_line}\n'
		for mpl in mpls:  # {'id':'1', "name":"манипуляция 1"}
			if ('mpl_list' in user
					and str(mpl['id']) in user['mpl_list']):
				text += f'✅ {mpl['name']}\n'
			else:
				kbd[mpl['name']] = f'apm6_mpl{mpl['id']}'
	else:
		text += f'{const.manipulation_not_found}\n'
	kbd['Готово'] = "entry_cancel"
	text += f'{const.text_line}\n{const.text_manipulation_done}'
	return text, kbd


##################################
# Global API
##################################

def apm6_start(username, text, key=None):
	user = db.get_user(username)
	if key == 'apm6_feeding':
		return nanny_feeding(text, user, username)
	elif key == 'apm6_weighing':
		return nanny_weighing(text, user, username)

	if key is None:
		checkDead = Tools.checkDead(text)
		if checkDead is not False:
			return checkDead
		animal = storage.get_animal_by_bar_code(text)
		if animal is None:
			return (
				const.animal_not_found.format(code=text),
				{const.text_ok: "entry_cancel"},
				None
			)
		user["animal_id"] = animal['animal_id']
		user["bar_code"] = text
		user["mpl_list"] = []
	text, kbd = apm6_show_mpls(user)
	return text, kbd, None


def apm6_button(username, text, key):
	user = db.get_user(username)
	if "mpl" in key:
		match = re.search(r'\d+$', key)
		manipulation_id = match.group()
		user["mpl_list"].append(manipulation_id)
		if int(manipulation_id) == feeding_manipulations_id:
			return (
				f'{const.text_animal_number} {user["bar_code"]}\n{nanny_text_entry_fish}',
				{const.text_cancel: "entry_cancel"},
				'apm6_feeding'
			)
		elif int(manipulation_id) == weighting_manipulations_id:
			return (
				f'{const.text_animal_number} {user["bar_code"]}\n{nanny_text_weighing_action}',
				{const.text_cancel: "entry_cancel"},
				'apm6_weighing'
			)
		else:
			storage.insert_history(
				manipulation_id=manipulation_id,
				animal_id=user["animal_id"],
				arms_id=user["apm"]["arm_id"],
				tg_nickname=username
			)
			text, kbd = apm6_show_mpls(user)
	# todo Local variable 'kbd' might be referenced before assignment
	return text, kbd, None
