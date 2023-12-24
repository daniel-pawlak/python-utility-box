import cv2
from pytesseract import Output
import pytesseract
import re
import numpy as np

from src.utils import file_name_func, lines_remover, resizing, lines_position, rect_mini, rect_mini_ups
from documents_analyzer.documents_analyzer import pytesseract_path, custom_config

pytesseract.pytesseract.tesseract_cmd = pytesseract_path

def ups_words_loop(image, d, date_patterns, row):
    date_short_eu, date_short_us, date_month, months, only_year, date_pattern, date_pattern2, date_pattern3, date_pattern4 = [*date_patterns]
    # loop through every found word and look for date and signature
    date = ''
    # delete empty values
    if row == 0:
        for i in range(20):
            try:
                if len(d['text'][i]) == 0 or d['text'][i] == None:
                    for key in d.keys():
                        del d[key][i]
            except:
                pass
    n_boxes = len(d['text'])
    index = 0
    index_sign = 0
    index_printed = 0
    too_little = 0
    ups_index = 0
    text_everify1 = 'e-verify'
    text_everify2 = 'everify'

    for i in range(n_boxes): 
        # condition to only pick boxes with a confidence > 30%
        if float(d['conf'][i]) > 30:
            if re.match(date_pattern, d['text'][i]) or re.match(date_pattern2, d['text'][i]) or re.match(date_pattern3, d['text'][i]) or re.match(date_pattern4, d['text'][i]):
                (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                image = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)    # red
                if i > 5:
                    date = d['text'][i]
            elif re.match(date_short_eu, d['text'][i]) or re.match(date_short_us, d['text'][i]):
                try:
                    new_date = d['text'][i] + d['text'][i + 1] + d['text'][i + 2]
                    if re.match(date_pattern, new_date) or re.match(date_pattern2, new_date) or re.match(date_pattern3, new_date) or re.match(date_pattern4, new_date):
                        if re.match('^([0-2][0-9]|((19|20)\d\d))', d['text'][i + 2]):
                            index = i + 3
                            date = new_date
                except:
                    pass

            if re.match(text_everify1, d['text'][i].lower()) or re.match(text_everify2, d['text'][i].lower()):
                (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                image = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)    # red
                if d['text'][i+1].lower() == 'completed' or d['text'][i+1].lower() == 'completed?':
                    index = i + 1
                elif d['text'][i+2].lower() == 'completed' or d['text'][i+2].lower() == 'completed?':
                    index = i + 2
                elif d['text'][i+1].lower() == 'process':
                    index_sign = i + 11
            else:
                (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                image = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)    # green
            
        elif float(d['conf'][i]) > 10 and float(d['conf'][i]) <= 30: 
            if re.match(text_everify1, d['text'][i].lower()) or re.match(text_everify2, d['text'][i].lower()):
                too_little += 1
        else:
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            image = cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)    # blue

    return too_little, index, index_sign, image, ups_index, index_printed, date

