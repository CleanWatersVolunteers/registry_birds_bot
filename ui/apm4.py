# Первичка в стационаре

from const import const
from database import Database as db
from storage import storage
from tools import Tools

# БД manipulations.id
body_condition_manipulations_id = 8
mucous_manipulations_id = 9

# БД values_history_type.id
body_condition_history_type_id = 4
mucous_history_type_id = 5

apm4_place_id = 4
apm4_text_triage = '⚠️ Укажите триаж животного'
apm4_body_condition = 'Укажите степень упитанности'
apm4_text_mucous = 'Укажите состояние слизистой'

apm4_body_condition_list = ['1', '2', '2.5', '3', '3.5', '4', '4.5', '5']


def get_body_condition_list():
	kbd = dict()
	for i in range(len(apm4_body_condition_list)):
		kbd[apm4_body_condition_list[i]] = f'apm4_condition_{i}'
	kbd[const.text_cancel] = "entry_cancel"
	text = f'{apm4_body_condition}'
	return text, kbd, None


def show_mpls(user, mpls):
	kbd = dict()
	text = f'{const.text_animal_number} {user["bar_code"]}\n'
	for mpl in mpls:  # {'id':'1', "name":"манипуляция 1"}
		if ('mpl_list' in user
				and str(mpl['id']) in user['mpl_list']):
			text += f'✅ {mpl['name']}\n'
		else:
			kbd[mpl['name']] = f'apm4_mpl_{mpl["id"]}'
	kbd['Готово'] = 'entry_cancel'
	text += f'{const.text_manipulation_done}'
	return text, kbd


def get_mucous(user):
	return (
		f'{const.text_animal_number} {user["bar_code"]}\n{apm4_text_mucous}',
		{const.text_cancel: "entry_cancel"},
		'apm4_mucous'
	)


##################################
# Global API
##################################

def apm4_start(username, text, key=None):
	user = db.get_user(username)
	if key == 'apm4_mucous':
		storage.insert_value_history(animal_id=user["animal_id"], type_id=mucous_history_type_id, value=text,
									 tg_nickname=username)
	if key is None:
		checkDead = Tools.checkDead(text)
		if checkDead is not False:
			return checkDead
		animal = storage.get_animal_by_bar_code(text)
		if animal == {}:
			return (
				const.animal_not_found.format(code=text),
				{const.text_ok: "entry_cancel"},
				None
			)
		user['animal_id'] = animal['animal_id']
		user['bar_code'] = text
		user['mpl_list'] = []
		if animal['triage'] is None:
			return (
				f'{const.text_animal_number} {user["bar_code"]}\n{apm4_text_triage}',
				{
					const.text_triage_green: "apm4_triage_green",
					const.text_triage_yellow: "apm4_triage_yellow",
					const.text_triage_red: "apm4_triage_red",
					const.text_cancel: "entry_cancel"
				},
				None
			)
	mpls = storage.get_manipulations(apm4_place_id)
	if len(mpls) == 0:
		return (
			const.manipulation_not_found,
			{const.text_exit: "entry_cancel"}, None
		)
	text, kbd = show_mpls(user, mpls)
	return text, kbd, None


def apm4_button(username, text, key):
	user = db.get_user(username)
	if key == 'apm4_triage_green':
		storage.update_animal(user["animal_id"], triage=1)
	elif key == 'apm4_triage_yellow':
		storage.update_animal(user["animal_id"], triage=2)
	elif key == 'apm4_triage_red':
		storage.update_animal(user["animal_id"], triage=3)
	elif 'apm4_condition_' in key:
		body_condition = apm4_body_condition_list[int(key.split('_')[-1])]
		storage.insert_value_history(animal_id=user["animal_id"], type_id=body_condition_history_type_id,
									 value=body_condition,
									 tg_nickname=username)
	else:
		key_id = key.split('_')[-1]
		user['mpl_list'].append(key_id)
		if int(key_id) == body_condition_manipulations_id:
			return get_body_condition_list()
		elif int(key_id) == mucous_manipulations_id:
			return get_mucous(user)
		storage.insert_history(
			manipulation_id=key_id,
			animal_id=user["animal_id"],
			arms_id=user["apm"]["arm_id"],
			tg_nickname=username
		)

	mpls = storage.get_manipulations(apm4_place_id)
	text, kbd = show_mpls(user, mpls)
	return text, kbd, None
