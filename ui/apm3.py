# Прием в стационар

from const import const
from database import Database as Db
from storage import Storage
from tools import Tools

apm3_text = f"Введите массу животного в граммах"
apm3_place_id = 3


##################################
# Global API
##################################

def apm3_start(user_id, text, key=None):
	user = Db.get_user(user_id)
	if key is None:
		checkDead = Tools.checkDead(text)
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
				{const.text_cancel: "entry_cancel"},
				'apm3_weight'
			)
		else:
			dead_info = Storage.get_animal_dead(animal['bar_code'])
			if dead_info is None:
				return (
					f'{const.text_animal_number} {animal['bar_code']}',
					{const.text_animal_dead: 'apm3_animal_dead_confirmation', const.text_cancel: 'entry_cancel'},
					None
				)

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


def apm3_animal_dead_confirmation(user):
	return (
		f'{const.text_animal_dead_confirmation} {const.text_animal_number} {user['animal']['bar_code']}',
		{f'{const.text_ok}': f'apm3_animal_dead', f'{const.text_cancel}': "entry_apm3"},
		None
	)


def apm3_animal_dead(user):
	animal_id = user['animal']['animal_id']
	arm_id = Storage.get_arm_id(user['apm']['place_id'], user['location_id'])
	if arm_id is not None:
		Storage.create_dead_animal(animal_id, arm_id, user['name'])
	return None, None, None


def apm3_button(user, msg, key):
	if key == "apm3_done":
		# todo Использовать arm_id из базы #154
		arm_id = Storage.get_arm_id(apm3_place_id, user["location_id"])
		# todo Использовать arm_id из базы #154
		Storage.insert_place_history(arm_id, user['animal']['animal_id'], user['name'])
		Storage.update_animal(user['animal']['animal_id'], weight=user['weight'])
		user['weight'] = None  # todo Мало того что оно к user не относится, так еще и сохраняется при смене животного.
	elif key == 'apm3_animal_dead_confirmation':
		return apm3_animal_dead_confirmation(user)
	elif key == 'apm3_animal_dead':
		return apm3_animal_dead(user)
	return None, None, None
