import cv2 as cv
import numpy as np
from pyzbar.pyzbar import decode 

from const import const

code_animal_text = 'Введите код животного'


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

def code_request(apm_list):
	if len(apm_list) > 1:
		return code_animal_text, {const.text_cancel:'entry_menu'}
	return code_animal_text, {const.text_exit:'entry_exit'}

def code_parse(code)->int:
	# code from text
	if isinstance(code, str):
		if code.isdigit():
			return int(code)
		return 0

	# code from photo
	codes = code_reader(code)
	if len(codes) == 1:
		if codes[0].isdigit():
			return codes[0]
	return 0
	
