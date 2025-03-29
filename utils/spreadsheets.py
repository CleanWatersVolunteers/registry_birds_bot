import asyncio
import os
import time

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from logs import my_logger
from timetools import today

scope = [
	"https://spreadsheets.google.com/feeds",
	"https://www.googleapis.com/auth/drive"
]

DEAD_COLUMN = 8
OUTGONE_COLUMN = 9

MAIN_GOOGLE_SHEET = os.getenv('MAIN_GOOGLE_SHEET')
MAIN_WORKSHEET_TITLE = 'Общий журнал'

VET_INCOME_GOOGLE_SHEET = os.getenv('VET_INCOME_GOOGLE_SHEET')
VET_INCOME_PREFIX = 'Поступление'
VET_OUTGONE_PREFIX = 'Убытие'


def openSheet(sheet_name):
	credentials = ServiceAccountCredentials.from_json_keyfile_name("registrybirdstest-084d0b679072.json", scope)
	client = gspread.authorize(credentials)
	try:
		spreadsheet = client.open(sheet_name)
		return spreadsheet
	except Exception as e:
		my_logger.error(f"openSheet Ошибка открытия таблицы: {sheet_name} - {e}")
		return None


def ensure_worksheet_exists(spreadsheet, worksheet_title, titles=None):
	try:
		# Попытка получить вкладку по названию
		worksheet = spreadsheet.worksheet(worksheet_title)
		my_logger.debug(f"Вкладка '{worksheet_title}' уже существует.")
		return worksheet
	except gspread.exceptions.WorksheetNotFound:
		# Если вкладка не найдена, создаём новую
		if titles is not None:
			worksheet = spreadsheet.add_worksheet(title=worksheet_title, rows="100", cols=len(titles))
			worksheet.append_row(titles)
			my_logger.debug(f"Вкладка '{worksheet_title}' создана.")
			return worksheet
		else:
			return None


def asyncExportDeadAnimal(code, date_time):
	asyncio.create_task(asyncio.to_thread(
		exportDeadAnimal, code, date_time)
	)


def exportDeadAnimal(code, date_time):
	spreadsheet = openSheet(MAIN_GOOGLE_SHEET)
	if spreadsheet is not None:
		worksheet = ensure_worksheet_exists(spreadsheet, MAIN_WORKSHEET_TITLE)
		if worksheet is not None:
			cell = worksheet.find(str(code), in_column=1)
			if cell:
				my_logger.debug(f"Найдено в строке {cell.row}, столбце {cell.col}")
				result = worksheet.update_cell(cell.row, DEAD_COLUMN, date_time)
				my_logger.debug(f'exportDeadAnimal, изменен: {result['updatedRange']}')
			else:
				my_logger.debug(f'exportDeadAnimal, не найдено животное: {code}')


def asyncExportOutgoneAnimal(code, date_time, reason):
	asyncio.create_task(asyncio.to_thread(
		exportOutgoneAnimal, code, date_time, reason)
	)


def exportOutgoneAnimal(code, date_time, reason):
	spreadsheet = openSheet(MAIN_GOOGLE_SHEET)
	if spreadsheet is not None:
		worksheet = ensure_worksheet_exists(spreadsheet, MAIN_WORKSHEET_TITLE)
		if worksheet is not None:
			cell = worksheet.find(str(code), in_column=1)
			if cell:
				my_logger.debug(f"Найдено в строке {cell.row}, столбце {cell.col}")
				worksheet.update_cell(cell.row, OUTGONE_COLUMN, date_time)
				result = worksheet.update_cell(cell.row, OUTGONE_COLUMN + 1, reason)
				my_logger.debug(f'exportDeadAnimal, изменен: {result['updatedRange']}')
			else:
				my_logger.debug(f'exportDeadAnimal, не найдено животное: {code}')


