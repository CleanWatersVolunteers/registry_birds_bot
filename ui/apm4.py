# Первичка в стационаре

from const import const
from database import Database as db
from storage import storage
from tools import Tools

apm4_place_id = 4
apm4_text_triage = '⚠️ Укажите триаж животного'


def show_mpls(user, mpls):
	kbd = dict()
	text = f'{const.text_animal_number} {user["bar_code"]}\n'
	for mpl in mpls:  # {'id':'1', "name":"манипуляция 1"}
		if ('mpl_list' in user
				and str(mpl["id"]) in user["mpl_list"]):
			text += f'✅ {mpl["name"]}\n'
		else:
			kbd[mpl["name"]] = f'apm4_mpl_{mpl["id"]}'
	kbd["Готово"] = "entry_cancel"
	text += f'{const.text_manipulation_done}'
	return text, kbd


##################################
# Global API
##################################

def apm4_start(username, text, key=None):
	user = db.get_user(username)
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

	user["mpl_list"] = []
	# get manipulation list
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
	else:
		key_id = key.split('_')[-1]
		user["mpl_list"].append(key_id)
		storage.insert_history(
			manipulation_id=key_id,
			animal_id=user["animal_id"],
			arms_id=user["apm"]["arm_id"],
			tg_nickname=username
		)

	mpls = storage.get_manipulations(apm4_place_id)
	text, kbd = show_mpls(user, mpls)
	return text, kbd, None
