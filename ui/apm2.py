# Первичка на мойке

from database import Database as db
from storage import storage

apm2_text_animal_header = "Животное №:"
apm2_text = f"Выполните необходимые манипуляции и нажмите 'Готово'"
apm2_text_done = 'Готово'
apm2_text_cancel = 'Отмена'


##################################
# Global API
##################################

def apm2_start(username, text, key=None):
	user = db.get_user(username)
	animal = storage.get_animal_by_bar_code(text)
	if animal is not None:
		user["animal_id"] = animal['animal_id']
	if user["animal_id"] is None:
		return (
			f'❌ Животное с номером {text} не найдено!',
			{apm2_text_cancel: "entry_cancel"}, None
		)
	return (
		f'{apm2_text_animal_header}{animal["bar_code"]}\n{apm2_text}',
		{apm2_text_done: "apm2_done", apm2_text_cancel: "entry_cancel"},
		None
	)


def apm2_entry(username, text, key):
	user = db.get_user(username)
	print(username)
	# todo Получать arm_id из базы
	arm_id = 1
	storage.insert_place_history(arm_id, user["animal_id"], username)
	return None, None
