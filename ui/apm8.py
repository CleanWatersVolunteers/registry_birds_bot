from const import const
from database import Database as db
from storage import storage
from tools import Tools

apm8_place_id = 8

apm8_text_confirm = 'Подтвердите поступление'


##################################
# Global API
##################################

def apm8_start(username, text, key=None):
	user = db.get_user(username)
	check_dead = Tools.checkDead(text)
	if check_dead is not False:
		return check_dead
	animal = storage.get_animal_by_bar_code(text)
	if animal is None:
		return (
			const.animal_not_found.format(code=text),
			{const.text_ok: "entry_cancel"},
			None
		)
	user["animal_id"] = animal['animal_id']
	return (
		f'{const.text_animal_number}{animal["bar_code"]}\n{apm8_text_confirm}',
		{const.text_done: "apm8_done", const.text_cancel: "entry_cancel"},
		None
	)


def apm8_button(username, text, key):
	user = db.get_user(username)
	# todo Использовать arm_id из базы #154
	arm_id = storage.get_arm_id(apm8_place_id, user["location_id"])
	# todo Использовать arm_id из базы #154
	storage.insert_place_history(arm_id, user["animal_id"], username)
	return None, None, None
