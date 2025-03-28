import os

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from timetools import today

scope = [
	"https://spreadsheets.google.com/feeds",
	"https://www.googleapis.com/auth/drive"
]

DEAD_COLUMN = 8

MAIN_GOOGLE_SHEET = os.getenv('MAIN_GOOGLE_SHEET')
VET_INCOME_GOOGLE_SHEET = os.getenv('VET_INCOME_GOOGLE_SHEET')


def openSheet(sheet_name):
	credentials = ServiceAccountCredentials.from_json_keyfile_name("registrybirdstest-084d0b679072.json", scope)
	client = gspread.authorize(credentials)
	try:
		spreadsheet = client.open(sheet_name)
		return spreadsheet
	except Exception as e:
		print(f"Ошибка открытия таблицы: {MAIN_GOOGLE_SHEET} - {e}")
		return None


def ensure_worksheet_exists(spreadsheet, worksheet_title, titles):
	try:
		# Попытка получить вкладку по названию
		worksheet = spreadsheet.worksheet(worksheet_title)
		print(f"Вкладка '{worksheet_title}' уже существует.")
	except gspread.exceptions.WorksheetNotFound:
		# Если вкладка не найдена, создаём новую
		worksheet = spreadsheet.add_worksheet(title=worksheet_title, rows="100", cols=len(titles))
		worksheet.append_row(titles)
		print(f"Вкладка '{worksheet_title}' создана.")
	return worksheet


def getSheet(sheet_name, page_name=None):
	credentials = ServiceAccountCredentials.from_json_keyfile_name("registrybirdstest-084d0b679072.json", scope)
	client = gspread.authorize(credentials)
	try:
		if page_name is None:
			sheet = client.open(sheet_name).sheet1
		else:
			sheet = client.open(sheet_name).worksheet(page_name)
		return sheet
	except Exception as e:
		print(f"Ошибка открытия таблицы: {MAIN_GOOGLE_SHEET} - {e}")
		return None


def exportDeadAnimal(code, date_time):
	sheet = getSheet(MAIN_GOOGLE_SHEET)
	if sheet is not None:
		cell = sheet.find(str(code), in_column=1)
		if cell:
			print(f"Найдено в строке {cell.row}, столбце {cell.col}")
			result = sheet.update_cell(cell.row, DEAD_COLUMN, date_time)  # Обновить ячейку A1
			print(f'exportDeadAnimal, изменен: {result['updatedRange']}')
		else:
			print(f'exportDeadAnimal, не найдено животное: {code}')


def exportNewAnimal(code, place, capture_datetime, register_datetime, pollution, species, catcher):
	sheet = getSheet(MAIN_GOOGLE_SHEET)
	if sheet is not None:
		addNewAnimal(sheet, code, place, capture_datetime, register_datetime, pollution, species, catcher)


def exportAnimalList(animals):
	if animals is not None:
		sheet = getSheet(MAIN_GOOGLE_SHEET)
		if sheet is not None:
			first_column_data = sheet.col_values(1)  # Получаем все значения из первого столбца
			# и оставляем только те что еще не были вставлены
			filtered_data = [
				item for item in animals if str(item["bar_code"]) not in first_column_data
			]
			if filtered_data:
				try:
					for animal in filtered_data:
						addNewAnimal(sheet, animal['bar_code'], animal['place_capture'], animal['capture_datetime'],
									 animal['place_history_datetime'], animal['degree_pollution'], animal['species'],
									 animal['catcher'])
				except Exception as e:
					print(f'Ошибка вставки данных в таблицу экспорта: [{MAIN_GOOGLE_SHEET}] - {e}')
				return
			else:
				print(f'Все данные экспортированы')
	else:
		print(f'Пустой список для экспорта')


def addNewAnimal(sheet, code, place, capture_datetime, register_datetime, pollution, species, catcher):
	new_row = [code, place, capture_datetime, register_datetime, pollution, species, catcher]
	res = sheet.append_row(new_row)
	print(f'exportNewAnimal res: {res}')


def addVetIncome(code, register_datetime):
	prefix = 'Поступление'
	spreadsheet = openSheet(VET_INCOME_GOOGLE_SHEET)
	if spreadsheet is not None:
		titles = ['Номер птицы', 'Время поступления', 'Дата отбора ВПГП']
		worksheet = ensure_worksheet_exists(spreadsheet, f'{prefix} - {today()}', titles)
		new_row = [code, register_datetime]
		res = worksheet.append_row(new_row)
		print(f'addVetIncome res: {res}')


def addVetOutgone(code, register_datetime, outgone_datetime, reason=None):
	prefix = 'Убытие'
	spreadsheet = openSheet(VET_INCOME_GOOGLE_SHEET)
	if spreadsheet is not None:
		if reason is None:
			reason = 'гибель'
		titles = ['Номер птицы', 'Время поступления', 'Время убытия', 'Причина']
		worksheet = ensure_worksheet_exists(spreadsheet, f'{prefix} - {today()}', titles)
		new_row = [code, register_datetime, outgone_datetime, reason]
		res = worksheet.append_row(new_row)
		print(f'addVetOutgone res: {res}')
