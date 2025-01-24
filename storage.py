import mysql.connector
from mysql.connector import pooling
from config import Config
from datetime import datetime

class storage:

    capture_datetime_string_format = "%d.%m.%Y %H:%M"
    capture_datetime_db_format = "%Y-%m-%d %H:%M:%S"

    dbconfig = Config.load_config_from_json()
    connection_pool = pooling.MySQLConnectionPool(
        pool_name = "mypool",
        pool_size = 5,
        **dbconfig
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
                return True
        except mysql.connector.Error as err:
            print(f"Ошибка при выполнении запроса: {err}")
            return None
        finally:
            cursor.close()
            connection.close()  # Закрываем соединение, возвращая его в пул

    @classmethod
    def insert_place_history(cls, bar_code, tg_nickname):
        animal_id = cls.get_animal_id(bar_code)
        print(f"animal_id: {animal_id}")
        if animal_id is not None:
            #todo убрать после реальных вызовов
            item = {
                "animal_id": animal_id,
                "tg_nickname": tg_nickname,
                "arm_id": 3
            }
            #todo убрать после реальных вызовов
            query = """
            INSERT INTO place_history (datetime, animal_id, tg_nickname, arm_id)
            VALUES (NOW(), %s, %s, %s)
            """
            data = (item["animal_id"], item["tg_nickname"], item["arm_id"])
            cls.execute_query(query, data)
        else:
            print(f"invalid animal_id: {animal_id}")

    @classmethod
    def get_animal_id(cls, bar_code):
        select_query = "SELECT id FROM animals WHERE bar_code = %s"
        result = cls.execute_query(select_query, (bar_code,), fetch=True)
        if result is not None and len(result) > 0:  # Проверяем, что результат не пустой
            print(result[0])  # Печатаем первый элемент результата
            return result[0]['id']  # Возвращаем значение 'id' первого элемента
        return None  # Возвращаем None, если ничего не найдено

    @classmethod
    def get_animal_by_id(cls, animal_id) -> dict:
        query = "SELECT * FROM animals WHERE id = %s"
        data = (animal_id,)
        result = cls.execute_query(query, data, fetch=True)
        if result:
            return result[0]  # Возвращаем первый (и единственный) объект
        else:
            print("Животное не найдено.")
            return None
    
    #todo Удалить после перехода на id
    @classmethod
    def get_animal_by_bar_code(cls, bar_code) -> dict:
        query = "SELECT * FROM animals WHERE bar_code = %s"
        data = (bar_code,)
        result = cls.execute_query(query, data, fetch=True)
        if result:
            return result[0]  # Возвращаем первый (и единственный) объект
        else:
            print("Животное не найдено.")
            return None

    @classmethod
    def insert_numerical_history(cls, animal_id, type_id, value, tg_nickname):
        query = """
        INSERT INTO numerical_history (datetime, animal_id, type_id, value, tg_nickname)
        VALUES (NOW(), %s, %s, %s, %s)
        """
        data = (animal_id, type_id, value, tg_nickname)
        cls.execute_query(query, data)

    def get_animal_by_id(cls, animal_id) -> dict:
        print(f'get_animal_by_id animal_id: {animal_id}')
        query = "SELECT * FROM animals WHERE id = %s"
        data = (animal_id,)
        result = cls.execute_query(query, data, fetch=True)
        if result:
            return result[0]  # Возвращаем первый (и единственный) объект
        else:
            print("Животное не найдено.")
            return None

    @classmethod
    def get_numerical_history_type(cls):
        select_query = "SELECT id, name, units FROM numerical_history_type"
        results = cls.execute_query(select_query, fetch=True)
        if results is not None:
            items = [{"id": row["id"], "name": row["name"], "units": row["units"]} for row in results]
            return items
        return []
    
    @classmethod
    def get_animal_numerical_history(cls, animal_id):
        select_query = """
        SELECT 
            nht.name AS type_name,
            nht.units AS type_units,
            nh.value,
            nh.tg_nickname,
            nh.datetime
        FROM 
            numerical_history nh
        JOIN 
            numerical_history_type nht ON nh.type_id = nht.id
        WHERE 
            nh.animal_id = %s;
        """
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
        query = """
        INSERT INTO history (datetime, animal_id, manipulation_id, arm_id, tg_nickname)
        VALUES (NOW(), %s, %s, %s, %s)
        """
        data = (animal_id, manipulation_id, arms_id, tg_nickname)
        cls.execute_query(query, data)

    @classmethod
    def get_animal_history(cls, animal_id):
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
            h.animal_id = %s;
        """
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
    def insert_animal(cls, animal):
        capture_datetime = datetime.strptime(animal["capture_datetime"], cls.capture_datetime_string_format)
        capture_datetime_formatted = capture_datetime.strftime(cls.capture_datetime_db_format)
        query = """
        INSERT INTO animals (registration_datetime, bar_code, place_capture, capture_datetime, degree_pollution)
        VALUES (NOW(), %s, %s, %s, %s)
        """
        data = (animal["bar_code"], animal["place_capture"], capture_datetime_formatted, animal["degree_pollution"])
        cls.execute_query(query, data)

    @classmethod
    def get_manipulations(cls, place_number):
        select_query = "SELECT id, name FROM manipulations WHERE FIND_IN_SET(%s, place_list)"
        results = cls.execute_query(select_query, (place_number,), fetch=True)
        if results is not None:
            items = [{"id": row["id"], "name": row["name"]} for row in results]
            return items
        return []

    #Обновление таблицы animals
    #todo Переделать на WHERE id = id
    @classmethod
    def update_animal(cls, bar_code, weight=None, female=None, species=None, clinical_condition_admission=None) -> bool:
        query = "UPDATE animals SET "
        updates = []
        data = []

        # Добавляем поля для обновления, если они указаны
        if weight is not None:
            updates.append("weight = %s")
            data.append(weight)
        if female is not None:
            updates.append("female = %s")
            data.append(female)
        if species is not None:
            updates.append("species = %s")
            data.append(species)
        if clinical_condition_admission is not None:
            updates.append("clinical_condition_admission = %s")
            data.append(clinical_condition_admission)

        if not updates:
            print("Нет данных для обновления.")
            return False

        query += ", ".join(updates) + " WHERE bar_code = %s"
        data.append(bar_code)

        result = cls.execute_query(query, data)
        if result is None:
            print("Ошибка обновления данных.")
            return False
        else:
            print(f"Данные для бар-кода {bar_code} успешно обновлены.")
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
    def __create_user(cls):
        user = {"location_id":None, "location_name":None, "mode":None, "code":None, "id":None}
        return user

    @classmethod
    def init(cls, users, birds):
        cls.__users = {}

    @classmethod
    def add_user(cls, username)->bool:
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