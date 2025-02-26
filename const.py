# Константы
from datetime import datetime, timedelta

import pytz


class const:
	text_done = 'Готово'
	text_cancel = 'Отмена'
	text_ok = 'OK'
	text_incorrect = 'Неверный ввод:'
	text_animal_number = 'Животное №:'
	text_exit = 'Выход'
	animal_not_found = '❌ Животное с номером {code} не найдено!'
	manipulation_not_found = '❌ Манипуляции не найдены!'
	text_manipulation_done = "Выполните необходимые манипуляции и нажмите 'Готово'"
	text_data_check = "Проверьте, что данные введены верно и нажмите 'Готово'\n"
	text_capture_time = "Время отлова"
	text_capture_place = "Место отлова"
	text_today = 'Сегодня'

	datetime_short_format = "%d.%m.%y %H:%M"
	datetime_format = "%d.%m.%Y %H:%M"
	time_format = "%H:%M"
	date_format = "%d.%m.%Y"
	now = lambda: datetime.utcnow().astimezone(pytz.timezone('Etc/GMT-6')).strftime("%Y.%m.%d %H:%M")
	today = datetime.utcnow().astimezone(pytz.timezone('Etc/GMT-6')).strftime(date_format)
	tomorrow = (datetime.utcnow().astimezone(pytz.timezone('Etc/GMT-6')) + timedelta(days=1)).strftime(date_format)
