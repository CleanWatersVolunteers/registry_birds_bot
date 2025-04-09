# Прием в стационар

from const import const
from database import Database as Db
from storage import Storage
from timetools import now
from tools import Tools
from utils.spreadsheets import asyncAddVetOutgone
from utils.spreadsheets import asyncExportOutgoneAnimal

apm3_text = 'Введите массу животного в граммах'
apm3_text_skip = 'Пропустить'
apm3_text_outgone = 'Отбытие'
apm3_text_outgone_confirmation = '⚠️ Подтвердите отбытие'
apm3_text_outgone_description = 'Введите место отбытия'
apm3_text_registration = 'Регистрация'


##################################
# Global API
##################################

def apm3_start(user_id, text, key=None):
	user = Db.get_user(user_id)
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
		user['animal'] = animal
		if animal['weight'] is None:
			return (
				f'{const.text_animal_number} {text}\n{apm3_text}',
				[{const.text_cancel: "entry_cancel", apm3_text_skip: "apm3_show_dead"}],
				'apm3_weight'
			)
		else:
			dead_info = Storage.get_animal_dead(animal['bar_code'])
			if dead_info is None:
				return apm3_show_dead(user, animal['bar_code'])
	if key == 'apm3_outgone_description':
		user['animal_outgone'] = text
		return apm3_animal_outgone_confirmation(user)

	if key == 'apm3_weight':
		if not text.isdigit():
			return (
				f'{const.text_incorrect} {text}\n{apm3_text}',
				{const.text_cancel: 'entry_cancel'},
				'apm3_weight'
			)
		user['weight'] = text
		return (
			f'✅ Вес животного: {text} грамм',
			{const.text_done: "apm3_done", const.text_cancel: "entry_cancel"},
			None
		)
	return None, None


def apm3_show_dead(user, bar_code):
	buttons = [
		{const.text_animal_dead: 'apm3_animal_dead_confirmation', apm3_text_outgone: 'apm3_get_animal_outgone'}
	]
	if Storage.get_reg_time(user['animal']['animal_id'], user['apm']['arm_id']) is None:
		buttons.append({apm3_text_registration: 'apm3_done'})
	buttons.append({const.text_cancel: 'entry_cancel'})
	return (
		f'{const.text_animal_number} {bar_code}',
		buttons,
		None
	)


def apm3_animal_dead_confirmation(user):
	return (
		f'{const.text_animal_dead_confirmation} {const.text_animal_number} {user['animal']['bar_code']}',
		{f'{const.text_ok}': f'apm3_animal_dead', f'{const.text_cancel}': "entry_apm3"},
		None
	)


def apm3_get_animal_outgone(user):
	return (
		f'{const.text_animal_number} {user['animal']['bar_code']}\n{apm3_text_outgone_description}',
		{const.text_cancel: "entry_cancel"},
		'apm3_outgone_description'
	)


def apm3_animal_outgone_confirmation(user):
	return (
		f'{const.text_animal_number} {user['animal']['bar_code']}\n{apm3_text_outgone_confirmation}\n{user['animal_outgone']}',
		{f'{const.text_ok}': f'apm3_animal_outgone_ready', f'{const.text_cancel}': "entry_apm3"},
		None
	)


def apm3_animal_dead(user):
	Tools.dead(user['animal']['animal_id'], user['animal']['bar_code'], user['apm']['arm_id'], user['name'])
	return None, None, None


def apm3_button(user, msg, key):
	if key == "apm3_done":
		if Storage.get_reg_time(user['animal']['animal_id'], user['apm']['arm_id']) is None:
			Storage.insert_place_history(user['apm']['arm_id'], user['animal']['animal_id'], user['name'])
		if 'weight' in user:
			Storage.update_animal(user['animal']['animal_id'], weight=user['weight'])
			del user['weight']  # todo Мало того что оно к user не относится, так еще и сохраняется при смене животного.
	elif key == 'apm3_animal_dead_confirmation':
		return apm3_animal_dead_confirmation(user)
	elif key == 'apm3_animal_dead':
		return apm3_animal_dead(user)
	elif key == 'apm3_show_dead':
		return apm3_show_dead(user, user['animal']['bar_code'])
	elif key == 'apm3_get_animal_outgone':
		return apm3_get_animal_outgone(user)
	elif key == 'apm3_animal_outgone_ready':
		Storage.insert_animals_outside(user['animal']['animal_id'], user['name'], user['animal_outgone'],
									   user['apm']['arm_id'])
		asyncExportOutgoneAnimal(user['animal']['bar_code'], now(), user['animal_outgone'])
		# todo Убрать хардкод конда появится вторая локация
		reg_arm_id = 1
		reg_datetime = Storage.get_reg_time(user['animal']['animal_id'], reg_arm_id)
		asyncAddVetOutgone(user['animal']['bar_code'], reg_datetime.strftime(const.datetime_format), now(),
						   f'{apm3_text_outgone}:{user['animal_outgone']}')
	return None, None, None
