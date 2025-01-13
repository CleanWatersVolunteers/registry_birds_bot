from datetime import datetime
import pytz

# time_tz = lambda tz: datetime.utcnow().astimezone(pytz.timezone(tz))
# curr_time = lambda : time_tz('Etc/GMT-3').isoformat().split('+')[0]
curr_time = lambda: datetime.now().isoformat()

class Bird(object):
    def __init__(self, code):
        super(Bird, self).__init__()
        self.id = code
        self.capture_place = None
        self.capture_date = curr_time()
        self.polution = None
        self.mass = None
        self.species = None
        self.sex = None
        self.clinic_state = None
        self.stage = {"apm1":"","apm2":"","apm3":"","apm4":"","apm5":"","apm6":"","apm7":""}

    def set_capture(self, place, date):
        self.capture_place = place
        self.capture_date = date
    def set_polution(self, polution):
        self.polution = polution
    def set_mass(self, mass):
        self.mass = mass
    def set_species(self, species):
        self.species = species
    def set_sex(self, sex):
        self.sex = sex
    def set_clinic_state(self, clinic_state):
        self.clinic_state = clinic_state
    def set_location(self, location):
        self.__location = location
    def upd_stage(self, num, location):
        self.stage[f'apm{num}'] = location