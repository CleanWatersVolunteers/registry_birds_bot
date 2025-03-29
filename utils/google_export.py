from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

import csv

from exchange_storage import ExchangeStorage
from utils.spreadsheets import exportAnimalList, exportDeadAnimalList, exportOutsideAnimalList


def save_animals_to_csv():
	"""
	Метод для сохранения списка животных в CSV-файл.
	Имя файла формируется в формате "yy-mm-dd-google.csv".
	"""
	animals = ExchangeStorage.get_animals_list()

	if not animals:
		print("Список животных пуст. CSV-файл не создан.")
		return

	current_date = datetime.now()
	file_name = current_date.strftime("%y-%m-%d") + "-google.csv"

	headers = [
		"bar_code",
		"place_capture",
		"capture_datetime",
		"place_history_datetime",
		"degree_pollution",
		"species",
		"catcher"
	]

	try:
		with open(file_name, mode="w", newline="", encoding="utf-8") as file:
			writer = csv.DictWriter(file, fieldnames=headers, delimiter=",")
			writer.writeheader()
			writer.writerows(animals)

		print(f"Список животных успешно сохранен в файл: {file_name}")
	except Exception as e:
		print(f"Ошибка при сохранении данных в CSV-файл: {e}")


def save_to_google_sheet():
	"""
	Метод для сохранения списка животных в google-таблицу.
	"""
	animals = ExchangeStorage.get_animals_list()
	if not animals:
		print("Список животных пуст.")
		return
	print(f'В работе {len(animals)} животных')
	exportAnimalList(animals)

def save_dead_google_sheet():
	"""
	Метод для сохранения списка животных в google-таблицу.
	"""
	animals = ExchangeStorage.get_animals_dead_list()
	if not animals:
		print("Список животных пуст.")
		return
	print(f'В работе {len(animals)} мертвых животных')
	exportDeadAnimalList(animals)

def save_outside_google_sheet():
	"""
	Метод для сохранения списка животных в google-таблицу.
	"""
	animals = ExchangeStorage.get_animals_outside()
	if not animals:
		print("Список животных пуст.")
		return
	print(f'В работе {len(animals)} выпущенных животных')
	exportOutsideAnimalList(animals)


if __name__ == "__main__":
	save_to_google_sheet()
	save_dead_google_sheet()
	save_outside_google_sheet()
