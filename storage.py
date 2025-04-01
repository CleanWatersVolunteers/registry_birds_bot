import os
from datetime import datetime

import mysql.connector
from mysql.connector import pooling

from logs import my_logger
from timetools import TimeTools

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


class Storage:
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
			my_logger.error(f"Ошибка при выполнении запроса: {err}\n{query}")
			return None
		finally:
			cursor.close()
			connection.close()  # Закрываем соединение, возвращая его в пул

	@classmethod
	def insert_place_history(cls, arm_id, animal_id, tg_nickname):
		my_logger.info(f'insert_place_history. arm_id: {arm_id}, animal_id: {animal_id}, tg_nickname: {tg_nickname}')
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
	def get_reg_time(cls, animal_id, arm_id):
		"""
		Метод для получения значения datetime из таблицы place_history
		по заданным animal_id и arm_id.

		:param animal_id: ID животного.
		:param arm_id: ID руки.
		:return: datetime (если запись найдена) или None (если запись не найдена).
		"""
		query = """
				SELECT datetime
				FROM place_history
				WHERE animal_id = %s AND arm_id = %s
			"""
		data = (animal_id, arm_id)

		# Выполняем запрос
		results = cls.execute_query(query, data, fetch=True)

		if results:
			return results[0]["datetime"]
		else:
			return None

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
	def get_max_qr_code(cls):
		query = """
		SELECT bar_code
		FROM (
			SELECT bar_code, ROW_NUMBER() OVER (ORDER BY id DESC) AS rn
		FROM animals
		) AS subquery
		WHERE rn = 1;
		"""
		result = cls.execute_query(query, fetch=True)
		return result[0]['bar_code']

	@classmethod
	def insert_value_history(cls, animal_id, type_id, value, tg_nickname):
		my_logger.info(
			f'insert_value_history. animal_id: {animal_id}, type_id: {type_id}, value: {value}, tg_nickname: {tg_nickname}')
		query = """
        INSERT INTO values_history (datetime, animal_id, type_id, value, tg_nickname)
        VALUES (NOW(), %s, %s, %s, %s)
        """
		data = (animal_id, type_id, value, tg_nickname)
		return cls.execute_query(query, data)

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
		my_logger.info(
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
	def insert_animal(cls, code, capture_datetime, place, species, catcher, pollution):
		my_logger.info(
			f'insert_animal. code: {code}, capture_datetime: {capture_datetime}, place: {place}, species: {species}, catcher: {catcher}, pollution: {pollution}')
		capture_datetime = datetime.strptime(capture_datetime, cls.capture_datetime_string_format)
		capture_datetime_formatted = capture_datetime.strftime(cls.capture_datetime_db_format)
		query = """
			INSERT INTO animals (bar_code, place_capture, capture_datetime, species, catcher, degree_pollution)
			VALUES (%s, %s, %s, %s, %s, %s)
		"""
		data = (code, place, capture_datetime_formatted, species, catcher, pollution)
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
		my_logger.info(
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
			my_logger.error("update_animal: Нет данных для обновления.")
			return False

		query += ", ".join(updates) + " WHERE id = %s"
		data.append(animal_id)

		result = cls.execute_query(query, data)
		if result is None:
			my_logger.error("update_animal: Ошибка обновления данных.")
			return False
		else:
			my_logger.info(f"Данные animals для id {animal_id} успешно обновлены.")
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
		my_logger.info(f'create_dead_animal. animal_id: {animal_id}, arms_id: {arms_id}, tg_nickname: {tg_nickname}')
		query = """INSERT INTO animals_dead (animal_id, arms_id, tg_nickname, datetime) VALUES (%s, %s, %s, NOW())"""
		data = (animal_id, arms_id, tg_nickname)
		result = cls.execute_query(query, data)
		return result is not None

	@classmethod
	def count_animals_dead(cls, location_id, start_datetime=None, end_datetime=None):
		my_logger.info(
			f'count_animals_dead location_id: {location_id}, start_datetime: {start_datetime}, end_datetime: {end_datetime}')
		"""
		Возвращает количество записей в таблице animals_dead для указанного location_id
		и временного диапазона [start_datetime, end_datetime]."""
		query = """
		SELECT COUNT(*) AS count
		FROM animals_dead ad 
		JOIN arms a ON ad.arms_id = a.id
		"""
		where = " WHERE a.location_id = %s"
		params = [location_id]
		if start_datetime is not None:
			where += " AND ad.datetime >= %s"
			params.append(start_datetime)
		if end_datetime is not None:
			where += " AND ad.datetime <= %s"
			params.append(end_datetime)
		results = cls.execute_query(query + where, tuple(params), fetch=True)
		if results and len(results) > 0:
			return results[0]["count"]
		return 0

	@classmethod
	def get_animal_dead(cls, bar_code):
		query = """
			SELECT "dead", datetime, tg_nickname
			FROM animals_dead ad
			JOIN animals a ON ad.animal_id = a.id
			WHERE a.bar_code = %s
			"""
		result = cls.execute_query(query, (bar_code,), fetch=True)
		if result and len(result) > 0:
			return result
		return None

	@classmethod
	def insert_animals_outside(cls, animal_id, tg_nickname, description, arms_id):
		my_logger.info(
			f'insert_animals_outside animal_id: {animal_id}, tg_nickname: {tg_nickname}, description: {description}, arms_id: {arms_id}')
		"""
		Метод для вставки записи в таблицу animals_outside.
	
		:param animal_id: ID животного.
		:param tg_nickname: Никнейм пользователя Telegram.
		:param description: Описание.
		:param arms_id: ID рабочего места.
		:return: ID вставленной записи или None в случае ошибки.
		"""
		query = """
				INSERT INTO animals_outside (animal_id, datetime, tg_nickname, description, arms_id)
				VALUES (%s, NOW(), %s, %s, %s)
			"""
		data = (animal_id, tg_nickname, description, arms_id)

		try:
			# Выполняем запрос на вставку
			last_row_id = cls.execute_query(query, data)
			if last_row_id is not None:
				my_logger.debug(f"Запись успешно добавлена в таблицу animals_outside. ID: {last_row_id}")
				return last_row_id
			else:
				my_logger.error("Ошибка при добавлении записи в таблицу animals_outside.")
				return None
		except Exception as e:
			my_logger.error(f"Ошибка при выполнении запроса: {e}")
			return None

	@classmethod
	def count_animals_outside(cls, location_id, start_datetime=None, end_datetime=None):
		my_logger.info(
			f'count_animals_outside location_id: {location_id}, start_datetime: {start_datetime}, end_datetime: {end_datetime}')
		"""
		Возвращает количество записей в таблице animals_outside для указанного location_id
		и временного диапазона [start_datetime, end_datetime]."""
		query = """
		SELECT COUNT(*) AS count
		FROM animals_outside ao 
		JOIN arms a ON ao.arms_id = a.id
		"""
		where = " WHERE a.location_id = %s"
		params = [location_id]
		if start_datetime is not None:
			where += " AND ao.datetime >= %s"
			params.append(start_datetime)
		if end_datetime is not None:
			where += " AND ao.datetime <= %s"
			params.append(end_datetime)
		results = cls.execute_query(query + where, tuple(params), fetch=True)
		if results and len(results) > 0:
			return results[0]["count"]
		return 0

	@classmethod
	def get_animal_outside(cls, bar_code):
		"""
		Получает запись из таблицы animals_outside по bar_code.

		:param bar_code: QR-код животного для поиска.
		:return: Словарь с данными записи или None, если запись не найдена.
		"""
		query = """
					SELECT "outside", datetime, tg_nickname, description
					FROM animals_outside ao
					JOIN animals a ON ao.animal_id = a.id
					WHERE a.bar_code = %s
					"""
		result = cls.execute_query(query, (bar_code,), fetch=True)
		if result and len(result) > 0:
			return result
		return None

	@classmethod
	def get_place_count(cls, location_id, start_datetime=None, end_datetime=None):
		my_logger.info(
			f'get_place_count location_id: {location_id}, start_datetime: {start_datetime}, end_datetime: {end_datetime}')
		query = """
			SELECT p.id, p.name, COUNT(DISTINCT ph.animal_id) AS count
			FROM place_history ph
			JOIN arms a ON ph.arm_id = a.id
			JOIN places p ON a.place_id = p.id
			"""
		where = " WHERE a.location_id = %s"
		group_order = """
			GROUP BY p.id, p.name
			ORDER BY p.id;
		"""
		params = [location_id]
		if start_datetime is not None:
			where += " AND datetime >= %s"
			params.append(start_datetime)
		if end_datetime is not None:
			where += " AND datetime < %s"
			params.append(end_datetime)
		results = cls.execute_query(query + where + group_order, tuple(params), fetch=True)
		return results

	@classmethod
	def get_diff_values_history(cls, animal_id, type_id):
		query = """
			(SELECT `value` AS `first_value` FROM values_history 
			WHERE animal_id = %s AND type_id = %s 
			ORDER BY datetime DESC LIMIT 1)
			UNION ALL
			(SELECT `value` AS `second_value` FROM values_history 
			WHERE animal_id = %s AND type_id = %s 
			ORDER BY datetime DESC LIMIT 1 OFFSET 1)
			"""
		data = (animal_id, type_id, animal_id, type_id)
		results = cls.execute_query(query, data, fetch=True)

		if results and len(results) == 2:
			first_value = int(results[0]['first_value'])
			second_value = int(results[1]['first_value'])
			difference = first_value - second_value
			return difference
		else:
			return None

	@classmethod
	def getHospitalCountNow(cls, arm_id):
		"""
		Метод для получения количества записей из таблицы animals,
		которых нет в animals_dead и animals_outside, но которые есть в place_history с arm_id.

		:return: Количество записей (int) или None в случае ошибки.
		"""
		query = """
				SELECT COUNT(DISTINCT a.id) AS count
				FROM animals a
				JOIN place_history ph ON a.id = ph.animal_id
				LEFT JOIN animals_dead ad ON a.id = ad.animal_id
				LEFT JOIN animals_outside ao ON a.id = ao.animal_id
				WHERE ad.animal_id IS NULL
				  AND ao.animal_id IS NULL
				  AND ph.arm_id = %s;
			"""
		try:
			# Выполняем запрос
			result = cls.execute_query(query, (arm_id,), fetch=True)

			# Проверяем результат
			if result and len(result) > 0:
				return result[0]["count"]  # Возвращаем значение count
			else:
				my_logger.warning("Нет данных для статистики.")
				return 0

		except Exception as e:
			my_logger.error(f"Ошибка при получении статистики: {e}")
			return None

	@classmethod
	def get_history_count(cls, place_id, location_id):
		"""
		Метод для получения количества записей в таблице place_history
		по заданным place_id и location_id.

		:param place_id: ID места.
		:param location_id: ID локации.
		:return: Количество записей (int) или None в случае ошибки.
		"""
		query = """
				SELECT COUNT(*) AS count
				FROM place_history ph
				JOIN arms a ON ph.arm_id = a.id
				WHERE a.place_id = %(place_id)s
				  AND a.location_id = %(location_id)s;
			"""
		data = {
			"place_id": place_id,
			"location_id": location_id
		}

		try:
			# Выполняем запрос
			result = cls.execute_query(query, data=data, fetch=True)

			# Проверяем результат
			if result and len(result) > 0:
				return result[0]["count"]  # Возвращаем значение count
			else:
				my_logger.warning("Нет данных для статистики.")
				return 0

		except Exception as e:
			my_logger.error(f"Ошибка при получении статистики: {e}")
			return None

	@classmethod
	def __create_user(cls):
		user = {"location_id": None, "location_name": None, "mode": None, "code": None, "id": None}
		return user

	@classmethod
	def init(cls, users):
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
		result = Storage.execute_query(query, fetch=True)
		return result[0]["qr_start_value"] if result else None

	@staticmethod
	def set_qr_start_value(new_value):
		query = "UPDATE qr_last_number SET qr_start_value = %s WHERE id = 1;"
		Storage.execute_query(query, (new_value,))
