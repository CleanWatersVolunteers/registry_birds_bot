class Database:
	# apm_list = ['apm1', 'apm2', 'apm3'] # todo for test, read from base according user access
	apm_list = ['apm5'] 

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
	def get_apm_list(cls, name)->[]:
		if name in cls.user_list:
			return cls.user_list[name]["apm_list"]
		return []

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
