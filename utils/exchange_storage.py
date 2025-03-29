import os
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.exc import IntegrityError, SQLAlchemyError  # Основное исключение SQLAlchemy
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

# from pymysql.err import IntegrityError as PymysqlIntegrityError  # Исключение драйвера pymysql

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

# Создание движка (engine) для подключения к базе данных
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL, pool_size=5, max_overflow=10)

# Создание сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для ORM-моделей
Base = declarative_base()


class Animal(Base):
	__tablename__ = "animals"

	id = Column(Integer, primary_key=True, autoincrement=True)
	bar_code = Column(Integer, unique=True, nullable=False)
	place_capture = Column(String(45), nullable=False)
	capture_datetime = Column(DateTime, nullable=False)
	degree_pollution = Column(String(45), nullable=False)
	weight = Column(Integer, nullable=True)
	species = Column(String(45), nullable=True)
	clinical_condition_admission = Column(String(45), nullable=True)
	triage = Column(Integer, nullable=True)
	catcher = Column(String(45), nullable=False)

	# Связь с таблицей place_history
	place_history = relationship("PlaceHistory", back_populates="animal")


class PlaceHistory(Base):
	__tablename__ = "place_history"

	id = Column(Integer, primary_key=True, autoincrement=True)
	animal_id = Column(Integer, ForeignKey("animals.id"), nullable=False)
	datetime = Column(DateTime, nullable=False)
	tg_nickname = Column(String(50), nullable=False)
	arm_id = Column(Integer, nullable=False)

	# Связь с таблицей animals
	animal = relationship("Animal", back_populates="place_history")


class AnimalDead(Base):
	__tablename__ = "animals_dead"

	id = Column(Integer, primary_key=True, autoincrement=True)
	animal_id = Column(Integer, ForeignKey("animals.id"), nullable=False, unique=True)
	datetime = Column(DateTime, nullable=False)
	arms_id = Column(Integer, nullable=False)
	tg_nickname = Column(String(50), nullable=False)


# Определение ORM-модели для таблицы animals_outside
class AnimalOutside(Base):
	__tablename__ = "animals_outside"

	id = Column(Integer, primary_key=True, autoincrement=True)
	animal_id = Column(Integer, nullable=False)
	datetime = Column(DateTime, nullable=False)
	tg_nickname = Column(String(50), nullable=False)
	description = Column(String(50), nullable=False)
	arms_id = Column(Integer, nullable=False)


