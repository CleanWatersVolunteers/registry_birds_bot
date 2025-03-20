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
		# print(
		# 	f'insert_animal. code: {code}, capture_datetime: {capture_datetime}, place: {place}, species: {species}, catcher: {catcher}, pollution: {pollution}')
		capture_datetime = datetime.strptime(capture_datetime, cls.capture_datetime_string_format)
		capture_datetime_formatted = capture_datetime.strftime(cls.capture_datetime_db_format)
		query = """
			INSERT INTO animals (bar_code, place_capture, capture_datetime, species, catcher, degree_pollution)
			VALUES (%s, %s, %s, %s, %s, %s)
		"""
		data = (code, place, capture_datetime_formatted, species, catcher, pollution)
		result = cls.execute_query(query, data)
		return result

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

	@classmethod
	def insert_dead(cls, code, dead_datetime, arms_id, tg_nickname):
		# print(
		# 	f'insert_dead. code: {code}, dead_datetime: {dead_datetime}, arms_id: {arms_id}, tg_nickname: {tg_nickname}')
		"""
		Метод для внесения записи о погибшем животном в таблицу animals_dead.

		:param code: QR-код животного (уникальный идентификатор).
		:param dead_datetime: Дата и время смерти животного (формат datetime или строка).
		:param arms_id: Идентификатор рабочего места.
		:param tg_nickname: Никнейм пользователя Telegram.
		:return: ID вставленной записи или None в случае ошибки.
		"""
		# 1. Найти animal_id по bar_code
		find_animal_query = "SELECT id FROM animals WHERE bar_code = %s"
		animal_data = cls.execute_query(find_animal_query, (code,), fetch=True)

		if not animal_data:
			print(f"Животное с bar_code {code} не найдено.")
			return None

		animal_id = animal_data[0]["id"]

		dead_datetime = datetime.strptime(dead_datetime, cls.capture_datetime_string_format)
		dead_datetime_formatted = dead_datetime.strftime(cls.capture_datetime_db_format)

		# 2. Вставить запись в таблицу animals_dead
		insert_query = """
				INSERT INTO animals_dead (animal_id, datetime, arms_id, tg_nickname)
				VALUES (%s, %s, %s, %s)
			"""
		data = (animal_id, dead_datetime_formatted, arms_id, tg_nickname)

		try:
			# Выполняем запрос на вставку
			last_row_id = cls.execute_query(insert_query, data)
			if last_row_id is not None:
				print(f"Запись успешно добавлена в таблицу animals_dead. QR: {code}")
				return last_row_id
			else:
				print(f"Ошибка при добавлении записи в таблицу animals_dead. QR: {code}")
				return None
		except Exception as e:
			print(f"Ошибка при выполнении запроса: {e}")
			return None
