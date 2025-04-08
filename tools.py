from const import const
from logs import my_logger
from storage import Storage
from timetools import now
from utils.spreadsheets import asyncAddVetOutgone
from utils.spreadsheets import asyncExportDeadAnimal


class Tools:

	@classmethod
	def checkLeave(cls, bar_code):
		if Storage.get_animal_dead(bar_code):
			return (
				const.animal_is_dead.format(code=bar_code),
				{const.text_ok: "entry_cancel"},
				None
			)
		if Storage.get_animal_outside(bar_code):
			return (
				const.animal_is_out.format(code=bar_code),
				{const.text_ok: "entry_cancel"},
				None
			)
		return False

	@classmethod
	def dead(cls, animal_id, bar_code, arm_id, user_name):
		Storage.create_dead_animal(animal_id, arm_id, user_name)
		my_logger.debug('Start asyncExportDeadAnimal')
		asyncExportDeadAnimal(bar_code, now())
		# todo Убрать хардкод конда появится вторая локация
		reg_arm_id = 1
		reg_datetime = Storage.get_reg_time(animal_id, reg_arm_id)
		if reg_datetime is not None:
			my_logger.debug('Start asyncAddVetOutgone')
			asyncAddVetOutgone(bar_code, reg_datetime.strftime(const.datetime_format), now(), 'гибель')

	@classmethod
	def getAnimalTitle(cls, animal):
		if animal['species'] is None:
			return f'{const.text_animal_number} {animal['bar_code']}'
		else:
			return f'{const.text_animal_number} {animal['bar_code']} - {animal['species']}'

	# Возвращает время регистрации в стационаре
	@classmethod
	def getHospitalTime(cls, location_id, animal_id):
		hospital_arm_id = Storage.get_arm_id(const.HOSPITAL_ARM_ID, location_id)
		return Storage.get_reg_time(animal_id, hospital_arm_id)
