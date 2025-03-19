import os
from datetime import datetime

import mysql.connector
from mysql.connector import pooling

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')


class ExchangeStorage:
	capture_datetime_string_format = "%d.%m.%Y %H:%M"
	capture_datetime_db_format = "%Y-%m-%d %H:%M:%S"

	# print(f'host: {DB_HOST}')
	# print(f'port: {DB_PORT}')
	# print(f'user: {DB_USER}')
	# print(f'password: {DB_PASSWORD}')
	# print(f'host: {DB_NAME}')

	DB_CONFIG = {
		"host": DB_HOST,
		"port": int(DB_PORT),
		"user": DB_USER,
		"password": DB_PASSWORD,
		"database": DB_NAME
	}
	connection_pool = pooling.MySQLConnectionPool(
		pool_name="mypool",
		pool_size=5,
		**DB_CONFIG
	)

	@classmethod
	def execute_query(cls, query, data=None, fetch=False):
		connection = cls.connection_pool.get_connection()
		cursor = connection.cursor(dictionary=True)
		try:
			cursor.execute(query, data)
			if fetch:
				results = cursor.fetchall()
				return results
			else:
				connection.commit()  # Подтверждаем изменения
				return cursor.lastrowid
		except mysql.connector.Error as err:
			print(f"Ошибка при выполнении запроса: {err}\n{query}")
			return None
		finally:
			cursor.close()
			connection.close()  # Закрываем соединение, возвращая его в пул

	@classmethod
	def insert_animal(cls, code, capture_datetime, place, species, catcher, pollution):
		print(
			f'insert_animal. code: {code}, capture_datetime: {capture_datetime}, place: {place}, species: {species}, catcher: {catcher}, pollution: {pollution}')
		capture_datetime = datetime.strptime(capture_datetime, cls.capture_datetime_string_format)
		capture_datetime_formatted = capture_datetime.strftime(cls.capture_datetime_db_format)
		query = """
			INSERT INTO animals (bar_code, place_capture, capture_datetime, species, catcher, degree_pollution)
			VALUES (%s, %s, %s, %s, %s, %s)
		"""
		data = (code, place, capture_datetime_formatted, species, catcher, pollution)
		return cls.execute_query(query, data)

	# Вставка записей бумажного журнала первичной регистрации
	@classmethod
	def import_place_history(cls, code, registration_datetime, tg_nickname, arm_id):
		print(
			f'import_place_history. code: {code}, arm_id: {arm_id}, registration_datetime: {registration_datetime}, tg_nickname: {tg_nickname}')
		registration_datetime = datetime.strptime(registration_datetime, cls.capture_datetime_string_format)
		capture_datetime_formatted = registration_datetime.strftime(cls.capture_datetime_db_format)
		query = """
				INSERT INTO place_history (animal_id, datetime, tg_nickname, arm_id)
				VALUES (
					(SELECT id FROM animals WHERE bar_code = %s), %s, %s, %s);
				"""
		data = (code, capture_datetime_formatted, tg_nickname, arm_id)
		result = cls.execute_query(query, data)
		return result

	@classmethod
	def get_animals_list(cls):
		"""
		Метод для получения списка животных с указанными полями, включая данные из place_history.
		:return: Список словарей, где каждый словарь представляет одно животное.
		"""
		query = """
				SELECT 
					a.bar_code, 
					a.place_capture, 
					a.capture_datetime, 
					a.degree_pollution, 
					a.species, 
					a.catcher,
					ph.datetime AS place_history_datetime
				FROM animals a
				LEFT JOIN place_history ph ON a.id = ph.animal_id
				WHERE ph.arm_id = 1
				ORDER BY ph.datetime
			"""
		# Выполняем запрос и получаем результаты
		results = cls.execute_query(query, fetch=True)
		if results is None:
			# Если произошла ошибка, возвращаем пустой список
			return []

		# Преобразуем capture_datetime и place_history_datetime в строковый формат для удобства
		for animal in results:
			if animal["capture_datetime"]:
				animal["capture_datetime"] = animal["capture_datetime"].strftime(cls.capture_datetime_string_format)
			if animal["place_history_datetime"]:
				animal["place_history_datetime"] = animal["place_history_datetime"].strftime(
					cls.capture_datetime_string_format)

		return results
