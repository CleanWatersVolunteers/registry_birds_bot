import os
from datetime import datetime

import mysql.connector
from mysql.connector import pooling

from logs import log
from timetools import TimeTools

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


class storage:
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
			log.error(f"Ошибка при выполнении запроса: {err}\n{query}")
			return None
		finally:
			cursor.close()
			connection.close()  # Закрываем соединение, возвращая его в пул

	@classmethod
	def insert_place_history(cls, arm_id, animal_id, tg_nickname):
		log.info(f'insert_place_history. arm_id: {arm_id}, animal_id: {animal_id}, tg_nickname: {tg_nickname}')
		query = """
            INSERT INTO place_history (datetime, animal_id, tg_nickname, arm_id)
            VALUES (NOW(), %s, %s, %s)
            """
		data = (animal_id, tg_nickname, arm_id)
		return cls.execute_query(query, data)

	@classmethod
	def get_place_history(cls, animal_id, start_date):
		select_query = """
                SELECT 
                    ph.datetime, 
                    p.name AS place_name, 
                    l.name AS location_name
                FROM 
                    place_history ph
                JOIN 
                    arms a ON ph.arm_id = a.id
                JOIN 
                    places p ON a.place_id = p.id
                JOIN 
                    locations l ON a.location_id = l.id
                WHERE 
                    ph.animal_id = %s
            """
		if start_date is not None:
			select_query += " AND ph.datetime >= %s"
			data = (animal_id, start_date)
		else:
			data = (animal_id,)
		return cls.execute_query(select_query, data, fetch=True)

	@classmethod
	def get_animal_id(cls, bar_code):
		select_query = "SELECT id FROM animals WHERE bar_code = %s"
		result = cls.execute_query(select_query, (bar_code,), fetch=True)
		if result is not None and len(result) > 0:  # Проверяем, что результат не пустой
			return result[0]['id']  # Возвращаем значение 'id' первого элемента
		return None  # Возвращаем None, если ничего не найдено

	@classmethod
	def get_animal_by_bar_code(cls, bar_code) -> dict:
		query = "SELECT *, id AS animal_id FROM animals WHERE bar_code = %s"
		data = (bar_code,)
		result = cls.execute_query(query, data, fetch=True)
		if result:
			return result[0]  # Возвращаем первый (и единственный) объект
		else:
			return {}

	@classmethod
	def insert_value_history(cls, animal_id, type_id, value, tg_nickname):
		log.info(
			f'insert_value_history. animal_id: {animal_id}, type_id: {type_id}, value: {value}, tg_nickname: {tg_nickname}')
		query = """
        INSERT INTO values_history (datetime, animal_id, type_id, value, tg_nickname)
        VALUES (NOW(), %s, %s, %s, %s)
        """
		data = (animal_id, type_id, value, tg_nickname)
		cls.execute_query(query, data)

	@classmethod
	def get_values_history_type(cls):
		select_query = "SELECT id, name, units FROM values_history_type"
		results = cls.execute_query(select_query, fetch=True)
		if results is not None:
			items = [{"id": row["id"], "name": row["name"], "units": row["units"]} for row in results]
			return items
		return []

	@classmethod
	def get_animal_values_history(cls, animal_id, start_date=None):
		select_query = """
	SELECT 
		vht.name AS type_name,
		vht.units AS type_units,
		vh.value,
		vh.tg_nickname,
		vh.datetime
	FROM 
		values_history vh
	JOIN 
		values_history_type vht ON vh.type_id = vht.id
	WHERE 
		vh.animal_id = %s
	"""
		if start_date is not None:
			select_query += " AND vh.datetime >= %s"
			data = (animal_id, start_date)
		else:
			data = (animal_id,)
		results = cls.execute_query(select_query, data, fetch=True)
		if results is not None:
			# Формируем список записей
			items = [{
				"type_name": row["type_name"],
				"type_units": row["type_units"],
				"value": row["value"],
				"tg_nickname": row["tg_nickname"],
				"datetime": row["datetime"]
			} for row in results]
			return items
		return []

	@classmethod
	def insert_history(cls, manipulation_id, animal_id, arms_id, tg_nickname):
		log.info(
			f'insert_history. manipulation_id: {manipulation_id}, animal_id: {animal_id}, arms_id: {arms_id}, tg_nickname: {tg_nickname}')
		query = """
	INSERT INTO history (datetime, animal_id, manipulation_id, arm_id, tg_nickname)
	VALUES (NOW(), %s, %s, %s, %s)
	"""
		data = (animal_id, manipulation_id, arms_id, tg_nickname)
		cls.execute_query(query, data)

	@classmethod
	def get_animal_history(cls, animal_id, start_date):
		select_query = """
	SELECT 
		h.datetime, 
		h.arm_id, 
		h.tg_nickname, 
		m.name AS manipulation_name 
	FROM 
		history h 
	JOIN 
		manipulations m ON h.manipulation_id = m.id 
	WHERE 
		h.animal_id = %s
	"""
		if start_date is not None:
			select_query += " AND h.datetime >= %s"
			data = (animal_id, start_date)
		else:
			data = (animal_id,)
		results = cls.execute_query(select_query, data, fetch=True)
		if results is not None:
			# Формируем список записей
			items = [{
				"datetime": row["datetime"],
				"arm_id": row["arm_id"],
				"tg_nickname": row["tg_nickname"],
				"manipulation_name": row["manipulation_name"]
			} for row in results]
			return items
		return []

	@classmethod
	def get_history(cls, animal_id):
		select_query = "SELECT * FROM history WHERE animal_id = %s"
		data = (animal_id,)
		results = cls.execute_query(select_query, data, fetch=True)
		if results is not None:
			# Формируем список записей
			items = [{"id": row["id"], "animal_id": row["animal_id"], "datetime": row["datetime"],
					  "manipulation_id": row["manipulation_id"], "arm_id": row["arm_id"],
					  "tg_nickname": row["tg_nickname"]} for row in results]
			return items
		return []

	@classmethod
	def insert_animal(cls, code, capture_datetime, place, pollution):
		log.info(
			f'insert_animal. code: {code}, capture_datetime: {capture_datetime}, place: {place}, pollution: {pollution}')
		capture_datetime = datetime.strptime(capture_datetime, cls.capture_datetime_string_format)
		capture_datetime_formatted = capture_datetime.strftime(cls.capture_datetime_db_format)
		query = """
			INSERT INTO animals (bar_code, place_capture, capture_datetime, degree_pollution)
			VALUES (%s, %s, %s, %s)
		"""
		data = (code, place, capture_datetime_formatted, pollution)
		return cls.execute_query(query, data)

	@classmethod
	def get_manipulations(cls, place_number):
		select_query = "SELECT id, name FROM manipulations WHERE FIND_IN_SET(%s, place_list)"
		results = cls.execute_query(select_query, (place_number,), fetch=True)
		if results is not None:
			items = [{"id": row["id"], "name": row["name"]} for row in results]
			return items
		return []

	# Обновление таблицы animals
	@classmethod
	def update_animal(cls, animal_id, weight=None, species=None, clinical_condition_admission=None,
					  triage=None) -> bool:
		log.info(
			f'update_animal. animal_id: {animal_id}, weight: {weight}, species: {species}, clinical_condition_admission: {clinical_condition_admission}')
		query = "UPDATE animals SET "
		updates = []
		data = []

		# Добавляем поля для обновления, если они указаны
		if weight is not None:
			updates.append("weight = %s")
			data.append(weight)
		if species is not None:
			updates.append("species = %s")
			data.append(species)
		if clinical_condition_admission is not None:
			updates.append("clinical_condition_admission = %s")
			data.append(clinical_condition_admission)
		if triage is not None:
			updates.append("triage = %s")
			data.append(triage)
		if not updates:
			log.error("update_animal: Нет данных для обновления.")
			return False

		query += ", ".join(updates) + " WHERE id = %s"
		data.append(animal_id)

		result = cls.execute_query(query, data)
		if result is None:
			log.error("update_animal: Ошибка обновления данных.")
			return False
		else:
			log.info(f"Данные animals для id {animal_id} успешно обновлены.")
			return True

	@classmethod
	def get_location(cls):
		query = """
	SELECT DISTINCT 
		l.id AS location_id, 
		l.name AS location_name
	FROM 
		arms a
	JOIN 
		locations l ON a.location_id = l.id;
	"""
		return cls.execute_query(query, fetch=True)

	@classmethod
	def get_place_name(cls, place_id):
		query = """SELECT name FROM places WHERE id = %s """
		result = cls.execute_query(query, (place_id,), fetch=True)
		if result and len(result) == 1:
			name = result[0]["name"]
			return name
		return None

	@classmethod
	def get_arms(cls, location_id):
		query = """
	SELECT
		p.id AS arm_id, 
		a.place_id AS place_id,
		p.name AS arm_name
	FROM places p
	INNER JOIN arms a ON a.place_id = p.id
	WHERE a.location_id = %s
	"""
		return cls.execute_query(query, (location_id,), fetch=True)

	@classmethod
	def get_arm_id(cls, place_id, location):
		query = """
	  SELECT DISTINCT
		  a.id AS id
	  FROM places p
	  INNER JOIN arms a ON a.place_id = p.id
	  WHERE p.id = %s AND a.location_id = %s 
	  """
		result = cls.execute_query(query, (place_id, location,), fetch=True)
		if result and len(result) == 1:
			arm_id = result[0]["id"]
			return arm_id
		return None

	@classmethod
	def access_data(cls, place_id, location_id):
		query = """
			SELECT aa.*, p.name
			FROM arm_access aa
			JOIN arms a ON aa.arm_id = a.id
			JOIN places p ON p.id = a.place_id
			WHERE a.place_id = %s AND a.location_id = %s
			ORDER BY start_date
			"""
		data = (place_id, location_id)
		return cls.execute_query(query, data, fetch=True)

	# Создаёт новую смену
	@classmethod
	def create_duty(cls, arm_id, start_date, end_date, password):
		start_date_str = start_date.strftime(cls.capture_datetime_db_format)
		end_date_str = end_date.strftime(cls.capture_datetime_db_format)
		query = """INSERT INTO arm_access (arm_id, start_date, end_date, password) VALUES (%s, %s, %s, %s)"""
		data = (arm_id, start_date_str, end_date_str, password)
		result = cls.execute_query(query, data)
		return result is not None

	# Проверяет попадает ли дата внутрь смены
	@classmethod
	def check_duty_date(cls, arm_id, date):
		start = TimeTools.getDateTime(date)
		date_str = start.strftime(cls.capture_datetime_db_format)
		query = """SELECT id FROM arm_access WHERE arm_id = %s AND (%s BETWEEN start_date AND end_date)"""
		data = (arm_id, date_str)
		results = cls.execute_query(query, data, fetch=True)
		return results is None or len(results) == 0

	# Удаляет смену
	@classmethod
	def delete_duty(cls, access_id):
		query = """DELETE FROM arm_access WHERE id = %s"""
		data = (access_id,)
		result = cls.execute_query(query, data)
		return result is not None

	# Возвращает информацию для авторизации
	@classmethod
	def get_arm_access(cls, datetime_now, password):
		query = """
		SELECT 
			a.id AS arm_id,
			a.place_id,
			a.location_id,
			p.name AS arm_name,
			l.name AS location_name,
			aa.start_date,
			aa.end_date,
			aa.password
		FROM arms a
		JOIN arm_access aa ON a.id = aa.arm_id
		JOIN places p ON p.id = a.place_id
		JOIN locations l ON l.id = a.location_id
		WHERE %s BETWEEN aa.start_date AND aa.end_date
	"""
		if password is not None:
			query += " AND aa.password = %s"
			data = (datetime_now, password)
		else:
			data = (datetime_now,)

		return cls.execute_query(query, data, fetch=True)

	@classmethod
	def create_dead_animal(cls, animal_id, arms_id, tg_nickname):
		log.info(f'create_dead_animal. animal_id: {animal_id}, arms_id: {arms_id}, tg_nickname: {tg_nickname}')
		query = """INSERT INTO animals_dead (animal_id, arms_id, tg_nickname, datetime) VALUES (%s, %s, %s, NOW())"""
		data = (animal_id, arms_id, tg_nickname)
		result = cls.execute_query(query, data)
		return result is not None

	@classmethod
	def get_animal_dead(cls, bar_code):
		query = """
			SELECT ad.*
			FROM animals_dead ad
			JOIN animals a ON ad.animal_id = a.id
			WHERE a.bar_code = %s
			"""
		result = cls.execute_query(query, (bar_code,), fetch=True)
		if result and len(result) > 0:
			return result
		return None

	# Вставка записей бумажного журнала первичной регистрации
	@classmethod
	def import_place_history(cls, code, registration_datetime, tg_nickname, arm_id):
		log.info(
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
	def get_place_count(cls, location_id):
		query = """
			SELECT p.id, p.name, COUNT(DISTINCT ph.animal_id) AS count
			FROM place_history ph
			JOIN arms a ON ph.arm_id = a.id
			JOIN places p ON a.place_id = p.id
			WHERE a.location_id = %s
			GROUP BY p.id, p.name
			ORDER BY p.id;
			"""

		# Выполнение запроса, передавая location_id
		results = cls.execute_query(query, (location_id,), fetch=True)
		return results

	@classmethod
	def __create_user(cls):
		user = {"location_id": None, "location_name": None, "mode": None, "code": None, "id": None}
		return user

	@classmethod
	def init(cls, users, birds):
		cls.__users = {}

	@classmethod
	def add_user(cls, username) -> bool:
		if username in cls.__users:
			return False
		cls.__users[username] = cls.__create_user()
		cls.__users[username]["id"] = username
		return True

	@classmethod
	def get_user(cls, username):
		if username in cls.__users:
			return cls.__users[username]
		return None


class QRCodeStorage:
	@staticmethod
	def get_qr_start_value():
		query = "SELECT qr_start_value FROM qr_last_number WHERE id = 1;"
		result = storage.execute_query(query, fetch=True)
		return result[0]["qr_start_value"] if result else None

	@staticmethod
	def set_qr_start_value(new_value):
		query = "UPDATE qr_last_number SET qr_start_value = %s WHERE id = 1;"
		storage.execute_query(query, (new_value,))
