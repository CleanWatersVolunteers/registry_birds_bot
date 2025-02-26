# Медицинский прием

from const import const
from database import Database as db
from storage import storage

apm5_text_species = '⚠️ Введите вид животного'
apm5_text_clinic_state = '⚠️ Введите клиническое состояние'

history_text_pollution_degree = 'Степень загрязнения'
history_text_weight = 'Вес'
history_text_not_specified = 'Не указан'
history_text_species = 'Вид'
history_text_clinical_condition = 'Клиническое состояние'
history_manipulations_not_found = 'Манипуляции не найдены'

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
	text = f'{get_animal_card(user['animal'])}\n'
	for mpl in mpls:  # {'id':'1', "name":"манипуляция 1"}
		if str(mpl['id']) in user['mpl_list']:
			text += f'✅ {mpl['name']}\n'
		else:
			kbd[mpl['name']] = f'apm5_mpl_{mpl["id"]}'
	kbd['Готово'] = 'entry_cancel'
	text += f'{const.text_manipulation_done}'
	return text, kbd


def get_animal_card(animal):
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
		text += '---------------\n'
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
		if animal['species'] is None:
			return (
				f'{get_animal_card(animal)}\n{apm5_text_species}',
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


def apm5_button(username, text, key):
	user = db.get_user(username)
	if key == 'apm5_done':
		storage.update_animal(
			animal_id=user['animal']['animal_id'],
			species=user['species'],
			clinical_condition_admission=user['clinic_state']
		)
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
		return text, kbd, None
	return None, None, None
