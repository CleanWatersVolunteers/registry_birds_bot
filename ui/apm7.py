from database import Database as db

def apm7_start(username, text, key=None):
	code = text
	if db.code_is_exist(code):
		return f'Животное с номером {code} уже зарегистрировано\!', {"OK": "entry_cancel"}
	return "Exit", {"OK": "entry_cancel"}

def apm7_button(username, text, key):
	return "Exit", {"OK": "entry_cancel"}