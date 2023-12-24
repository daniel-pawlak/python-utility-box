import cv2
from pytesseract import Output
from matplotlib import pyplot as plt
from PIL import Image
import pytesseract
import re

from documents_analyzer.documents_analyzer import pytesseract_path, custom_config, IMGS_DIR

pytesseract.pytesseract.tesseract_cmd = pytesseract_path

def rect_mini(self, pdf_name, k):
    # look for boxes marked as signed with usage of rectangles_rec function. If found, then insert data in correct place
    img_name = "{}{}".format(pdf_name, k)
    signed = 0
    if self.rectangles_rec(img_name) == True:
        signed = 1
    return signed

def rect_mini_ups(self, pdf_name, k,  index_line, index_sign_line):
    # look for boxes marked as signed with usage of rectangles_rec function. If found, then insert data in correct place
    img_name = "{}{}".format(pdf_name, k)
    signed = 0
    if self.rectangles_rec_ups(img_name,  index_line, index_sign_line) == True:
        signed = 1
    return signed

def file_name_func(k, file_format, pdf_name):
    # process file name based on file format
    if file_format == 0:         
        file_name = "{}{}.jpg".format(pdf_name, k)
    elif file_format == 1:
        file_name = "{}.jpg".format(pdf_name)
    elif file_format == 2:
        file_name = pdf_name
    elif file_format == 3:
        file_name = pdf_name    
    elif file_format == 4:
        file_name = pdf_name 

    return file_name

def lines_position(d, index_line, index_sign_line):
    # get lines coordinates for further checking checked boxes
    data = {}
    for i in range(len(d['line_num'])):
        txt = d['text'][i]
        block_num = d['block_num'][i]
        line_num = d['line_num'][i]
        top, left = d['top'][i], d['left'][i]
        width, height = d['width'][i], d['height'][i]
        if not (txt == '' or txt.isspace()):
            tup = (txt, left, top, width, height)
            if block_num in data:
                if line_num in data[block_num]:
                    data[block_num][line_num].append(tup)
                else:
                    data[block_num][line_num] = [tup]
            else:
                data[block_num] = {}
                data[block_num][line_num] = [tup]

    linedata = {}
    idx = 0
    for _, b  in data.items():
        for _, l in b.items():
            linedata[idx] = l
            idx += 1
    line_idx = 1
    index_line_pos, index_sign_line_pos = (0, 0), (0, 0)
    for _, line in linedata.items():
        xmin, ymin = line[0][1], line[0][2]
        xmax, ymax = (line[-1][1] + line[-1][3]), (line[-1][2] + line[-1][4])
        line_idx += 1
        if ymax + 30 >= index_line and ymin - 30 <= index_line:
            index_line_pos = (ymin, ymax)
        elif ymax + 30 >= index_sign_line and ymin - 30 <= index_sign_line:
            index_sign_line_pos = (ymin, ymax)

    return index_line_pos, index_sign_line_pos

def lines_remover(self, file_name):
    # remove lines from file to make it more readable for script
    # To convert the Image From GIF to JPG
    if self.file_format == 3:
        img = Image.open(IMGS_DIR + file_name).convert('RGB')
        new_name = IMGS_DIR + file_name.replace('.GIF', '') + '.jpg'
        img.save(new_name)
        image = cv2.imread(new_name)
        file_name = file_name.replace('.GIF', '') + '.jpg'
    else:
        image = cv2.imread(IMGS_DIR+file_name)
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

def resizing(image):
    # resize image with given variables to make it more readable
    image = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)      # reshape image, make it bigger and easier to read
    d = pytesseract.image_to_data(image, config=custom_config, output_type=Output.DICT)
    return d

def shrinking(image):
    # resize image with given variables to make it more readable
    image = cv2.resize(image, None, fx=0.6, fy=0.6, interpolation=cv2.INTER_CUBIC)      # reshape image, make it smalle and easier to read for 
    d = pytesseract.image_to_data(image, config=custom_config, output_type=Output.DICT)
    return d 

