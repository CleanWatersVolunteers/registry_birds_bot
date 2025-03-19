# Медицинский прием
import re

from const import const
from database import Database as Db
from storage import Storage
from timetools import week_db, TimeTools
from ui.history import get_diff_values_history
from ui.history import history_get_info

apm5_text_clinic_state = '⚠️ Введите клиническое состояние'
apm5_text_other = 'Введите описание'

history_text_pollution_degree = 'Степень загрязнения'
history_text_weight = 'Вес'
history_text_not_specified = 'Не указан'
history_text_species = 'Вид'
history_text_clinical_condition = 'Клиническое состояние'
history_text_triage = 'Триаж'

apm5_place_id = 5


def apm5_add_hdr_item(label, value):
	text = f'{label}: '
	if value:
		text += f'{value}\n'
	else:
		text += '-\n'
	return text


def apm5_show_mpls(user, dead_info=None):
	kbd = dict()
	text = f'{apm5_get_animal_card(user)}\n'
	history = history_get_info(user['animal']['animal_id'], week_db(), dead_info)
	if history is not None:
		text += f'{history}\n'
	if user['animal']['is_dead'] is False:
		mpls = Storage.get_manipulations(apm5_place_id)
		if len(mpls) > 0:
			text += f'{const.text_line}\n'
			for mpl in mpls:  # {'id':'1', "name":"манипуляция 1"}
				if ('mpl_list' in user
						and str(mpl['id']) in user['mpl_list']):
					text += f'✅ {mpl['name']}\n'
				else:
					kbd[mpl["name"]] = f'apm5_mpl_{mpl['id']}'
		else:
			text += f'{const.manipulation_not_found}\n'
		kbd[const.text_animal_dead] = 'apm5_animal_dead_confirmation'
	kbd['Готово'] = 'entry_cancel'
	text += const.text_manipulation_done
	return text, kbd


def apm5_get_triage(triage):
	if triage == 1:
		return const.text_triage_green
	elif triage == 2:
		return const.text_triage_yellow
	elif triage == 3:
		return const.text_triage_red


def apm5_get_animal_card(user):
	animal = Storage.get_animal_by_bar_code(user['animal']['bar_code'])
	if animal:
		text = apm5_add_hdr_item(const.text_animal_number, animal['bar_code'])
		text += apm5_add_hdr_item(const.text_capture_place, animal['place_capture'])
		text += apm5_add_hdr_item(const.text_capture_time, animal['capture_datetime'].strftime(const.datetime_format))
		text += f'({TimeTools.formatTimeInterval(animal['capture_datetime'])})\n'
		text += apm5_add_hdr_item(history_text_pollution_degree, animal['degree_pollution'])
		text += apm5_add_hdr_item(history_text_weight,
								  f"{animal['weight']} гр." if animal['weight'] else history_text_not_specified)
		text += apm5_add_hdr_item(history_text_species,
								  animal['species'] if animal['species'] else history_text_not_specified)
		text += apm5_add_hdr_item(history_text_clinical_condition, animal["clinical_condition_admission"] if animal[
			'clinical_condition_admission'] else history_text_not_specified)
		if animal["triage"]:
			animal["triage"] = apm5_get_triage(animal["triage"])
		else:
			animal["triage"] = history_text_not_specified
		text += apm5_add_hdr_item(history_text_triage, animal["triage"])
		weight_change = get_diff_values_history(animal['animal_id'], const.history_type_weight)
		if weight_change is not None:
			text += weight_change
		text += f'{const.text_line}'
		return text
	return None


def apm5_animal_dead_confirmation(user):
	return (
		f'{const.text_animal_dead_confirmation} {const.text_animal_number} {user['animal']['bar_code']}',
		{f'{const.text_ok}': f'apm5_animal_dead', f'{const.text_cancel}': "entry_apm5"},
		None
	)


def apm5_animal_dead(user):
	animal_id = user['animal']['animal_id']
	arm_id = Storage.get_arm_id(user['apm']['place_id'], user['location_id'])
	if arm_id is not None:
		Storage.create_dead_animal(animal_id, arm_id, user['name'])
	return None, None, None


##################################
# Global API
##################################

