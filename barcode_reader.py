import cv2 as cv
import numpy as np
from pyzbar.pyzbar import decode 


def barCodeReader(image) -> []:
    img = cv.imdecode(np.frombuffer(image, dtype=np.uint8), flags=1)
    barcodes = decode(img)
    codes = []
    if barcodes:
        for barcode in barcodes:
            if barcode.data != "":
                codes.append(barcode.data.decode("utf-8"))
    return codes
