
def code_request():
	return f'Введите код животного', {'Отмена':'entry_cancel'}

def code_parse(code)->int:
	if isinstance(code, str):
		if code.isdigit():
			return int(code)
	return 0
	
