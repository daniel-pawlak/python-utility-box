import pytesseract
from pytesseract import Output
import cv2 
from matplotlib import pyplot as plt
import numpy as np

def gray_scale(image):
    """convert image to gray scale"""
    gray_scale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # image thresholding
    # _, img_bin = cv2.threshold(gray_scale_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    _, img_bin = cv2.threshold(gray_scale_image, 100, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    img_bin = 255 - img_bin

    # Image.fromarray(img_bin).show()

    return img_bin

def resizing(image, custom_config):
    # resize image with given variables to make it more readable
    image = cv2.resize(image, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)      # reshape image, make it bigger and easier to read
    d = pytesseract.image_to_data(image, config=custom_config, output_type=Output.DICT)
    return d

def display_image(image):
    """display image"""
    b,g,r = cv2.split(image)
    rgb_img = cv2.merge([r,g,b])
    plt.figure(figsize=(16,12))
    plt.imshow(rgb_img)
    plt.title('SAMPLE DOCUMENT WITH WORD LEVEL BOXES')
    plt.show()

def lines_remover(file_name):
    # remove lines from file to make it more readable for script
    image = cv2.imread(file_name)
    try:
        result = image.copy()
    except:
        result = image
    # if image is not read properl
    try:
        gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    except:
        gray = cv2.cvtColor(image,cv2.COLOR_RGB2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    # Remove horizontal lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40,1))
    remove_horizontal = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    cnts = cv2.findContours(remove_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv2.drawContours(result, [c], -1, (255,255,255), 5)

    # Remove vertical lines
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,40))
    remove_vertical = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
    cnts = cv2.findContours(remove_vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv2.drawContours(result, [c], -1, (255,255,255), 5)
    cv2.imwrite(r"path\Images\{}".format(file_name), result)

    return result
 
def remove_background(file):
    low_green = np.array([25, 52, 72])
    high_green = np.array([102, 255, 255])

    while True:
        img = cv2.imread(file)
        img = cv2.resize(img, (900, 650), interpolation=cv2.INTER_CUBIC)

        # convert BGR to HSV
        imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # create the Mask
        mask = cv2.inRange(imgHSV, low_green, high_green)
        # inverse mask
        # mask = 255-mask
        res = cv2.bitwise_and(img, img, mask=mask)

        cv2.imshow("mask", mask)
        cv2.imshow("cam", img)
        cv2.imshow('res', res)
        cv2.waitKey(10)
