# Первичка на мойке

from const import const
from database import Database as Db
from storage import Storage
from tools import Tools

apm2_place_id = 2


##################################
# Global API
##################################

def apm2_start(user_id, text, key=None):
	user = Db.get_user(user_id)
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
	user["animal_id"] = animal['animal_id']
	return (
		f'{const.text_animal_number}{animal["bar_code"]}\n{const.text_manipulation_done}',
		{const.text_done: "apm2_done", const.text_cancel: "entry_cancel"},
		None
	)


def apm2_button(user, text, key):
	# todo Использовать arm_id из базы #154
	arm_id = Storage.get_arm_id(apm2_place_id, user["location_id"])
	# todo Использовать arm_id из базы #154
	Storage.insert_place_history(arm_id, user["animal_id"], user['name'])
	return None, None, None
