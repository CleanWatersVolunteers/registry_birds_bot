from dotenv import load_dotenv

load_dotenv()

import csv
import sys
from exchange_storage import ExchangeStorage

NO_DATA = 'Не указано'
YEAR = '.2025'
REGISTRATION_ARM_ID = 1
CLINIC_ARM_ID = 3
DIVISION = 700
GONE_TIME = '12:00'
TG_NICKNAME = 'RegisterScript'


def getDateTime(date, time):
	if len(date) == 0 or len(time) == 0:
		return None
	else:
		return f"{date}{YEAR} {time}"


# code,capture_date,capture_time,registration_date,registration_time,species,place,catcher,weight
# dead_date	dead_time
# 234,07.03,12:50,16:45,Чомга,Пляж
# name, old_number
def process_csv(file_name):
	with (open(file_name, mode='r', encoding='utf-8') as file):
		row_count = 0  # Считаем количество строк
		invalid_count = 0
		animal_count = 0
		registration_count = 0
		clinic__count = 0
		dead_count = 0

		start_qr = 60
		code = None
		reader = csv.DictReader(file)  # Читаем файл как словарь, используя первую строку как заголовки
		for row in reader:
			row_count += 1

			capture = getDateTime(row['capture_date'], row['capture_time'])
			registration = getDateTime(row['registration_date'], row['registration_time'])

			if capture is None or registration is None or 'number' not in row:
				invalid_count += 1
				print(f'Нет данных для добавления: {row}')
				continue

			dead = getDateTime(row['dead_date'], row['dead_time'])
			clinic = getDateTime(row['clinic_date'], row['clinic_time'])
			gone = getDateTime(row['gone_date'], GONE_TIME)
			gone_info = row['gone_info']

			if len(row['weight']) > 0:
				weight = row['weight']
			else:
				weight = None

			species = row['species']
			place = row['place']

			if 'catcher' in row:
				catcher = row['catcher']
			else:
				catcher = NO_DATA

			if 'degree_pollution' in row:
				pollution = f'{row['degree_pollution'].strip()}'
			else:
				pollution = NO_DATA

			number = row['number']
			if int(number) >= DIVISION:
				old_animal = ExchangeStorage.getAnimal(code=number)
			else:
				if 'number' in row and 'name' in row:
					name = f'{row['number'].strip()} - {row['name'].strip()}'
				else:
					name = None
				old_animal = ExchangeStorage.getAnimal(name=name)

			if old_animal is None:
				if int(number) < DIVISION and code is None:
					code = start_qr
				animal_id = ExchangeStorage.insertAnimal(code=code,
														 capture_datetime=capture,
														 place=place,
														 species=species,
														 catcher=catcher,
														 weight=weight,
														 name=name,
														 pollution=pollution)
				if animal_id is not None:
					code += 1
					animal_count += 1

					registration_result = ExchangeStorage.importPlaceHistory(animal_id=animal_id, date=registration,
																			 tg_nickname=TG_NICKNAME,
																			 arm_id=REGISTRATION_ARM_ID)
					if registration_result is not None:
						registration_count += 1
					clinic_result = ExchangeStorage.importPlaceHistory(animal_id=animal_id, date=clinic,
																	   tg_nickname=TG_NICKNAME,
																	   arm_id=CLINIC_ARM_ID)
					if clinic_result is not None:
						clinic__count += 1

					if dead:
						dead_result = ExchangeStorage.insertDead(animal_id, dead, CLINIC_ARM_ID, TG_NICKNAME)
						if dead_result is not None:
							dead_count += 1
					if gone:
						gone_result = ExchangeStorage.insertOutside(code, gone, CLINIC_ARM_ID, TG_NICKNAME, gone_info)



			else:
				if registration is not None:
					has_reg = ExchangeStorage.getPlaceHistory(old_animal.id, REGISTRATION_ARM_ID)
					if has_reg is None:
						registration_result = ExchangeStorage.importPlaceHistory(animal_id=old_animal.id,
																				 date=registration,
																				 tg_nickname=TG_NICKNAME,
																				 arm_id=REGISTRATION_ARM_ID)
						if registration_result is not None:
							registration_count += 1

				if clinic is not None:
					has_clinic = ExchangeStorage.getPlaceHistory(old_animal.id, CLINIC_ARM_ID)
					if has_clinic is None:
						clinic_result = ExchangeStorage.importPlaceHistory(animal_id=old_animal.id, date=clinic,
																		   tg_nickname=TG_NICKNAME,
																		   arm_id=CLINIC_ARM_ID)
						if clinic_result is not None:
							clinic__count += 1

				if dead is not None:
					has_dead = ExchangeStorage.getDeadInfo(old_animal.id)
					if has_dead is None:
						dead_result = ExchangeStorage.insertDead(old_animal.id, dead, CLINIC_ARM_ID, TG_NICKNAME)
						if dead_result is not None:
							dead_count += 1
				if gone is not None:
					gone_outside = ExchangeStorage.getAnimalOutside(old_animal.id)
					if gone_outside is None:
						gone_result = ExchangeStorage.insertOutside(code, gone, CLINIC_ARM_ID, TG_NICKNAME, gone_info)
	print(
		f'Всего: {row_count}, animal_count: {animal_count}, registration_count: {registration_count}, dead_result: {dead_count}. Пропущено: {invalid_count}')


# Пример использования
if __name__ == "__main__":
	if len(sys.argv) != 2:
		print("Использование: python register.py <nickname> <имя_файла>")
		sys.exit(1)

	file_name = sys.argv[1]  # Получаем имя файла из аргументов командной строки
	process_csv(file_name)