def ups_pages_loop(df, failures, start, num, row, pdf_index, pdf_name, file_format):
    # loop through every page and look for date and signature with usage of different functions, like words_loop
    pdf_index = pdf_index
    signed = 0
    # nonlocal failures   # to copy not signed file to a different directory
    for k in range(start, num):
        if k == 0:
            if pdf_name.endswith(".pdf"):   
                file_name = file_name_func(k, file_format)
            else:
                file_name = pdf_name
        else:
            file_name = file_name_func(k, file_format)
        image = lines_remover(file_name)
        # create copy in case of enlarging
        image_copy = image.copy()       
        # read image 
        d = pytesseract.image_to_data(image, config=custom_config, output_type=Output.DICT)
        # loop through every word
        too_little, index, index_sign, image, ups_index, index_printed, date = ups_words_loop(image, d)
        # resize image if it's too little
        if too_little != 0:
            d = resizing(image_copy)
            too_little, index, index_sign, image, ups_index, index_printed, date = ups_words_loop(image_copy, d)

        n_boxes = len(d['text'])
        # if date exists, look for signature in 2 ways: one step to the right from index or one step to the right from 'Signature'
        marked_list = ['x', 'y', 'v', 'xyes', '_xyes', 'xx', 'x_yes__no', 'x_yes', 'y_', '_x', '_x_yes', 'x_yes___no', 'vv', 'ves', 'v_', '_x_',
            '_x__yes', '_x__']
        if index > 1:
            try:
                if index_sign < n_boxes:
                    if d['text'][index+1].lower() in marked_list:
                        signed += 1
                    elif d['text'][index+1].lower() == 'yes':
                        if len(d['text'][index+2].lower()) != 0:
                            if d['text'][index+2].lower() in marked_list:
                                signed += 1
                            elif d['text'][index+2].lower() == 'or' or d['text'][index+2].lower() == 'i-9':
                                signed += 1
                        else:
                            if d['text'][index+3].lower() == 'or' or d['text'][index+3].lower() == 'i-9':
                                signed += 1                                 
                    elif len(d['text'][index+1].lower()) == 0:
                        if d['text'][index+2].lower() == 'yes':
                            if (d['text'][index+3].lower()) != 0:
                                if d['text'][index+3].lower() == 'or' or d['text'][index+3].lower() == 'i-9':
                                    signed += 1                                         
                            else:
                                if d['text'][index+4].lower() == 'or' or d['text'][index+4].lower() == 'i-9':
                                    signed += 1           
                    if d['text'][index_sign+1].lower() in marked_list:
                        signed += 1
                    elif d['text'][index_sign+1].lower() == 'yes':
                        if len(d['text'][index_sign+2].lower()) != 0:
                            if d['text'][index_sign+2].lower() in marked_list:
                                signed += 1
                            else:
                                if d['text'][index_sign+3].lower() == 'or' or d['text'][index_sign+3].lower() == 'i-9':
                                    signed += 1 
                        # new functionality
                        elif len(d['text'][index_sign+2].lower()) == 0 and d['text'][index_sign+3].lower() == 'i-9':
                            signed += 1                                            
                    elif len(d['text'][index_sign+1].lower()) == 0:
                        if d['text'][index_sign+2].lower() == 'yes':
                            if (d['text'][index_sign+3].lower()) != 0:
                                if d['text'][index_sign+3].lower() == 'or' or d['text'][index_sign+3].lower() == 'i-9':
                                    signed += 1                                         
                            else:
                                if d['text'][index_sign+4].lower() == 'or' or d['text'][index_sign+4].lower() == 'i-9':
                                    signed += 1   
                    if d['text'][index_sign+1].lower() == 'date' or d['text'][index_sign+1].lower() == 'date.':
                        if d['text'][index_sign+2].lower() in marked_list:
                            signed += 1
                        elif d['text'][index_sign+2].lower() == 'yes' and d['text'][index_sign+3].lower() != 'no' and d['text'][index_sign+4].lower() != 'no' and d['text'][index_sign+5].lower() != 'no':
                            signed += 1
            
            except:
                try:
                    pdf_index = rect_mini(pdf_name, k)
                except:    
                    pass
        if k == 0:
            if signed == 0:
                index_line = d['top'][index]
                index_sign_line = d['top'][index_sign]
                try:
                    index_line_pos, index_sign_line_pos = lines_position(d, index_line, index_sign_line)
                    signed = rect_mini_ups(pdf_name, k, index_line_pos, index_sign_line_pos)
                except:
                    pass

    df.loc[row, ['File Name']] = pdf_name
    if signed > 0:
        df.loc[row, ['Found']] = 'Signed'
        df.loc[row, ['Date']] = date
    else:
        df.loc[row, ['Not Found']] = 'Not signed'

        failures += 1   # to copy not signed file to a different directory
    
    row += 1   

    return d

def ups_signature(d, i):
    # check if it is UPS file, if so then look for signature given in a different way than usually
    n_boxes = len(d['text'])
    text = 'Signature'
    text_long = 'Signature Transaction ID:'
    for i in range(n_boxes):
        if re.match(text, d['text'][i]):
            if re.match(text_long, (d['text'][i] + ' ' + d['text'][i+1] + ' ' + d['text'][i+2])):
                if len(d['text'][i+4]) > 10:
                    return True
                else:
                    return False
            else:
                return 'empty'

