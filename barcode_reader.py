import cv2 as cv
from pyzbar.pyzbar import decode 

# pip install pyzbar
# sudo apt install libzbar0


def barCodeReader(image, sim=False) -> []:
    barcodes = decode(cv.imread(image))
    codes = []

    if barcodes:
        for barcode in barcodes:
            if barcode.data != "":
                codes.append(barcode.data.decode("utf-8"))
    return codes
