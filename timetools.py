import re
from datetime import datetime, timedelta

from const import const

GET_TIME = lambda text: re.search(r'(\d{1,2})[.:,\s](\d{1,2})', text)
GET_DATETIME = lambda text: re.search(r'\d{2}\.\d{2}\.\d{4} \d{1,2}:\d{1,2}', text)

SECONDS_IN_DAY = 24 * 60 * 60
SECONDS_IN_HOUR = 3600


def tomorrow():
	return (datetime.now().date() + timedelta(days=1)).strftime(const.date_format)


def today():
	return datetime.now().strftime(const.date_format)


def now():
	return datetime.now().strftime(const.datetime_format)


def yesterday():
	return (datetime.now().date() - timedelta(days=1)).strftime(const.date_format)


def week_db():
	return (datetime.now().date() - timedelta(days=7)).strftime("%Y.%m.%d")


def yesterday_db():
	return (datetime.now().date() - timedelta(days=1)).strftime(const.date_db_format)


def today_db():
	return (datetime.now().date()).strftime(const.date_db_format)


def now_db():
	return datetime.now().strftime("%Y.%m.%d %H:%M")


class TimeTools:

	@classmethod
	def createFullDate(cls, date, time):
		return GET_DATETIME(f'{date} {time}').string

	@classmethod
	def getTime(cls, time):
		match = GET_TIME(time)
		if match:
			hours, minutes = map(int, match.groups())  # Извлекаем часы и минуты как числа
			# Проверяем корректность времени
			if 0 <= hours <= 23 and 0 <= minutes <= 59:
				# Форматируем в ЧЧ:ММ, добавляя ведущие нули при необходимости
				return f"{hours:02d}:{minutes:02d}"
		return None

	# Преобразуем строки в формат datetime
	@classmethod
	def getDateTime(cls, value):
		return datetime.strptime(value, const.datetime_format)

	@classmethod
	def formatTimeInterval(cls, capture_datetime):
		delta = datetime.now() - capture_datetime
		total_seconds = int(delta.total_seconds())

		if total_seconds < SECONDS_IN_DAY:  # Менее 24 часов
			hours = total_seconds // SECONDS_IN_HOUR
			return f"{hours} ч."
		else:  # 24 часа и более
			days = delta.days
			remaining_hours = (total_seconds % (SECONDS_IN_DAY)) // SECONDS_IN_HOUR
			return f"{days} дн. {remaining_hours} ч."
