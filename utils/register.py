from dotenv import load_dotenv

load_dotenv()

import csv
import sys
from exchange_storage import ExchangeStorage

DEFAULT_POLLUTION = 'Нет'
YEAR = '.2025'


# code,date,capture_time,registration_time,species,place,catcher
# 234,07.03,12:50,16:45,Чомга,Пляж
def process_csv(nickname, file_name):
	with open(file_name, mode='r', encoding='utf-8') as file:
		row_count = 0  # Считаем количество строк
		animal_count = 0
		place_count = 0
		reader = csv.DictReader(file)  # Читаем файл как словарь, используя первую строку как заголовки
		for row in reader:
			row_count += 1
			# Извлекаем значения из строки и подготавливаем даты
			code = row['code']
			date = row['date'] + YEAR  # Добавляем год к дате
			capture_time = row['capture_time']
			registration_time = row['registration_time']
			species = row['species']
			place = row['place']
			if 'catcher' in row:
				catcher = row['catcher']
			else:
				catcher = 'нет'

			# Форматируем даты и времена
			capture_date = f"{date} {capture_time}"
			registration_date = f"{date} {registration_time}"
			# Сохраняем значения в словарь
			result_dict = {
				'code': code,
				'capture_datetime': capture_date,
				'registration_date': registration_date,
				'species': species,
				'place': place,
				'pollution': DEFAULT_POLLUTION,
				'catcher': catcher
			}
			animal_result = ExchangeStorage.insert_animal(code=result_dict["code"],
														  capture_datetime=result_dict["capture_datetime"],
														  place=result_dict["place"],
														  species=result_dict["species"],
														  catcher=result_dict["catcher"],
														  pollution=result_dict["pollution"])
			if animal_result is not None:
				animal_count += 1

			place_result = ExchangeStorage.import_place_history(code=result_dict["code"],
																registration_datetime=result_dict["registration_date"],
																tg_nickname=nickname, arm_id=1)
			if place_result is not None:
				place_count += 1
	print(f'Всего: {row_count}, animal_count: {animal_count}, place_count: {place_count}')


# Пример использования
if __name__ == "__main__":
	if len(sys.argv) != 3:
		print("Использование: python register.py <nickname> <имя_файла>")
		sys.exit(1)

	nickname = sys.argv[1]
	file_name = sys.argv[2]  # Получаем имя файла из аргументов командной строки
	result = process_csv(nickname, file_name)
