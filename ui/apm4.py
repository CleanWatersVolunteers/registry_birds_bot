# Первичка в стационаре

from database import Database as db
from storage import storage

apm4_place_id = 4
apm4_text = "Выберите манипуляцию:\n"

def show_mpls(user, mpls):
	kbd = dict()
	text = ''
	for mpl in mpls: # {'id':'1', "name":"манипуляция 1"}
		if mpl["id"] in user["mpl_list"]:
			text += f'✅ {mpl["name"]}\n'
		else:
			kbd[mpl["name"]] = f'apm4_mpl_{mpl["id"]}'
	kbd["Готово"] = "entry_cancel"
	text += apm4_text
	return text, kbd

##################################
# Global API
##################################

def apm4_start(username, text, key=None):
	user = db.get_user(username)
	if user["animal_id"] == None:
		user["animal_id"] = storage.get_animal_id(text)	
		if user["animal_id"] == None:
			return (
				f'❌ Животное с номером {text} не найдено!',
				{"Отмена": "entry_cancel"}, None
			)
		user["mpl_list"] = []
	# get manipulation list
	mpls = storage.get_manipulations(apm4_place_id)
	if len(mpls) == 0:
		return (
			"❌ Манипуляции не найдены!",
			{"Выход": "entry_cancel"}, None
		)
	text,kbd = show_mpls(user, mpls)
	return text, kbd, None

def apm4_entry(username, text, key):
	user = db.get_user(username)
	id = key.split('_')[-1]
	user["mpl_list"].append(id)
	storage.insert_history(
		manipulation_id=id,
		animal_id = user["animal_id"],
		arms_id = user["apm"]["arm_id"],
		tg_nickname = username
	)
	mpls = storage.get_manipulations(apm4_place_id)
	text,kbd = show_mpls(user, mpls)
	return text,kbd
