import json

class Config:
    def __init__(self, dbconfig):
        self.database = dbconfig['database']
        self.user = dbconfig['user']
        self.password = dbconfig['password']
        self.host = dbconfig['host']

    def __repr__(self):
        return f"Config(database={self.database}, user={self.user}, password={self.password}, host={self.host})"

    @classmethod
    def load_config_from_json(cls):
        with open("config.json", 'r') as file:
            dbconfig = json.load(file)
        return dbconfig