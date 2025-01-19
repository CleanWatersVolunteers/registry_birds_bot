import mysql.connector
from mysql.connector import pooling
from config import Config

class storage:

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
                print("Запись успешно добавлена.")
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
        print("get_animal_id")
        select_query = "SELECT id FROM animals WHERE bar_code = %s"
        result = cls.execute_query(select_query, (bar_code,), fetch=True)
        if result is not None and len(result) > 0:  # Проверяем, что результат не пустой
            print(result[0])  # Печатаем первый элемент результата
            return result[0]['id']  # Возвращаем значение 'id' первого элемента
        return None  # Возвращаем None, если ничего не найдено

    @classmethod
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
    def insert_numerical_history(cls):
        #todo убрать после реальных вызовов
        item = {
            "animal_id": 11,
            "type_id": 2,
            "value": 700
        }
        #todo убрать после реальных вызовов
        query = """
        INSERT INTO numerical_history (datetime, animal_id, type_id, value)
        VALUES (NOW(), %s, %s, %s)
        """
        data = (item["animal_id"], item["type_id"], item["value"])
        cls.execute_query(query, data)

    @classmethod
    def get_numerical_history(cls):
        print("get_numerical_history")
        select_query = "SELECT animal_id, type_id, value, datetime FROM numerical_history"
        results = cls.execute_query(select_query, fetch=True)
        if results is not None:
            items = [{"animal_id": row["animal_id"], "type_id": row["type_id"], "value": row["value"], "datetime": row["datetime"]} for row in results]
            print(items)
            return items
        return []

    @classmethod
    def get_numerical_history_type(cls):
        print("get_numerical_history_type")
        select_query = "SELECT id, name, units FROM numerical_history_type"
        results = cls.execute_query(select_query, fetch=True)
        if results is not None:
            items = [{"id": row["id"], "name": row["name"], "units": row["units"]} for row in results]
            print(items)
            return items
        return []

    @classmethod
    def insert_history(cls, tg_nickname):
        item = {
            "animal_id": 11,
            "manipulation_id": 2,
            "arms_id": 2,
            "tg_nickname": tg_nickname
        }
        query = """
        INSERT INTO history (datetime, animal_id, manipulation_id, arm_id, tg_nickname)
        VALUES (NOW(), %s, %s, %s, %s)
        """
        data = (item["animal_id"], item["manipulation_id"], item["arms_id"], item["tg_nickname"])
        cls.execute_query(query, data)

    @classmethod
    def insert_animals(cls):
        print("insert_animals")
        #todo убрать после реальных вызовов
        item = {
            "bar_code": 1236,  # barcode
            "place_capture": "Marina",  # Место отлова
            #"capture_datetime": #Дата/время отлова. Временно! подставляется текущее прямо в базу. См. второй NOW()            
            "degree_pollution": 3  # Степень загрязнения
        }
        #todo убрать после реальных вызовов
        query = """
        INSERT INTO animals (registration_datetime, bar_code, place_capture, capture_datetime, degree_pollution)
        VALUES (NOW(), %s, %s, NOW(), %s)
        """
        data = (item["bar_code"], item["place_capture"], item["degree_pollution"])
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
    @classmethod
    def update_animal(cls, bar_code, weight=None, female=None, species=None, clinical_condition_admission=None) -> bool:
        print(f'update_animal bar_code: {bar_code}, weight: {weight}, female: {female}, species: {species}, clinical_condition_admission: {clinical_condition_admission}')
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
    def __create_bird(cls):
        bird = {}
        bird["capture_place"] = None
        bird["capture_date"] = None
        bird["polution"] = None
        bird["mass"] = None
        bird["species"] = None
        bird["sex"] = None
        bird["clinic_state"] = None
        bird["nanny"] = None
        bird["stage1"] = None
        bird["stage2"] = None
        bird["stage3"] = None
        bird["stage4"] = None
        bird["stage5"] = None
        bird["stage6"] = None
        bird["stage7"] = None
        return bird
    
    @classmethod
    def show_manipulations(cls):
        place = 2
        records = cls.get_manipulations(place)
        if records:
            print("Записи для {place}.")
            for record in records:
                print(record)
        else:
            print("Записей не найдено.")

    @classmethod
    def __create_user(cls):
        user = {"addr":None, "mode":None, "code":None, "id":None}
        return user

    @classmethod
    def init(cls, users, birds):
        cls.__users = {}
        cls._birds = {}
        # with open(users, 'r') as f:
        #     json.dump(self.__users, f)
        # with open(birds, 'r') as f:
        #     json.dump(self._birds, f)

    @classmethod
    def add_bird(cls, code)->bool:
        if code in cls._birds:
            return False
        cls._birds[code] = cls.__create_bird()
        return True

    @classmethod
    def upd_bird(cls, code, key, val)->bool:
        if code in cls._birds:
            cls._birds[code][key] = val
            return True
        return False

    @classmethod
    def get_bird(cls, code):
        # todo Тестовое чтение таблицы
        # cls.show_manipulations()
        # print(cls._birds)
        if code == None:
            return None
        if code in cls._birds:
            return cls._birds[code]
        return None

    @classmethod
    def add_user(cls, username)->bool:
        if username in cls.__users:
            return False
        cls.__users[username] = cls.__create_user()
        cls.__users[username]["id"] = username
        return True

    @classmethod
    def upd_user(cls, username, key, val)->bool:
        if username in cls.__users:
            cls.__users[username][key] = val
            return True
        return False

    @classmethod
    def get_user(cls, username):
        if username in cls.__users:
            return cls.__users[username]
        return None