class ExchangeStorage:
	capture_datetime_string_format = "%d.%m.%Y %H:%M"
	capture_datetime_db_format = "%Y-%m-%d %H:%M:%S"

	@staticmethod
	def get_session():
		"""Создает и возвращает сессию."""
		return SessionLocal()

	@classmethod
	def insert_animal(cls, code, capture_datetime, place, pollution, weight=None, species=None, clinical_condition=None,
					  triage=None, catcher=None):
		capture_datetime = datetime.strptime(capture_datetime, cls.capture_datetime_string_format)
		capture_datetime_formatted = capture_datetime.strftime(cls.capture_datetime_db_format)

		db = cls.get_session()
		try:
			new_animal = Animal(
				bar_code=code,
				place_capture=place,
				capture_datetime=capture_datetime_formatted,
				degree_pollution=pollution,
				weight=weight,
				species=species,
				clinical_condition_admission=clinical_condition,
				triage=triage,
				catcher=catcher
			)
			db.add(new_animal)
			db.commit()
			db.refresh(new_animal)
			return new_animal.id
		except IntegrityError as e:  # Перехватываем IntegrityError
			db.rollback()
			if "Duplicate entry" in str(e):
				print(f"Ошибка: Животное с bar_code '{code}' уже существует.")
			else:
				print(f"Ошибка целостности данных: {e}")
			return None
		except Exception as e:
			db.rollback()
			print(f"Ошибка при добавлении животного: {e}")
			return None
		finally:
			db.close()

	# Вставка записей бумажного журнала первичной регистрации
	@classmethod
	def import_place_history(cls, code, registration_datetime, tg_nickname, arm_id):
		registration_datetime = datetime.strptime(registration_datetime, cls.capture_datetime_string_format)
		registration_datetime_formatted = registration_datetime.strftime(cls.capture_datetime_db_format)

		db = cls.get_session()
		try:
			# Найти animal_id по bar_code
			animal = db.query(Animal).filter_by(bar_code=code).first()
			if not animal:
				print(f"Животное с bar_code {code} не найдено.")
				return None

			new_place_history = PlaceHistory(
				animal_id=animal.id,
				datetime=registration_datetime_formatted,
				tg_nickname=tg_nickname,
				arm_id=arm_id
			)
			db.add(new_place_history)
			db.commit()
			db.refresh(new_place_history)
			return new_place_history.id
		except IntegrityError as e:  # Перехватываем IntegrityError
			db.rollback()
			if "Duplicate entry" in str(e):
				print(f"Ошибка: Запись '{code} - {registration_datetime}' уже существует.")
			else:
				print(f"Ошибка целостности данных: {e}")
			return None
		except Exception as e:
			db.rollback()
			print(f"Ошибка при добавлении записи в place_history: {e}")
			return None
		finally:
			db.close()

	@classmethod
	def get_animals_list(cls):
		"""
		Метод для получения списка животных с указанными полями, включая данные из place_history.
		:return: Список словарей, где каждый словарь представляет одно животное.
		"""
		db = cls.get_session()
		try:
			results = (
				db.query(
					Animal.bar_code,
					Animal.place_capture,
					Animal.capture_datetime,
					Animal.degree_pollution,
					Animal.species,
					Animal.catcher,
					PlaceHistory.datetime.label("place_history_datetime"),
				)
				.outerjoin(PlaceHistory, Animal.id == PlaceHistory.animal_id)
				.filter(PlaceHistory.arm_id == 1)
				.order_by(PlaceHistory.datetime)
				.all()
			)

			# Преобразование результатов в словари
			animals_list = []
			for row in results:
				animal_data = {
					"bar_code": row.bar_code,
					"place_capture": row.place_capture,
					"capture_datetime": row.capture_datetime.strftime(cls.capture_datetime_string_format),
					"degree_pollution": row.degree_pollution,
					"species": row.species,
					"catcher": row.catcher,
					"place_history_datetime": row.place_history_datetime.strftime(cls.capture_datetime_string_format)
					if row.place_history_datetime else None,
				}
				animals_list.append(animal_data)

			return animals_list
		except Exception as e:
			print(f"Ошибка при получении списка животных: {e}")
			return []
		finally:
			db.close()

	@classmethod
	def insert_dead(cls, code, dead_datetime, arms_id, tg_nickname):
		"""
		Метод для внесения записи о погибшем животном в таблицу animals_dead.

		:param code: QR-код животного (уникальный идентификатор).
		:param dead_datetime: Дата и время смерти животного (формат datetime или строка).
		:param arms_id: Идентификатор рабочего места.
		:param tg_nickname: Никнейм пользователя Telegram.
		:return: ID вставленной записи или None в случае ошибки.
		"""
		dead_datetime = datetime.strptime(dead_datetime, cls.capture_datetime_string_format)
		dead_datetime_formatted = dead_datetime.strftime(cls.capture_datetime_db_format)

		db = cls.get_session()
		try:
			animal = db.query(Animal).filter_by(bar_code=code).first()
			if not animal:
				print(f"Животное с bar_code {code} не найдено.")
				return None

			new_dead_record = AnimalDead(
				animal_id=animal.id,
				datetime=dead_datetime_formatted,
				arms_id=arms_id,
				tg_nickname=tg_nickname
			)
			db.add(new_dead_record)
			db.commit()
			db.refresh(new_dead_record)
			return new_dead_record.id
		except IntegrityError as e:  # Перехватываем IntegrityError
			db.rollback()
			if "Duplicate entry" in str(e):
				print(f"Ошибка: Запись '{code}' уже существует.")
			else:
				print(f"Ошибка целостности данных: {e}")
			return None
		except Exception as e:
			db.rollback()
			print(f"Ошибка при добавлении записи о погибшем животном: {e}")
			return None
		finally:
			db.close()

	@classmethod
	def get_animals_dead_list(cls):
		"""
		Метод для получения списка записей из таблицы animals_dead с JOIN таблицы animals.
		Дополнительно извлекается поле bar_code из таблицы animals.

		:return: Список словарей с данными из таблиц animals_dead и animals.
				 Возвращает пустой список в случае ошибки.
		"""
		db = cls.get_session()
		try:
			# Выполняем запрос с JOIN между AnimalDead и Animal
			query = (
				db.query(
					Animal.bar_code,
					AnimalDead.datetime,
				)
				.join(Animal, AnimalDead.animal_id == Animal.id)
				.all()
			)

			# Преобразуем результаты в список словарей
			result = [
				{
					"bar_code": row.bar_code,
					"datetime": row.datetime.strftime(cls.capture_datetime_string_format),
				}
				for row in query
			]
			return result
		except SQLAlchemyError as e:
			print(f"Ошибка при выполнении запроса: {e}")
			return []
		finally:
			db.close()

	@classmethod
	def get_animals_outside(cls):
		"""
		Метод для получения списка записей из таблицы animals_outside.

		:return: Список словарей с данными из таблицы animals_outside.
				 Возвращает пустой список в случае ошибки.
		"""
		db = cls.get_session()
		try:
			# Выполняем запрос к таблице animals_outside
			query = (
				db.query(
					Animal.bar_code,
					AnimalOutside.datetime,
					AnimalOutside.description
				)
				.join(Animal, AnimalOutside.animal_id == Animal.id)
				.all())

			# Преобразуем результаты в список словарей
			result = [
				{
					"bar_code": row.bar_code,
					"datetime": row.datetime.strftime(cls.capture_datetime_string_format),
					"description": row.description,
				}
				for row in query
			]
			return result

		except SQLAlchemyError as e:
			print(f"Ошибка при выполнении запроса: {e}")
			return []
		finally:
			db.close()
