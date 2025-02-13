class Database:
	# apm_list = ['apm1', 'apm2', 'apm3','apm4','apm5','apm6','apm7'] # todo for test, read from base according user access
	apm_list = ['apm3'] 

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
	def clear_user(cls, name)->None:
		if name in cls.user_list:
			del cls.user_list[name]