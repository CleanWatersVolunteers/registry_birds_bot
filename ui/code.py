
def code_request(apm_list):
	if len(apm_list) > 1:
		return f'Введите код животного', {'Отмена':'entry_menu'}
	return f'Введите код животного', {'Выход':'entry_exit'}

def code_parse(code)->int:
	if isinstance(code, str):
		if code.isdigit():
			return int(code)
	return 0
	
