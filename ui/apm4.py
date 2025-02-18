# Первичка в стационаре

from database import Database as db
from storage import storage
from const import const

apm4_place_id = 3


def show_mpls(user, mpls):
	kbd = dict()
	text = f'{const.text_animal_number} {user["bar_code"]}\n'
	for mpl in mpls:  # {'id':'1', "name":"манипуляция 1"}
		if str(mpl["id"]) in user["mpl_list"]:
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
	# get manipulation list
	mpls = storage.get_manipulations(apm4_place_id)
	if len(mpls) == 0:
		return (
			"❌ Манипуляции не найдены!",
			{const.text_exit: "entry_cancel"}, None
		)
	text, kbd = show_mpls(user, mpls)
	return text, kbd, None


def apm4_entry(username, text, key):
	user = db.get_user(username)
	id = key.split('_')[-1]
	user["mpl_list"].append(id)
	storage.insert_history(
		manipulation_id=id,
		animal_id=user["animal_id"],
		arms_id=user["apm"]["arm_id"],
		tg_nickname=username
	)
	mpls = storage.get_manipulations(apm4_place_id)
	text, kbd = show_mpls(user, mpls)
	return text, kbd, None
