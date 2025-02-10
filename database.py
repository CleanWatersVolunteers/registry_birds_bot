class Database:
	apm_list = ['apm1', 'apm2', 'apm3','apm4','apm5','apm6','apm7'] # todo for test, read from base according user access
	# apm_list = ['apm3'] 

	user_list = {}

	@classmethod
	def init(cls):
		cls.user_list = dict()
		# todo open database
		pass

	@classmethod
	def login(cls, name, pswd)->bool:
		if not name in cls.user_list:
			if pswd != '1111':
				return False
			cls.user_list[name] = dict()
			cls.user_list[name]["apm_list"] = cls.apm_list
			cls.user_list[name]["apm"] = None
			cls.user_list[name]["animal_id"] = None
		# return True if login OK else False
		return True

	@classmethod
	def get_user(cls, name)->{}:
		if name in cls.user_list:
			return cls.user_list[name]
		return {}


	@classmethod
	def insert_animal(cls, animal)->int:
		print("[DB] New animal:", animal)
		return 10 # id from db

	@classmethod
	def get_animal_id(cls, bar_code):
		if bar_code == 2222:
			return 10
		return None

	@classmethod
	def update_animal(cls, id, weight=None,species=None,clinical_condition_admission=None):
		print("[DB] Upd animal:", id)

	@classmethod
	def get_manipulations(cls, place_id)->[]:
		if place_id == 4:	# Первичка в стационаре
			return [
				{'id':'1', "name":"манипуляция 1"},
				{'id':'2', "name":"манипуляция 2"},
				{'id':'3', "name":"манипуляция 3"}
			]
		if place_id == 6:	# Нянька
			return [
				{'id':'4', "name":"нянька 1"},
				{'id':'5', "name":"нянька 2"},
				{'id':'6', "name":"нянька 3"}
			]
		return []

	@classmethod
	def insert_history(cls, manipulation_id, animal_id, arms_id, tg_nickname):
		print("[DB] Add history:", manipulation_id,animal_id,arms_id,tg_nickname)

	@classmethod
	def get_history(cls, animal_id):
		items = [
			{"id": "1", "animal_id": "10", "datetime": "23.12.2027 12:33",
			"manipulation_id": "нянька 1", "arm_id": "0","tg_nickname": "username"},
			{"id": "2", "animal_id": "10", "datetime": "23.14.2022 12:53",
			"manipulation_id": "нянька 2", "arm_id": "0","tg_nickname": "username"},
			{"id": "3", "animal_id": "10", "datetime": "23.16.2023 12:43",
			"manipulation_id": "манипуляция 3", "arm_id": "0","tg_nickname": "username"},
		 ]
		return items