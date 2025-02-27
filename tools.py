from const import const
from storage import storage


class Tools:

	@classmethod
	def checkDead(cls, bar_code):
		deadAnimal = storage.get_animal_dead(bar_code)
		if deadAnimal:
			return (
				const.animal_is_dead.format(code=bar_code),
				{const.text_ok: "entry_cancel"},
				None
			)
		return False
