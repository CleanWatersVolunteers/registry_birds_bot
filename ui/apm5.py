# Медицинский прием
import re

from const import const
from database import Database as Db
from storage import Storage
from timetools import week_db, TimeTools
from tools import Tools
from ui.history import get_diff_values_history
from ui.history import history_get_info

apm5_text_clinic_state = '⚠️ Введите клиническое состояние'
apm5_text_note = 'Введите текст заметки'
apm5_text_neurological = 'Неврологическая симптоматика'

history_text_pollution_degree = 'Степень загрязнения'
history_text_weight = 'Вес'
history_text_not_specified = 'Не указан'
history_text_species = 'Вид'
history_text_clinical_condition = 'Клиническое состояние'
history_text_triage = 'Триаж'

apm5_place_id = 5

# БД values_history_type.id
apm5_note_history_type_id = 7
apm5_neurological_history_type_id = 8

# БД manipulations.id
apm5_note_manipulations_id = 16
apm5_neurological_manipulations_id = 17


def apm5_add_hdr_item(label, value):
	text = f'{label}: '
	if value:
		text += f'{value}\n'
	else:
		text += '-\n'
	return text


def apm5_show_mpls(user, dead_info=None, out_info=None):
	kbd = dict()
	text = f'{apm5_get_animal_card(user)}\n'
	history = history_get_info(user['animal']['animal_id'], user['animal']['capture_datetime'], week_db(), dead_info,
							   out_info)
	if history is not None:
		text += f'{history}\n'
	if user['animal']['is_dead'] is False and user['animal']['is_out'] is False:
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
	kbd[const.text_done] = 'apm5_done'
	if len(kbd) > 1:
		text += f'{const.text_line}\n{const.text_manipulation_done}'
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
		text = f'{Tools.getAnimalTitle(user['animal'])}\n'
		text += apm5_add_hdr_item(const.text_capture_place, animal['place_capture'])
		text += apm5_add_hdr_item(const.text_capture_time, animal['capture_datetime'].strftime(const.datetime_format))
		if user['animal']['is_dead'] is False and user['animal']['is_out'] is False:
			text += f'({TimeTools.formatTimeInterval(start_datetime=animal['capture_datetime'])})\n'
		text += apm5_add_hdr_item(history_text_pollution_degree, animal['degree_pollution'])
		text += apm5_add_hdr_item(history_text_weight,
								  f"{animal['weight']} гр." if animal['weight'] else history_text_not_specified)
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
		f'{const.text_animal_dead_confirmation} {Tools.getAnimalTitle(user['animal'])}',
		{f'{const.text_ok}': f'apm5_animal_dead', f'{const.text_cancel}': "entry_apm5"},
		None
	)


def apm5_animal_dead(user):
	arm_id = Storage.get_arm_id(user['apm']['place_id'], user['location_id'])
	if arm_id is not None:
		animal_id = user['animal']['animal_id']
		Tools.dead(animal_id, user['animal']['bar_code'], arm_id, user['name'])
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
		user['there_are_changes'] = False
		dead_info = Storage.get_animal_dead(animal["bar_code"])
		user['animal']['is_dead'] = dead_info is not None
		out_info = Storage.get_animal_outside(animal["bar_code"])
		user['animal']['is_out'] = out_info is not None
		if animal['clinical_condition_admission'] is None:
			return (
				f'{Tools.getAnimalTitle(user['animal'])}\n{apm5_text_clinic_state}',
				{const.text_cancel: 'entry_cancel'},
				'apm5_clinic_state'
			)
		user['mpl_list'] = []
		text, kbd = apm5_show_mpls(user, dead_info, out_info)
		return text, kbd, None
	if key == 'apm5_clinic_state':
		user['clinic_state'] = text
		text = f'{Tools.getAnimalTitle(user['animal'])}\n'
		text += f'{const.text_data_check}\n'
		text += f'❓ Клиническое состояние: {user['clinic_state']}\n'
		return text, {const.text_done: 'apm5_clinical_condition', const.text_cancel: 'entry_cancel'}, None
	if key == 'apm5_note':
		user['there_are_changes'] = True
		Storage.insert_value_history(animal_id=user['animal']['animal_id'], type_id=apm5_note_history_type_id,
									 value=text,
									 tg_nickname=user['name'])
		text, kbd = apm5_show_mpls(user)
		return text, kbd, None


