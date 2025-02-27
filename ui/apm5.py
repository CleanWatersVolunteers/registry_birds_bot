# Медицинский прием

from const import const
from database import Database as db
from storage import storage
from ui.history import history_get_info

apm5_text_species = '⚠️ Введите вид животного'
apm5_text_clinic_state = '⚠️ Введите клиническое состояние'
apm5_text_animal_dead = 'Гибель'
apm5_text_animal_dead_confirmation = '⚠️ Подтвердите гибель'

history_text_pollution_degree = 'Степень загрязнения'
history_text_weight = 'Вес'
history_text_not_specified = 'Не указан'
history_text_species = 'Вид'
history_text_clinical_condition = 'Клиническое состояние'

apm5_place_id = 5


def apm5_add_hdr_item(label, value):
	text = f'{label}: '
	if value:
		text += f'{value}\n'
	else:
		text += '-\n'
	return text


def apm5_show_mpls(user, mpls):
	kbd = dict()
	text = f'{apm5_get_animal_card(user['animal'])}\n'
	for mpl in mpls:  # {'id':'1', "name":"манипуляция 1"}
		if str(mpl['id']) in user['mpl_list']:
			text += f'✅ {mpl['name']}\n'
		else:
			if user['animal']['is_dead'] is False:
				kbd[mpl['name']] = f'apm5_mpl_{mpl["id"]}'
	return text, kbd


def apm5_get_animal_card(animal):
	if animal:
		text = apm5_add_hdr_item(const.text_animal_number, animal['bar_code'])
		text += apm5_add_hdr_item(const.text_capture_place, animal['place_capture'])
		text += apm5_add_hdr_item(const.text_capture_time, animal['capture_datetime'].strftime(const.datetime_format))
		text += apm5_add_hdr_item(history_text_pollution_degree, animal['degree_pollution'])
		text += apm5_add_hdr_item(history_text_weight,
								  f"{animal['weight']} гр." if animal['weight'] else history_text_not_specified)
		text += apm5_add_hdr_item(history_text_species,
								  animal['species'] if animal['species'] else history_text_not_specified)
		text += apm5_add_hdr_item(history_text_clinical_condition, animal["clinical_condition_admission"] if animal[
			'clinical_condition_admission'] else history_text_not_specified)
		text += f'{const.text_line}\n'
		return text
	return None


##################################
# Global API
##################################

def apm5_start(username, text, key=None):
	user = db.get_user(username)
	if key is None:
		animal = storage.get_animal_by_bar_code(text)
		if animal is None:
			return (
				const.animal_not_found.format(code=text),
				{const.text_ok: 'entry_cancel'},
				None
			)
		user['animal'] = animal
		dead_info = storage.get_animal_dead(animal["bar_code"])
		user['animal']['is_dead'] = dead_info is not None
		if animal['species'] is None:
			return (
				f'{apm5_get_animal_card(animal)}\n{apm5_text_species}',
				{const.text_cancel: 'entry_cancel'},
				'apm5_species'
			)
		user['mpl_list'] = []
		mpls = storage.get_manipulations(apm5_place_id)
		if len(mpls) == 0:
			return (
				const.manipulation_not_found,
				{const.text_exit: 'entry_cancel'}, None
			)
		text, kbd = apm5_show_mpls(user, mpls)
		if user['animal']['is_dead'] is False:
			kbd[apm5_text_animal_dead] = 'apm5_animal_dead_confirmation'
		kbd['Готово'] = 'entry_cancel'
		text += history_get_info(animal, dead_info)
		text += f'\n{const.text_line}\n'
		if user['animal']['is_dead'] is False:
			text += f'\n{const.text_manipulation_done}'
		return text, kbd, None
	if key == 'apm5_species':
		user['species'] = text
		return (
			f'{const.text_animal_number} {user['animal']['bar_code']}\n{apm5_text_clinic_state}',
			{const.text_cancel: 'entry_cancel'},
			'apm5_clinic_state'
		)
	if key == 'apm5_clinic_state':
		user['clinic_state'] = text
		text = f'{const.text_animal_number} {user['animal']['bar_code']}\n'
		text += f'{const.text_data_check}\n'
		text += f'❓ Вид: {user['species']}\n'
		text += f'❓ Клиническое состояние: {user['clinic_state']}\n'
		return text, {const.text_done: 'apm5_done', const.text_cancel: 'entry_cancel'}, None
	return (
		apm5_text_species,
		{const.text_cancel: 'entry_cancel'},
		'apm5_species'
	)


def apm5_animal_dead_confirmation(user):
	return (
		f'{apm5_text_animal_dead_confirmation} {const.text_animal_number} {user['animal']['bar_code']}',
		{f'{const.text_ok}': f'apm5_animal_dead', f'{const.text_cancel}': "entry_apm5"},
		None
	)


def apm5_animal_dead(user, username):
	animal_id = user['animal']['animal_id']
	arm_id = storage.get_arm_id(user['apm']['place_id'], user['location_id'])
	if arm_id is not None:
		storage.create_dead_animal(animal_id, arm_id, username)
	return None, None, None


def apm5_button(username, text, key):
	user = db.get_user(username)
	if key == 'apm5_done':
		storage.update_animal(
			animal_id=user['animal']['animal_id'],
			species=user['species'],
			clinical_condition_admission=user['clinic_state']
		)
	if key == 'apm5_animal_dead_confirmation':
		return apm5_animal_dead_confirmation(user)
	if key == 'apm5_animal_dead':
		return apm5_animal_dead(user, username)
	if "mpl" in key:
		user = db.get_user(username)
		key_id = key.split('_')[-1]
		user["mpl_list"].append(key_id)
		storage.insert_history(
			manipulation_id=key_id,
			animal_id=user['animal']['animal_id'],
			arms_id=user['apm']['arm_id'],
			tg_nickname=username
		)
		mpls = storage.get_manipulations(apm5_place_id)
		text, kbd = apm5_show_mpls(user, mpls)
		if user['animal']['is_dead'] is False:
			kbd[apm5_text_animal_dead] = 'apm5_animal_dead_confirmation'
		kbd['Готово'] = 'entry_cancel'
		return text, kbd, None
	return None, None, None
