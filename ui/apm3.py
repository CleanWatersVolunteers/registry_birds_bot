# Прием в стационар

from database import Database as db
from storage import storage

apm3_text_header = "Животное №:"
apm3_text = f"Введите массу животного в граммах"
apm3_text_ok = 'OK'
apm3_text_done = 'Готово'
apm3_text_cancel = 'Отмена'
apm3_text_incorrect = "Неверный ввод:"


##################################
# Global API
##################################

def apm3_start(username, text, key=None):
	user = db.get_user(username)
	if key is None:
		code = text
		animal = storage.get_animal_by_bar_code(text)
		if animal is None:
			return (
				f'❌ Животное с номером {code} не найдено!',
				{apm3_text_ok: "entry_cancel"},
				None
			)
		user["animal_id"] = animal['animal_id']
		return (
			f'{apm3_text_header} {text}\n{apm3_text}',
			{apm3_text_cancel: "entry_cancel"},
			'apm3_weight'
		)
	if key == 'apm3_weight':
		if not text.isdigit():
			return (
				f'{apm3_text_incorrect} {text}\n{apm3_text}',
				{apm3_text_cancel: "entry_cancel"},
				'apm3_weight'
			)
		user['weight'] = text
		return (
			f'✅ Вес животного: {text} грамм',
			{apm3_text_done: "apm3_done", apm3_text_cancel: "entry_cancel"},
			None
		)
	return None, None


def apm3_entry(username, msg, key):
	user = db.get_user(username)
	if key == "apm3_done":
		# todo Использовать arm_id из базы #154
		place_id = 2
		location_id = 0
		arm_id = storage.get_arm_id(place_id, location_id)
		# todo Использовать arm_id из базы #154
		storage.insert_place_history(arm_id, user["animal_id"], username)
		storage.update_animal(user["animal_id"], weight=user['weight'])
		user['weight'] = None  # todo Мало того что оно к user не относится, так еще и сохраняется при смене животного.
	return None, None
