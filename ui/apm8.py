# Генерация QR

from database import Database as db
from storage import storage
from const import const

gen_text_sel_mode = "📌 Выберите способ генерации QR-кодов"

gen_kbd_sel_mode = {
	"Старые QR":"apm8_old",
	"24 новых":"apm8_new24",
	"48 новых":"apm8_new48",
	"72 новых":"apm8_new72",
	"Отмена":"entry_cancel"
}
##################################
# Global API
##################################

def apm8_start(username, text, key=None):
	print("GEN START:", username, text, key)
	# user = db.get_user(username)
	# animal = storage.get_animal_by_bar_code(text)
	# if animal is None:
	# 	return (
	# 		const.animal_not_found.format(code=text),
	# 		{const.text_ok: "entry_cancel"},
	# 		None
	# 	)
	# user["animal_id"] = animal['animal_id']
	# return (
	# 	f'{const.text_animal_number}{animal["bar_code"]}\n{const.text_manipulation_done}',
	# 	{const.text_done: "apm2_done", const.text_cancel: "entry_cancel"},
	# 	None
	# )
	return None, None, None 


def apm8_entry(username, text, key):
	print("GEN ENTRY:", username, text, key)
	kbd = {}
	text = gen_text_sel_mode
	# kbd = gen_kbd_sel_mode
	kbd["Готово"] = "entry_menu"
	# user = db.get_user(username)
	# # todo Использовать arm_id из базы #154
	# place_id = 1
	# arm_id = storage.get_arm_id(place_id, user["location_id"])
	# # todo Использовать arm_id из базы #154
	# storage.insert_place_history(arm_id, user["animal_id"], username)
	return text, kbd, None # text, kbd, key
