import re
from datetime import datetime

from const import const

GET_DATE = lambda text: re.search(r'\d{2}\.\d{2}\.\d{4}', text)
GET_TIME = lambda text: re.search(r'\d{1,2}:\d{1,2}', text)
GET_DATETIME = lambda text: re.search(r'\d{2}\.\d{2}\.\d{4} \d{1,2}:\d{1,2}', text)


class TimeTools:

	@classmethod
	def createFullDate(cls, date, time):
		return GET_DATETIME(f'{date} {time}').string

	@classmethod
	def getDate(cls, value: str):
		date = GET_DATE(value)
		if date:
			date = date[0]
			if not cls.isValidDatetime(date, const.date_format):
				return None
		return date

	@classmethod
	def getTime(cls, time):
		time = GET_TIME(time)
		if time:
			time = time[0]
			if not cls.isValidDatetime(time, const.time_format):
				return None
		return time

	@classmethod
	def isValidDatetime(cls, date_str, date_format="%d.%m.%Y"):
		"""Проверяет, существует ли указанная дата в календаре."""
		try:
			datetime.strptime(date_str, date_format)
			return True
		except ValueError:
			return False

	# Преобразуем строки в формат datetime
	@classmethod
	def getDateTime(cls, value):
		return datetime.strptime(value, const.datetime_format)
