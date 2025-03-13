# Константы
from datetime import datetime, timedelta


class const:
	text_done = 'Готово'
	text_cancel = 'Отмена'
	text_ok = 'OK'
	text_incorrect = 'Неверный ввод:'
	text_animal_number = 'Животное №:'
	text_exit = 'Выход'
	animal_not_found = '❌ Животное с номером {code} не найдено!'
	animal_is_dead = '❌ Животное {code} погибло.'
	manipulation_not_found = '❌ Манипуляции не найдены!'
	text_manipulation_done = "⚠️Выполните необходимые манипуляции и нажмите 'Готово'"
	text_data_check = "Проверьте, что данные введены верно и нажмите 'Готово'\n"
	text_capture_time = "Время отлова"
	text_capture_place = "Место отлова"
	text_today = 'Сегодня'
	text_yesterday = 'Вчера'
	text_line = '------------------------'
	text_manipulations_not_found = "Манипуляции не найдены"
	text_animal_dead = 'Гибель'
	text_animal_dead_confirmation = '⚠️ Подтвердите гибель'

	text_triage_green = 'Зеленый'
	text_triage_yellow = 'Желтый'
	text_triage_red = 'Красный'

	datetime_short_format = "%d.%m.%y %H:%M"
	datetime_format = "%d.%m.%Y %H:%M"
	time_format = "%H:%M"
	date_format = "%d.%m.%Y"
	date_db_format = "%Y.%m.%d"

	now = datetime.now().strftime(datetime_format)
	today = datetime.now().strftime(date_format)
	yesterday = (datetime.now().date() - timedelta(days=1)).strftime(date_format)
	tomorrow = (datetime.now().date() + timedelta(days=1)).strftime(date_format)
	week_db = (datetime.now().date() - timedelta(days=7)).strftime("%Y.%m.%d")

	yesterday_db = (datetime.now().date() - timedelta(days=1)).strftime(date_db_format)
	today_db = (datetime.now().date()).strftime(date_db_format)
	now_db = datetime.now().strftime("%Y.%m.%d %H:%M")

	history_type_weight = 2
