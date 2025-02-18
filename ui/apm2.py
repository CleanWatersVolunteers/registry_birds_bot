# Первичка на мойке

from database import Database as db
from storage import storage
from const import const


##################################
# Global API
##################################

def apm2_start(username, text, key=None):
	user = db.get_user(username)
	animal = storage.get_animal_by_bar_code(text)
	if animal is None:
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


def apm2_entry(username, text, key):
	user = db.get_user(username)
	# todo Использовать arm_id из базы #154
	place_id = 1
	location_id = 0
	arm_id = storage.get_arm_id(place_id, location_id)
	# todo Использовать arm_id из базы #154
	storage.insert_place_history(arm_id, user["animal_id"], username)
	return None, None, None
