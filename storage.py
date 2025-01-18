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
    def get_manipulations(cls, place_number):
        connection = cls.connection_pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            # SQL-запрос для поиска записей по числу в place_list
            select_query = "SELECT id, name FROM manipulations WHERE FIND_IN_SET(%s, place_list)"
            cursor.execute(select_query, (place_number,))
            results = cursor.fetchall()

            # Создаём список объектов place
            places = []
            for row in results:
                place = {
                    "id": row["id"],
                    "name": row["name"]
                }
                places.append(place)
            return places
        except mysql.connector.Error as err:
            print(f"Ошибка: {err}")
            return None
        finally:
            cursor.close()
            connection.close()  # Возвращаем соединение в пул

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
        