def rectangles_rec(img_name):
    # look for rectangles that have information whether it is marked as signed or not in case of having no common signature
    # read image into array
    image_array = cv2.imread('path\Images\\{}.jpg'.format(img_name))     # may be changed

    # convering image to gray scale
    gray_scale_image = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)

    # image thresholding
    _, img_bin = cv2.threshold(gray_scale_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    img_bin = 255 - img_bin

    # Image.fromarray(img_bin).show()

    # set min width to detect horizontal lines
    line_min_width = 15
    # kernel to detect horizontal lines
    kernal_h = np.ones((1,line_min_width), np.uint8)
    # kernel to detect vertical lines
    kernal_v = np.ones((line_min_width,1), np.uint8)
    # horizontal kernel on the image
    img_bin_h = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, kernal_h)
    # verical kernel on the image
    img_bin_v = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, kernal_v)
    # combining the image
    img_bin_final=img_bin_h|img_bin_v
    # Image.fromarray(img_bin).show()
    final_kernel = np.ones((3,3), np.uint8)
    img_bin_final=cv2.dilate(img_bin_final,final_kernel,iterations=1)
    _, labels, stats,_ = cv2.connectedComponentsWithStats(~img_bin_final, connectivity=8, ltype=cv2.CV_32S)

    quotients = []
    areas = 0
    for x,y,w,h,area in stats[2:]:
        if area >= 100:
            areas += 1
            cv2.rectangle(image_array,(x,y),(x+w,y+h),(255,255,0),2)
        
            area2 = 0
            black = np.array([0, 0, 0])

            for i in range(x, x+w):
                for j in range(y, y+h):
                    if img_bin[j, i].all() != black.all():
                        area2 += 1
            
            quotient = area2/area
            if quotient > 0.2:
                quotients.append(quotient)
            
    if not quotients:
        if areas != 0:
            return False
        else:
            return "empty"
    else:
        return True                

def rectangles_rec_ups(img_name, index_line_pos, index_sign_line_pos):
    # look for rectangles that have information whether it is marked as signed or not in case of having no common signature
    # read image into array
    image_array = cv2.imread('path\\Images\\{}.jpg'.format(img_name))     # may be changed

    # convering image to gray scale
    gray_scale_image = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)

    # image thresholding
    _, img_bin = cv2.threshold(gray_scale_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    img_bin = 255 - img_bin

    # Image.fromarray(img_bin).show()

    # set min width to detect horizontal lines
    line_min_width = 15
    # kernel to detect horizontal lines
    kernal_h = np.ones((1,line_min_width), np.uint8)
    # kernel to detect vertical lines
    kernal_v = np.ones((line_min_width,1), np.uint8)
    # horizontal kernel on the image
    img_bin_h = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, kernal_h)
    # verical kernel on the image
    img_bin_v = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, kernal_v)
    # combining the image
    img_bin_final=img_bin_h|img_bin_v
    # Image.fromarray(img_bin).show()
    final_kernel = np.ones((3,3), np.uint8)
    img_bin_final=cv2.dilate(img_bin_final,final_kernel,iterations=1)
    _, labels, stats,_ = cv2.connectedComponentsWithStats(~img_bin_final, connectivity=8, ltype=cv2.CV_32S)

    quotients = []
    areas = 0
    for x,y,w,h,area in stats[2:]:
        if area >= 100:
            areas += 1
            cv2.rectangle(image_array,(x,y),(x+w,y+h),(255,255,0),2)
        
            area2 = 0
            area3 = 0
            white = np.array([255, 255, 255])
            black = np.array([0, 0, 0])

            for i in range(x, x+w):
                for j in range(y, y+h):
                    # check if box is in the same line with index or index_sign and if it's x position is no further than 1000 pix to avoid catching No boxes
                    if y >= index_line_pos[0] - 50 and y <= index_line_pos[1] + 50 or y >= index_sign_line_pos[0] - 50 and y <= index_sign_line_pos[1] + 50:
                        if x < 1000:
                            if img_bin[j, i].all() != black.all():
                                area2 += 1
                            if img_bin[j, i].all() != white.all():
                                area3 += 1
            quotient = area2/area
            if quotient > 0.2:
                quotients.append(quotient)
            
    if quotients:
        return True                
