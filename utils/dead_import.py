from dotenv import load_dotenv

load_dotenv()

import csv
import sys
from exchange_storage import ExchangeStorage


# code,date,time
# 234,07.03,16:45
def process_csv(nickname, file_name):
	with open(file_name, mode='r', encoding='utf-8') as file:
		row_count = 0  # Считаем количество строк
		registration_count = 0
		reader = csv.DictReader(file)  # Читаем файл как словарь, используя первую строку как заголовки
		for row in reader:
			row_count += 1
			'code'
			# Извлекаем значения из строки и подготавливаем даты
			code = row['code']
			date = row['date'] + '.2025'  # Добавляем год к дате
			time = row['time']

			# Форматируем даты и времена
			dead_datetime = f"{date} {time}"
			arms_id = 1
			result = ExchangeStorage.insert_dead(code, dead_datetime, arms_id, nickname)
			if result is not None:
				registration_count += 1
	print(f'Всего: {row_count}, зарегистрировано: {registration_count}')


# Пример использования
if __name__ == "__main__":
	if len(sys.argv) != 3:
		print("Использование: python dead_import.py <nickname> <имя_файла>")
		sys.exit(1)

	nickname = sys.argv[1]
	file_name = sys.argv[2]  # Получаем имя файла из аргументов командной строки
	result = process_csv(nickname, file_name)