def apm5_start(user_id, text, key=None):
	user = Db.get_user(user_id)
	if key is None:
		animal = Storage.get_animal_by_bar_code(text)
		if animal == {}:
			return (
				const.animal_not_found.format(code=text),
				{const.text_ok: 'entry_cancel'},
				None
			)
		user['mpl_list'] = []
		user['animal'] = animal
		dead_info = Storage.get_animal_dead(animal["bar_code"])
		user['animal']['is_dead'] = dead_info is not None
		if animal['clinical_condition_admission'] is None:
			return (
				f'{const.text_animal_number} {user['animal']['bar_code']}\n{apm5_text_clinic_state}',
				{const.text_cancel: 'entry_cancel'},
				'apm5_clinic_state'
			)
		user['mpl_list'] = []
		text, kbd = apm5_show_mpls(user, dead_info)
		return text, kbd, None
	if key == 'apm5_clinic_state':
		user['clinic_state'] = text
		text = f'{const.text_animal_number} {user['animal']['bar_code']}\n'
		text += f'{const.text_data_check}\n'
		text += f'❓ Клиническое состояние: {user['clinic_state']}\n'
		return text, {const.text_done: 'apm5_done', const.text_cancel: 'entry_cancel'}, None
	if key == 'apm5_diarrhea_yes':
		Storage.insert_value_history(animal_id=user['animal']['animal_id'], type_id=const.diarrhea_history_type_id,
									 value=const.text_yes,
									 tg_nickname=user['name'])
		text, kbd = apm5_show_mpls(user)
		return text, kbd, None
	if key == 'apm5_diarrhea_no':
		Storage.insert_value_history(animal_id=user['animal']['animal_id'], type_id=const.diarrhea_history_type_id,
									 value=const.text_no,
									 tg_nickname=user['name'])
		text, kbd = apm5_show_mpls(user)
		return text, kbd, None
	if key == 'apm5_other':
		Storage.insert_value_history(animal_id=user['animal']['animal_id'], type_id=const.other_history_type_id,
									 value=text,
									 tg_nickname=user['name'])
		text, kbd = apm5_show_mpls(user)
		return text, kbd, None


def apm5_button(user, text, key):
	if key == 'apm5_animal_dead_confirmation':
		return apm5_animal_dead_confirmation(user)
	if key == 'apm5_animal_dead':
		return apm5_animal_dead(user)
	if "mpl" in key:
		match = re.search(r'\d+$', key)
		manipulation_id = match.group()
		if int(manipulation_id) == const.diarrhea_manipulations_id:
			return (
				f'{const.text_animal_number} {user['animal']["bar_code"]}\n{const.text_diarrhea}',
				{const.text_yes: "apm5_diarrhea_yes", const.text_no: "apm5_diarrhea_no",
				 const.text_cancel: "entry_cancel"},
				None
			)
		elif int(manipulation_id) == const.other_manipulations_id:
			return (
				f'{const.text_animal_number} {user['animal']["bar_code"]}\n{apm5_text_other}',
				{const.text_cancel: "entry_cancel"},
				'apm5_other'
			)
		else:
			key_id = key.split('_')[-1]
			user["mpl_list"].append(key_id)
			Storage.insert_history(manipulation_id=key_id, animal_id=user['animal']['animal_id'],
								   arms_id=user['apm']['arm_id'], tg_nickname=user['name'])
	elif key == 'apm5_diarrhea_yes':
		user["mpl_list"].append(str(const.diarrhea_manipulations_id))
		Storage.insert_value_history(animal_id=user['animal']["animal_id"], type_id=const.diarrhea_history_type_id,
									 value=const.text_yes,
									 tg_nickname=user['name'])
	elif key == 'apm5_diarrhea_no':
		user["mpl_list"].append(str(const.diarrhea_manipulations_id))
		Storage.insert_value_history(animal_id=user['animal']["animal_id"], type_id=const.diarrhea_history_type_id,
									 value=const.text_no,
									 tg_nickname=user['name'])
	elif key == 'apm5_done':
		Storage.update_animal(animal_id=user['animal']['animal_id'], clinical_condition_admission=user['clinic_state'])
	text, kbd = apm5_show_mpls(user)
	return text, kbd, None
