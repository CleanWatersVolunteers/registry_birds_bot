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
	def create_user(cls, name, location_id, password=None):
		if not name in cls.user_list:
			cls.user_list[name] = dict()
			cls.user_list[name]["apm_list"] = cls.apm_list
			cls.user_list[name]["apm"] = None
			cls.user_list[name]["location_id"] = location_id
			cls.user_list[name]["animal_id"] = None
			if password is not None:
				cls.user_list[name]['pass'] = password
			else:
				cls.user_list[name]['pass'] = None
			return cls.user_list[name]

	@classmethod
	def get_user(cls, name) -> {}:
		if name in cls.user_list:
			return cls.user_list[name]
		return {}

	@classmethod
	def clear_user(cls, name) -> None:
		if name in cls.user_list:
			del cls.user_list[name]
