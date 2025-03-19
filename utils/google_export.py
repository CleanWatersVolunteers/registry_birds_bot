from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

import csv

from exchange_storage import ExchangeStorage


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


if __name__ == "__main__":
	result = save_animals_to_csv()
