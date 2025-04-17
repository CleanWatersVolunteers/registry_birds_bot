import os
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.exc import IntegrityError, SQLAlchemyError  # Основное исключение SQLAlchemy
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

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
	name = Column(String(50), nullable=False)

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
	def getSession():
		return SessionLocal()

	@classmethod
	def insertAnimal(cls, code, capture_datetime, place, pollution, weight=None, species=None, clinical_condition=None,
					 triage=None, catcher=None, name=None):
		print(
			f'insertAnimal: code: {code}, capture_datetime: {capture_datetime}, place: {place}, pollution: {pollution}, weight: {weight}, species: {species}, clinical_condition: {clinical_condition}, triage: {triage}, catcher: {catcher}')
		capture_datetime = datetime.strptime(capture_datetime, cls.capture_datetime_string_format)
		capture_datetime_formatted = capture_datetime.strftime(cls.capture_datetime_db_format)

		db = cls.getSession()
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
				catcher=catcher,
				name=name
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

	@classmethod
	def getAnimal(cls, name=None, code=None):
		db = cls.getSession()
		try:
			if name is not None:
				result = db.query(Animal).filter_by(name=name).first()
			else:
				result = db.query(Animal).filter_by(bar_code=code).first()
			return result
		except Exception as e:
			db.rollback()
			print(f"Ошибка getAnimal(): {e}")
			return None
		finally:
			db.close()

	@classmethod
	def getPlaceHistory(cls, animal_id, arm_id):
		db = cls.getSession()
		try:
			result = db.query(PlaceHistory).filter_by(animal_id=animal_id, arm_id=arm_id).first()
			return result
		except Exception as e:
			db.rollback()
			print(f"Ошибка getPlaceHistory(): {e}")
			return None
		finally:
			db.close()

	@classmethod
	def getDeadInfo(cls, animal_id):
		db = cls.getSession()
		try:
			result = db.query(AnimalDead).filter_by(animal_id=animal_id).first()
			return result
		except Exception as e:
			db.rollback()
			print(f"Ошибка getDeadInfo(): {e}")
			return None
		finally:
			db.close()

	@classmethod
	def getAnimalOutside(cls, animal_id):
		db = cls.getSession()
		try:
			result = db.query(AnimalOutside).filter_by(animal_id=animal_id).first()
			return result
		except Exception as e:
			db.rollback()
			print(f"Ошибка getAnimalOutside(): {e}")
			return None
		finally:
			db.close()

	# Вставка записей бумажного журнала первичной регистрации
	@classmethod
	def importPlaceHistory(cls, animal_id, date, tg_nickname, arm_id):
		print(
			f'importPlaceHistory animal_id: {animal_id}, date: {date}, tg_nickname: {tg_nickname}, arm_id: {arm_id}')
		db = cls.getSession()
		try:
			date = datetime.strptime(date, cls.capture_datetime_string_format)
			date_formatted = date.strftime(cls.capture_datetime_db_format)
			new_place_history = PlaceHistory(
				animal_id=animal_id,
				datetime=date_formatted,
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
				print(f"Ошибка: Запись '{animal_id} - {date}' уже существует.")
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
	def getAnimalsList(cls):
		"""
		Метод для получения списка животных с указанными полями, включая данные из place_history.
		:return: Список словарей, где каждый словарь представляет одно животное.
		"""
		db = cls.getSession()
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
	def insertDead(cls, animal_id, dead_datetime, arms_id, tg_nickname):
		"""
		Метод для внесения записи о погибшем животном в таблицу animals_dead.

		:param animal_id: Идентификатор животного (уникальный идентификатор).
		:param dead_datetime: Дата и время смерти животного (формат datetime или строка).
		:param arms_id: Идентификатор рабочего места.
		:param tg_nickname: Никнейм пользователя Telegram.
		:return: ID вставленной записи или None в случае ошибки.
		"""
		print(
			f'insertDead: animal_id: {animal_id}, dead_datetime: {dead_datetime}, arms_id: {arms_id}, tg_nickname: {tg_nickname}')

		db = cls.getSession()
		try:
			dead_datetime = datetime.strptime(dead_datetime, cls.capture_datetime_string_format)
			dead_datetime_formatted = dead_datetime.strftime(cls.capture_datetime_db_format)

			new_dead_record = AnimalDead(animal_id=animal_id, datetime=dead_datetime_formatted, arms_id=arms_id,
										 tg_nickname=tg_nickname)
			db.add(new_dead_record)
			db.commit()
			db.refresh(new_dead_record)
			return new_dead_record.id
		except IntegrityError as e:  # Перехватываем IntegrityError
			db.rollback()
			if "Duplicate entry" in str(e):
				print(f"Ошибка: Запись '{animal_id}' уже существует.")
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
	def getAnimalsDeadList(cls):
		"""
		Метод для получения списка записей из таблицы animals_dead с JOIN таблицы animals.
		Дополнительно извлекается поле bar_code из таблицы animals.

		:return: Список словарей с данными из таблиц animals_dead и animals.
				 Возвращает пустой список в случае ошибки.
		"""
		db = cls.getSession()
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
	def insertOutside(cls, code, date, arms_id, tg_nickname, description):
		"""
		Метод для внесения записи о выпущенном животном в таблицу animals_outside.

		:param code: QR-код животного (уникальный идентификатор).
		:param datetime: Дата и время выпуска животного (формат datetime или строка).
		:param arms_id: Идентификатор рабочего места.
		:param tg_nickname: Никнейм пользователя Telegram.
		:return: ID вставленной записи или None в случае ошибки.
		"""
		print(
			f'insertOutside: code: {code}, date: {date}, arms_id: {arms_id}, tg_nickname: {tg_nickname}')
		date = datetime.strptime(date, cls.capture_datetime_string_format)
		datetime_formatted = date.strftime(cls.capture_datetime_db_format)

		db = cls.getSession()
		try:
			animal = db.query(Animal).filter_by(bar_code=code).first()
			if not animal:
				print(f"Животное с bar_code {code} не найдено.")
				return None

			new_dead_record = AnimalOutside(
				animal_id=animal.id,
				datetime=datetime_formatted,
				arms_id=arms_id,
				tg_nickname=tg_nickname,
				description=description
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
	def getAnimalsOutside(cls):
		"""
		Метод для получения списка записей из таблицы animals_outside.

		:return: Список словарей с данными из таблицы animals_outside.
				 Возвращает пустой список в случае ошибки.
		"""
		db = cls.getSession()
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