def words_loop(image, d):
    # loop through every found word and look for date and signature
    text = 'Signature'      # text to be found inside file
    text_everify1 = 'E-Verify'
    text_everify2 = 'paycom'
    text_everify3 = 'CORTECH'
    text_everify4 = 'EVerify'
    text_everify5 = 'Verify'
    text_everify6 = 'Verification'

    text_ups = 'ups'
    text_ups_onboarding1 = 'upspre-hire'
    text_ups_onboarding2 = 'upsprehire'
    text_ups_onboarding3 = 'upson-boarding'
    text_ups_onboarding4 = 'upspre-hire'

    text_exhibit1 = 'exhibit'
    text_exhibit2 = 'exhibit12'
    text_exhibit3 = 'code'
    text_exhibit4 = 'codeofconduct'
    text_exhibit5 = 'acknowledgment'
    text_exhibit6 = 'acknowledgmentofstatus'
    text_exhibit7 = 'computer'
    text_exhibit8 = 'computeruseguidelines'
    text_exhibit9 = 'safe'
    text_exhibit10 = 'safeworkmethods'
    # delete empty values

    n_boxes = len(d['text'])
    conf = 0
    index = 0
    too_little = 0

    for i in range(n_boxes):
        # condition to only pick boxes with a confidence > 30%
        if float(d['conf'][i]) > 30:
            conf += 1   
            if re.match(text_everify1, d['text'][i]) or re.match(text_everify2, d['text'][i]) or re.match(text_everify3, d['text'][i]) or re.match(text_everify4, d['text'][i]):
                index = 1
                break
            elif re.match(text_everify5, d['text'][i]):
                new_text = d['text'][i-1] + d['text'][i]
                if new_text == text_everify4 or new_text == text_everify1:
                    index = 1
                    break
                else:
                    index = 0
            elif re.match(text_everify6, d['text'][i]):
                new_text = d['text'][i-1] + d['text'][i] + d['text'][i+1]
                if new_text == 'CaseVerificationNumber:':
                    index = 1
                    break
                else:
                    index = 0

            elif re.match(text_ups, d['text'][i].lower()):
                ups_text = d['text'][i].lower() + d['text'][i+1].lower()
                ups_text2 = ups_text + d['text'][i+2].lower()
                if ups_text == text_ups_onboarding1 or ups_text == text_ups_onboarding2 or ups_text == text_ups_onboarding4 or ups_text2 == text_ups_onboarding3 or d['text'][i-2].lower() == 'ltd.':
                    index = 2
                    break
                else:
                    pass        
            elif re.match(text_exhibit1, d['text'][i].lower()):
                exhibit_text = d['text'][i] + d['text'][i+1]
                if re.search(text_exhibit2, exhibit_text.lower()):
                    index = 3
                    break
            elif re.match(text_exhibit3, d['text'][i].lower()):
                exhibit_text = d['text'][i] + d['text'][i+1] + d['text'][i+2]
                if re.search(text_exhibit4, exhibit_text.lower()):
                    index = 3
                    break
            elif re.match(text_exhibit5, d['text'][i].lower()):
                exhibit_text = d['text'][i] + d['text'][i+1] + d['text'][i+2]
                if re.search(text_exhibit6, exhibit_text.lower()):
                    index = 3
                    break
            elif re.match(text_exhibit7, d['text'][i].lower()):
                exhibit_text = d['text'][i] + d['text'][i+1] + d['text'][i+2]
                if re.search(text_exhibit8, exhibit_text.lower()):
                    index = 3
                    break
            elif re.match(text_exhibit9, d['text'][i].lower()):
                exhibit_text = d['text'][i] + d['text'][i+1] + d['text'][i+2]
                if re.search(text_exhibit10, exhibit_text.lower()):
                    index = 3
                    break
            else:
                (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                image = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)    # green
                index = 0
        elif float(d['conf'][i]) > 10 and float(d['conf'][i]) <= 30: 
            if re.match(text_everify1, d['text'][i]) or re.match(text_everify2, d['text'][i]) or re.match(text_everify3, d['text'][i]) or re.match(text_everify4, d['text'][i]):
                too_little += 1

    return too_little, index

def display_image(image):
    # display image with marked boxes 
    b,g,r = cv2.split(image)
    rgb_img = cv2.merge([r,g,b])
    plt.figure(figsize=(16,12))
    plt.imshow(rgb_img)
    plt.title('SAMPLE DOCUMENT WITH WORD LEVEL BOXES')
    plt.show()
