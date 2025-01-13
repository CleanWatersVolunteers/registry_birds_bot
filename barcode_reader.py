import cv2 as cv
from pyzbar.pyzbar import decode 

def barCodeReader(image, sim=False) -> None:
    img = cv.imread(image)
    barcodes = decode(img)

    if not barcodes:
        print("barcodes not detected")
    else:
        for barcode in barcodes:
            (x, y, w, h) = barcode.rect
            cv.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 5)
        
            if barcode.data != "":
                data = barcode.data
                print(barcode.data)        

        if sim:
            cv.imshow("Image", img) 
            cv.waitKey(0) 
            cv.destroyAllWindows() 


if __name__ == '__main__':
    image = 'image3.png'
    barCodeReader(image)

