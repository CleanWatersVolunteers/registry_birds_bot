import cv2 as cv
import numpy as np
from pyzbar.pyzbar import decode

from const import const
from storage import storage

code_animal_text = 'Сфотографируйте QR-код нажав на `скрепку` ниже или введите номер животного вручную.'
duty_is_end = 'Смена закончена, введите новый пароль'


def code_reader(image) -> []:
	img = cv.imdecode(np.frombuffer(image, dtype=np.uint8), flags=1)
	barcodes = decode(img)
	codes = []
	if barcodes:
		for barcode in barcodes:
			if barcode.data != "":
				codes.append(barcode.data.decode("utf-8"))
	return codes


##################################
# Global API
##################################

def code_request(user):
	if user['pass'] is not None:
		arm_list = storage.get_arm_access(const.now(), password=user['pass'])
		if len(arm_list) > 0:
			return code_animal_text, {const.text_exit: 'entry_exit'}, True
		else:
			return duty_is_end, None, False
	else:
		return code_animal_text, {const.text_cancel: 'entry_menu'}, True


def code_parse(code) -> int:
	# code from text
	if isinstance(code, str):
		if code.isdigit():
			return int(code)
		return 0

	# code from photo
	codes = code_reader(code)
	if len(codes) == 1:
		if codes[0].isdigit():
			return int(codes[0])
	return 0