def exportNewAnimal(code, place, capture_datetime, register_datetime, pollution, species, catcher):
	time.sleep(1)
	spreadsheet = openSheet(MAIN_GOOGLE_SHEET)
	if spreadsheet is not None:
		titles = ['Номер птицы', 'Место отлова', 'Время отлова', 'Время поступления', 'Степень загрязнения', 'Вид',
				  'Время гибели', 'Время отбытия', 'Отбытие']
		worksheet = ensure_worksheet_exists(spreadsheet, MAIN_WORKSHEET_TITLE, titles)
		if worksheet is not None:
			addNewAnimal(worksheet, code, place, capture_datetime, register_datetime, pollution, species, catcher)


def asyncExportNewAnimal(code, place, capture_datetime, register_datetime, pollution, species, catcher):
	asyncio.create_task(asyncio.to_thread(
		exportNewAnimal, code, place, capture_datetime, register_datetime, pollution, species, catcher)
	)


def exportAnimalList(animals):
	if animals is not None:
		spreadsheet = openSheet(MAIN_GOOGLE_SHEET)
		if spreadsheet is not None:
			worksheet = ensure_worksheet_exists(spreadsheet, MAIN_WORKSHEET_TITLE)
			if worksheet is not None:
				first_column_data = worksheet.col_values(1)  # Получаем все значения из первого столбца
				# и оставляем только те что еще не были вставлены
				filtered_data = [
					item for item in animals if str(item["bar_code"]) not in first_column_data
				]
				if filtered_data:
					try:
						for animal in filtered_data:
							addNewAnimal(worksheet, animal['bar_code'], animal['place_capture'],
										 animal['capture_datetime'],
										 animal['place_history_datetime'], animal['degree_pollution'],
										 animal['species'],
										 animal['catcher'])
					except Exception as e:
						my_logger.error(f'Ошибка вставки данных в таблицу экспорта: [{MAIN_GOOGLE_SHEET}] - {e}')
					return
				else:
					my_logger.debug(f'Все данные экспортированы')
	else:
		my_logger.debug(f'Пустой список для экспорта')


def addNewAnimal(sheet, code, place, capture_datetime, register_datetime, pollution, species, catcher):
	new_row = [code, place, capture_datetime, register_datetime, pollution, species, catcher]
	res = sheet.append_row(new_row)
	my_logger.debug(f'exportNewAnimal res: {res}')


def asyncAddVetIncome(code, register_datetime):
	asyncio.create_task(asyncio.to_thread(
		addVetIncome, code, register_datetime)
	)


def addVetIncome(code, register_datetime):
	time.sleep(1)
	spreadsheet = openSheet(VET_INCOME_GOOGLE_SHEET)
	if spreadsheet is not None:
		titles = ['Номер птицы', 'Время поступления', 'Дата отбора ВПГП']
		worksheet = ensure_worksheet_exists(spreadsheet, f'{VET_INCOME_PREFIX} - {today()}', titles)
		new_row = [code, register_datetime]
		res = worksheet.append_row(new_row)
		my_logger.debug(f'addVetIncome res: {res}')


def asyncAddVetOutgone(code, register_datetime, outgone_datetime, reason=None):
	asyncio.create_task(asyncio.to_thread(
		addVetOutgone, code, register_datetime, outgone_datetime, reason)
	)


def addVetOutgone(code, register_datetime, outgone_datetime, reason):
	time.sleep(1)
	spreadsheet = openSheet(VET_INCOME_GOOGLE_SHEET)
	if spreadsheet is not None:
		if reason is None:
			reason = 'гибель'
		titles = ['Номер птицы', 'Время поступления', 'Время убытия', 'Причина']
		worksheet = ensure_worksheet_exists(spreadsheet, f'{VET_OUTGONE_PREFIX} - {today()}', titles)
		new_row = [code, register_datetime, outgone_datetime, reason]
		res = worksheet.append_row(new_row)
		my_logger.debug(f'addVetOutgone res: {res}')
