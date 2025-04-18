from const import const
from database import Database as Db
from storage import Storage
from tools import Tools

apm8_text_confirm = 'Подтвердите поступление'


##################################
# Global API
##################################

def apm8_start(user_id, text, key=None):
	user = Db.get_user(user_id)
	check_dead = Tools.checkLeave(text)
	if check_dead is not False:
		return check_dead
	animal = Storage.get_animal_by_bar_code(text)
	if animal == {}:
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


def apm8_button(user, text, key):
	Storage.insert_place_history(user['apm']['arm_id'], user["animal_id"], user['name'])
	return None, None, None
