
from const import const

code_animal_text = 'Введите код животного'

def code_request(apm_list):
	if len(apm_list) > 1:
		return code_animal_text, {const.text_cancel:'entry_menu'}
	return code_animal_text, {const.text_exit:'entry_exit'}

def code_parse(code)->int:
	if isinstance(code, str):
		if code.isdigit():
			return int(code)
	return 0
	
