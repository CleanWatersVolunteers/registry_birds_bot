# Нянька

import re

from const import const
from database import Database as Db
from storage import Storage
from timetools import week_db
from tools import Tools
from ui.history import get_diff_values_history
from ui.history import history_get_info

apm6_place_id = 6

nanny_minimal_weight = 50
nanny_minimal_fish = 1

# БД manipulations.id
feeding_manipulations_id = 0
weighting_manipulations_id = 7
feeding_manual_manipulations_id = 19

# БД values_history_type.id
feeding_history_type_id = 1
weighting_history_type_id = 2
feeding_manual_history_type_id = 9

nanny_text_entry_fish = 'Введите вес съеденной еды в граммах'
nanny_text_weighing_action = 'Введите массу животного в граммах'
nanny_text_incorrect_digit = '❌ Вводите только цифры'
nanny_text_incorrect_fish_number = '❌ Количество должно быть больше 0'
nanny_text_incorrect_weight = f'Вес должен быть от {nanny_minimal_weight} гр.'





def nanny_weighing(msg, user, username) -> (str,):
	if not msg.isdigit() or int(msg) < nanny_minimal_weight:
		error_text = nanny_text_incorrect_digit if not msg.isdigit() else nanny_text_incorrect_weight
		return (
			f'{Tools.getAnimalTitle(user['animal'])}\n{error_text}\n{nanny_text_weighing_action}',
			{const.text_cancel: 'entry_cancel'},
			'apm6_weighing'
		)
	else:
		Storage.insert_value_history(animal_id=user['animal']['animal_id'], type_id=weighting_history_type_id,
									 value=int(msg),
									 tg_nickname=username)
		user['there_are_changes'] = True
		text, kbd = apm6_show_mpls(user)
		return text, kbd, None


def nanny_feeding(msg, user, username) -> (str,):
	if not msg.isdigit() or int(msg) < nanny_minimal_fish:
		error_text = nanny_text_incorrect_digit if not msg.isdigit() else nanny_text_incorrect_fish_number
		return (
			f'{Tools.getAnimalTitle(user['animal'])}\n{error_text}\n{nanny_text_entry_fish}',
			{const.text_cancel: 'entry_cancel'},
			'apm6_feeding'
		)
	else:
		Storage.insert_value_history(animal_id=user['animal']['animal_id'], type_id=feeding_history_type_id,
									 value=int(msg),
									 tg_nickname=username)
		user['there_are_changes'] = True
		text, kbd = apm6_show_mpls(user)
		return text, kbd, None


def nanny_manual_feeding(msg, user, username) -> (str,):
	if not msg.isdigit() or int(msg) < nanny_minimal_fish:
		error_text = nanny_text_incorrect_digit if not msg.isdigit() else nanny_text_incorrect_fish_number
		return (
			f'{Tools.getAnimalTitle(user['animal'])}\n{error_text}\n{nanny_text_entry_fish}',
			{const.text_cancel: 'entry_cancel'},
			'apm6_feeding'
		)
	else:
		Storage.insert_value_history(animal_id=user['animal']['animal_id'], type_id=feeding_manual_history_type_id,
									 value=int(msg),
									 tg_nickname=username)
		user['there_are_changes'] = True
		text, kbd = apm6_show_mpls(user)
		return text, kbd, None


def apm6_show_mpls(user):
	kbd = dict()
	text = f'{Tools.getAnimalTitle(user['animal'])}\n{const.text_line}\n'
	history = history_get_info(user['animal']['animal_id'], user['animal']['capture_datetime'], week_db())
	if history is not None:
		text += f'{history}\n'
	weight_change = get_diff_values_history(user['animal']['animal_id'], const.history_type_weight)
	if weight_change is not None:
		text += weight_change
	mpls = Storage.get_manipulations(apm6_place_id)
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
	kbd[const.text_done] = 'apm6_done'
	if len(kbd) > 1:
		text += f'{const.text_line}\n{const.text_manipulation_done}'
	return text, kbd


##################################
# Global API
##################################

def apm6_start(user_id, text, key=None):
	user = Db.get_user(user_id)
	if key == 'apm6_feeding':
		return nanny_feeding(text, user, user['name'])
	elif key == 'apm6_feeding_manual':
		return nanny_manual_feeding(text, user, user['name'])
	elif key == 'apm6_weighing':
		return nanny_weighing(text, user, user['name'])

	if key is None:
		checkDead = Tools.checkLeave(text)
		if checkDead is not False:
			return checkDead
		animal = Storage.get_animal_by_bar_code(text)
		if animal == {}:
			return (
				const.animal_not_found.format(code=text),
				{const.text_ok: "entry_cancel"},
				None
			)
		user['there_are_changes'] = False
		user['animal'] = animal
		user['mpl_list'] = []
	text, kbd = apm6_show_mpls(user)
	return text, kbd, None


def apm6_button(user, text, key):
	if 'mpl' in key:
		match = re.search(r'\d+$', key)
		manipulation_id = match.group()
		user['mpl_list'].append(manipulation_id)
		if int(manipulation_id) == feeding_manipulations_id:
			return (
				f'{Tools.getAnimalTitle(user['animal'])}\n{nanny_text_entry_fish}',
				{const.text_cancel: "entry_cancel"},
				'apm6_feeding'
			)
		elif int(manipulation_id) == feeding_manual_manipulations_id:
			return (
				f'{Tools.getAnimalTitle(user['animal'])}\n{nanny_text_entry_fish}',
				{const.text_cancel: 'entry_cancel'},
				'apm6_feeding_manual'
			)
		elif int(manipulation_id) == weighting_manipulations_id:
			return (
				f'{Tools.getAnimalTitle(user['animal'])}\n{nanny_text_weighing_action}',
				{const.text_cancel: 'entry_cancel'},
				'apm6_weighing'
			)
		elif int(manipulation_id) == const.diarrhea_manipulations_id:
			return (
				f'{Tools.getAnimalTitle(user['animal'])}\n{const.text_diarrhea}',
				[{const.text_yes: 'apm6_diarrhea_yes', const.text_no: 'apm6_diarrhea_no'},
				 {const.text_cancel: 'entry_cancel'}],
				None
			)
		else:
			Storage.insert_history(
				manipulation_id=manipulation_id,
				animal_id=user['animal']['animal_id'],
				arms_id=user['apm']['arm_id'],
				tg_nickname=user['name']
			)
			user['there_are_changes'] = True
			text, kbd = apm6_show_mpls(user)
	elif key == 'apm6_done':
		if user['there_are_changes']:
			# todo Использовать arm_id из базы #154
			arm_id = Storage.get_arm_id(apm6_place_id, user['location_id'])
			# todo Использовать arm_id из базы #154
			Storage.insert_place_history(arm_id, user['animal']['animal_id'], user['name'])
		return None, None, None
	elif key == 'apm6_diarrhea_yes':
		Storage.insert_value_history(animal_id=user['animal']['animal_id'], type_id=const.diarrhea_history_type_id,
									 value=const.text_yes,
									 tg_nickname=user['name'])
		user['there_are_changes'] = True
		text, kbd = apm6_show_mpls(user)
	elif key == 'apm6_diarrhea_no':
		Storage.insert_value_history(animal_id=user['animal']['animal_id'], type_id=const.diarrhea_history_type_id,
									 value=const.text_no,
									 tg_nickname=user['name'])
		user['there_are_changes'] = True
		text, kbd = apm6_show_mpls(user)
	# todo Local variable 'kbd' might be referenced before assignment
	return text, kbd, None
