from const import const
from storage import Storage


class Tools:

	@classmethod
	def checkLeave(cls, bar_code):
		deadAnimal = Storage.get_animal_dead(bar_code)
		if deadAnimal:
			return (
				const.animal_is_dead.format(code=bar_code),
				{const.text_ok: "entry_cancel"},
				None
			)
		outAnimal = Storage.get_animal_outside(bar_code)
		if outAnimal:
			return (
				const.animal_is_out.format(code=bar_code),
				{const.text_ok: "entry_cancel"},
				None
			)
		return False