def apm5_button(user, text, key):
	if key == 'apm5_animal_dead_confirmation':
		return apm5_animal_dead_confirmation(user)
	if key == 'apm5_animal_dead':
		return apm5_animal_dead(user)
	if key == 'apm5_done':
		if user['there_are_changes']:
			# todo Использовать arm_id из базы #154
			arm_id = Storage.get_arm_id(apm5_place_id, user['location_id'])
			# todo Использовать arm_id из базы #154
			Storage.insert_place_history(arm_id, user['animal']['animal_id'], user['name'])
		return None, None, None
	if "mpl" in key:
		match = re.search(r'\d+$', key)
		manipulation_id = match.group()
		if int(manipulation_id) == const.diarrhea_manipulations_id:
			return (
				f'{Tools.getAnimalTitle(user['animal'])}\n{const.text_diarrhea}',
				[{const.text_yes: 'apm5_diarrhea_yes', const.text_no: 'apm5_diarrhea_no'},
				 {const.text_cancel: 'entry_cancel'}],
				None
			)
		elif int(manipulation_id) == apm5_note_manipulations_id:
			return (
				f'{Tools.getAnimalTitle(user['animal'])}\n{apm5_text_note}',
				{const.text_cancel: "entry_cancel"},
				'apm5_note'
			)
		elif int(manipulation_id) == apm5_neurological_manipulations_id:
			return (
				f'{Tools.getAnimalTitle(user['animal'])}\n{apm5_text_neurological}',
				[{const.text_yes: "apm5_neurological_yes", const.text_no: "apm5_neurological_no"},
				 {const.text_cancel: "entry_cancel"}],
				None
			)
		else:
			key_id = key.split('_')[-1]
			user["mpl_list"].append(key_id)
			Storage.insert_history(manipulation_id=key_id, animal_id=user['animal']['animal_id'],
								   arms_id=user['apm']['arm_id'], tg_nickname=user['name'])
			user['there_are_changes'] = True
	elif key == 'apm5_diarrhea_yes':
		user["mpl_list"].append(str(const.diarrhea_manipulations_id))
		Storage.insert_value_history(animal_id=user['animal']["animal_id"], type_id=const.diarrhea_history_type_id,
									 value=const.text_yes,
									 tg_nickname=user['name'])
		user['there_are_changes'] = True
	elif key == 'apm5_diarrhea_no':
		user["mpl_list"].append(str(const.diarrhea_manipulations_id))
		Storage.insert_value_history(animal_id=user['animal']["animal_id"], type_id=const.diarrhea_history_type_id,
									 value=const.text_no,
									 tg_nickname=user['name'])
		user['there_are_changes'] = True
	elif key == 'apm5_neurological_yes':
		user["mpl_list"].append(str(apm5_neurological_manipulations_id))
		Storage.insert_value_history(animal_id=user['animal']["animal_id"], type_id=apm5_neurological_history_type_id,
									 value=const.text_yes,
									 tg_nickname=user['name'])
		user['there_are_changes'] = True
	elif key == 'apm5_neurological_no':
		user["mpl_list"].append(str(apm5_neurological_manipulations_id))
		Storage.insert_value_history(animal_id=user['animal']["animal_id"], type_id=apm5_neurological_history_type_id,
									 value=const.text_no,
									 tg_nickname=user['name'])
	elif key == 'apm5_clinical_condition':
		Storage.update_animal(animal_id=user['animal']['animal_id'], clinical_condition_admission=user['clinic_state'])
		user['there_are_changes'] = True
	text, kbd = apm5_show_mpls(user)
	return text, kbd, None
