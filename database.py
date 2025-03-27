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
	def create_user(cls, user_id, name, location_id, password=None):
		if not user_id in cls.user_list:
			cls.user_list[user_id] = dict()
			if name is None:
				cls.user_list[user_id]['name'] = user_id
			else:
				cls.user_list[user_id]['name'] = name
			cls.user_list[user_id]['apm_list'] = cls.apm_list
			cls.user_list[user_id]['apm'] = None
			cls.user_list[user_id]['location_id'] = location_id
			cls.user_list[user_id]['animal_id'] = None
			if password is not None:
				cls.user_list[user_id]['pass'] = password
			else:
				cls.user_list[user_id]['pass'] = None
			return cls.user_list[user_id]

	@classmethod
	def get_user(cls, user_id) -> {}:
		if user_id in cls.user_list:
			return cls.user_list[user_id]
		return {}

	@classmethod
	def clear_user(cls, user_id) -> None:
		if user_id in cls.user_list:
			del cls.user_list[user_id]
