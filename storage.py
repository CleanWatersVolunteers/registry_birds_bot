class storage:
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
        bird["stage0"] = None
        bird["stage1"] = None
        bird["stage2"] = None
        bird["stage3"] = None
        bird["stage4"] = None
        bird["stage5"] = None
        bird["stage6"] = None
        bird["stage7"] = None
        return bird

    @classmethod
    def __create_user(cls):
        user = {"location":None, "apm":None, "code":None}
        return user

    @classmethod
    def init(cls, users, birds):
        cls.__users = {}
        cls.__birds = {}
        # with open(users, 'r') as f:
        #     json.dump(self.__users, f)
        # with open(birds, 'r') as f:
        #     json.dump(self.__birds, f)

    @classmethod
    def add_bird(cls, code)->bool:
        if code in cls.__birds:
            return False
        cls.__birds[code] = cls.__create_bird()
        return True

    @classmethod
    def upd_bird(cls, code, key, val)->bool:
        if code in cls.__birds:
            cls.__birds[code][key] = val
            return True
        return False

    @classmethod
    def get_bird(cls, code):
        if code == None:
            return None
        if code in cls.__birds:
            return cls.__birds[code]
        return None

    @classmethod
    def add_user(cls, username)->bool:
        if username in cls.__users:
            return False
        cls.__users[username] = cls.__create_user()
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
        