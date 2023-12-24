import cv2
from pytesseract import Output
import pytesseract
import re

from src.ups import ups_signature
from src.utils import lines_remover, resizing, shrinking, rect_mini, file_name_func
from documents_analyzer.documents_analyzer import pytesseract_path, custom_config

pytesseract.pytesseract.tesseract_cmd = pytesseract_path  

def exhibit_words_loop(row, image, d, date_patterns):
    # loop through every found word and look for date and signature
    date_short_eu, date_short_us, date_month, months, only_year, date_pattern, date_pattern2, date_pattern3, date_pattern4 = [*date_patterns]
    text = 'signature'      # text to be found inside file
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
    index_sign2 = 0
    index_printed = 0
    too_little = 0
    ups_index = 0
    text_ups = 'UPS'
    text_ups_long = 'UPS Pre-Employment'
    exhibit_letter = ''
    box_index = 0

    for i in range(n_boxes):
        # look for letter on exhibit page
        if re.search('exhibit', d['text'][i].lower()):
            if i < 5:
                exhibit_letter = d['text'][i + 1].replace('12', '').replace('1', '')
                if exhibit_letter == '4':
                    exhibit_letter = 'A'
                
        if re.match(text_ups, d['text'][i]):
            try:
                if re.match(text_ups_long, (d['text'][i] + ' ' + d['text'][i+1])):   
                    if ups_signature(d, i) == True:
                        ups_index = 1
                    elif ups_signature(d, i) == False:
                        ups_index = 2
                    else:
                        ups_index = 3
                    break
                else:
                    pass
            except:
                pass
        # condition to only pick boxes with a confidence > 30%
        if float(d['conf'][i]) > 30:
            if re.match(date_pattern, d['text'][i]) or re.match(date_pattern2, d['text'][i]) or re.match(date_pattern3, d['text'][i]) or re.match(date_pattern4, d['text'][i]):
                (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                image = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)    # red
                if i > 5:
                    index = i + 1
                    date = d['text'][i]   

            elif re.search(only_year, d['text'][i]):
                new_date = d['text'][i - 2] + d['text'][i - 1] + d['text'][i] 
                new_date2 = d['text'][i - 4] + d['text'][i - 3] + d['text'][i - 2] + d['text'][i - 1] + d['text'][i] 
                
                if i > 5:
                    if re.match(date_pattern, new_date) or re.match(date_pattern2, new_date) or re.match(date_pattern3, new_date) or re.match(date_pattern4, new_date):
                        date = new_date
                        index = i + 1
                        image = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)    # red
                    elif re.match(date_pattern, new_date2) or re.match(date_pattern2, new_date2) or re.match(date_pattern3, new_date2) or re.match(date_pattern4, new_date2):
                        date = new_date2
                        index = i + 1
                        image = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)    # red
            else:
                (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                image = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)    # green

            # looking for signature
            if re.search(text, d['text'][i].lower()):
                (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                image = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)    # red
                if index_sign == 0:
                    index_sign = i + 1
                else:
                    index_sign2 = i + 1

            if re.search('check', d['text'][i].lower()):
                check_text = d['text'][i].lower() + d['text'][i + 1].lower() + d['text'][i + 2].lower()
                if check_text == 'checktosign':
                    box_index = 1
        elif float(d['conf'][i]) > 10 and float(d['conf'][i]) <= 30: 
            if re.match(date_pattern, d['text'][i]) or re.match(date_pattern2, d['text'][i]) or re.match(date_pattern3, d['text'][i]) or re.match(date_pattern4, d['text'][i]):
                too_little += 1
        else:
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            image = cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)    # blue
        
        # look for Printed Name with conf > 30 and if found then set variable 
        if re.match('Printed', d['text'][i]) and re.match('Name', d['text'][i + 1]):
            if float(d['conf'][i]) > 30 and float(d['conf'][i + 1]) > 30:
                index_printed = i - 1
        # printing if found, if not look for separated date
        if index == 0 and i > 5:
            if re.match(date_pattern, d['text'][i]) or re.match(date_pattern2, d['text'][i]) or re.match(date_pattern3, d['text'][i]) or re.match(date_pattern4, d['text'][i]):
                pass
            elif re.match(date_short_eu, d['text'][i]) or re.match(date_short_us, d['text'][i]):
                try:
                    new_date = d['text'][i] + d['text'][i + 1] + d['text'][i + 2]
                    if re.match(date_pattern, new_date) or re.match(date_pattern2, new_date) or re.match(date_pattern3, new_date) or re.match(date_pattern4, new_date):
                        if re.match('^([0-2][0-9]|((19|20)\d\d))', d['text'][i + 2]):
                            index = i + 3
                            date = new_date
                except:
                    pass
        # if date is in format Apr 23, 2021
        if d['text'][i].strip() in months:
            if re.match(date_month, d['text'][i + 1]):
                date = d['text'][i] + d['text'][i + 1]
                index = i + 2
            elif re.match(date_month, (d['text'][i + 1] + d['text'][i + 2])):
                date = d['text'][i] + d['text'][i + 1] + d['text'][i + 2] 
                index = i + 3
    return too_little, index, index_sign, image, ups_index, index_printed, date, exhibit_letter, box_index, index_sign2

def exhibit_pages_loop(df, start, num, row, pdf_index, pdf_name, failures, file_format):
    # loop through every page and look for date and signature with usage of different functions, like words_loop
    pdf_index = pdf_index
    exhibit_pages = []
    exhibit_dates = []
    exhibit_pages_signed = []
    exhibit_pages_notsigned = []
    big_signed = 0
    # nonlocal failures   # to copy not signed file to a different directory    
    for k in range(start, num):   
        if k == 0:
            if pdf_name.endswith(".pdf"):   
                file_name = file_name_func(k, file_format)
            else:
                file_name = pdf_name
        else:
            file_name = file_name_func(k, file_format)       
        # image = cv2.imread(IMGS_DIR + file_name) 
        # remove lines from image
        image = lines_remover(file_name)
        # create copy in case of enlarging
        image_copy = image.copy() 
        image_copy2 = image.copy()       
        # read image 
        d = pytesseract.image_to_data(image, config=custom_config, output_type=Output.DICT)

        # loop through every word
        too_little, index, index_sign, image, ups_index, index_printed, date, exhibit_letter, box_index, index_sign2 = exhibit_words_loop(image, d)
        # resize image if it's too little
        if too_little != 0 or date == '':
            d = resizing(image_copy)
            too_little, index, index_sign, image, ups_index, index_printed, date, exhibit_letter, box_index, index_sign2 = exhibit_words_loop(image_copy, d)
            if date == '':
                d = shrinking(image_copy2)
                too_little, index, index_sign, image, ups_index, index_printed, date, exhibit_letter, box_index, index_sign2 = exhibit_words_loop(image_copy, d)
            
        n_boxes = len(d['text'])
        signature = ''
        signed = 0

        # don't add any text except signature yes/no
        if index > 1:
            try:
                if index_sign < n_boxes:
                    
                    if index < n_boxes:
                        if index_printed != 0:
                            if len(d['text'][index]) > 0 or len(d['text'][index_sign]) > 0 or len(d['text'][index_printed]) > 0:
                                signature = 'Yes'
                            elif d['text'][index + 1] == "|":
                                if len(d['text'][index + 2]) > 1:
                                    signature = 'Yes'
                            elif index < index_printed:
                                if len(d['text'][index + 1]) > 1 and d['text'][index + 1].lower() != 'printed':
                                    signature = 'Yes'
                        else:
                            if len(d['text'][index]) > 0 or len(d['text'][index_sign]) > 0 or len(d['text'][index_sign + 1]) > 0 and d['text'][index_sign + 1].lower() != 'supplier':
                                signature = 'Yes'
                            elif d['text'][index + 1] == "|":
                                if len(d['text'][index + 2]) > 1:
                                    signature = 'Yes'   
                    else:    
                        if index_printed != 0:
                            if len(d['text'][index_sign]) > 0 or len(d['text'][index_printed]) > 0:
                                signature = 'Yes'
                            elif d['text'][index + 1] == "|":
                                if len(d['text'][index + 2]) > 1:
                                    signature = 'Yes'   
                        else:
                            # provide d['text'][index_sign + 1].lower() != 'supplier' to avoid empty lines like in UPS Daniel Pomerantz files, where in+1 is empty 
                            # and in+2 is electronically, but if it's supplier, than line is empty or not found.
                            if len(d['text'][index_sign]) > 0 or len(d['text'][index_sign + 1]) > 0 and d['text'][index_sign + 1].lower() != 'supplier':
                                signature = 'Yes'
                            elif d['text'][index + 1] == "|":
                                if len(d['text'][index + 2]) > 1:
                                    signature = 'Yes'            
                else:
                    if index < n_boxes:
                        if index_printed != 0:
                            if len(d['text'][index]) > 0 or len(d['text'][index_printed]) > 0:
                                signature = 'Yes'
                            elif d['text'][index + 1] == "|":
                                if len(d['text'][index + 2]) > 1:
                                    signature = 'Yes'
                            elif index < index_printed:
                                if len(d['text'][index + 1]) > 1 and d['text'][index + 1].lower() != 'printed':
                                    signature = 'Yes'
                        else:
                            if len(d['text'][index]) > 0:
                                signature = 'Yes'
                            elif d['text'][index + 1] == "|":
                                if len(d['text'][index + 2]) > 1:
                                    signature = 'Yes'
                    else:    
                        if index_printed != 0:
                            if len(d['text'][index_printed]) > 0:
                                signature = 'Yes'
                        elif d['text'][index + 1] == "|":
                            if len(d['text'][index + 2]) > 1:
                                signature = 'Yes'    
            except:
                try:
                    signed = rect_mini(pdf_name, k)
                    big_signed = signed
                except:    
                    pass
        
        elif index_sign != 0:
            if k == (num-1):
                # check if last page is signed without date
                if (index_sign + 1) < n_boxes and (index_sign2 + 1) < n_boxes:
                    if len(d['text'][index_sign]) > 0 and d['text'][index_sign].lower() != 'supplier' or len(d['text'][index_sign + 1]) > 0 and d['text'][index_sign + 1].lower() != 'supplier':
                        signed = 1
                        big_signed = signed
                    elif len(d['text'][index_sign2]) > 0 and d['text'][index_sign2].lower() != 'date:' or len(d['text'][index_sign2 + 1]) > 0 and d['text'][index_sign2 + 1].lower() != 'date:':
                        signed = 1
                        big_signed = signed
                    else:
                        signed = rect_mini(pdf_name, k)
                        big_signed = signed   
                else:
                    signed = rect_mini(pdf_name, k)
                    big_signed = signed 
            else:
                signed = rect_mini(pdf_name, k)
                big_signed = signed
        elif ups_index != 0:
            if ups_index == 1:
                signature = 'Yes'
        try:
            if d['text'][index - 4].lower() == 'printed':
                if len(d['text'][index - 8]) > 0 and d['text'][index - 8].lower() != '' and d['text'][index - 8].lower() != 'signature':
                    signature = 'Yes'
        except:
            pass

        if index_printed != 0 and signed == 0:
            if d['text'][index_printed-1] == '|' and len(d['text'][index_printed-2]):
                if d['text'][index_printed-3] == date or d['text'][index_printed-4] == date or d['text'][index_printed-5] == date:
                    signed = 1
                    signature = 'Yes'
                    big_signed = signed
        # check if there is a box to be checked
        if box_index != 0 and signed == 0:
            signed = rect_mini(pdf_name, k)
            big_signed = signed
        # check if document is signed or not
        # add letters of signed documents (Exhibit 12A, 12B...)
        if len(exhibit_letter) > 0:
            exhibit_pages.append(exhibit_letter)
        # check if signed by date
        if len(date) > 0 and signature == 'Yes':
            if len(exhibit_dates) < len(exhibit_pages):
                exhibit_dates.append(date)
                # add document as completed
                if len(exhibit_dates) == len(exhibit_pages):
                    if exhibit_pages[-1] not in exhibit_pages_signed:
                        exhibit_pages_signed.append(exhibit_pages[-1])
        if signed == 1 and len(exhibit_dates) == 3 and len(exhibit_pages) == 4:
            exhibit_pages_signed.append(exhibit_pages[-1])
            exhibit_dates.append(exhibit_dates[0])
        # add document as not completed
        if len(exhibit_pages) > (len(exhibit_dates) + 1) :
            if exhibit_pages[-2] not in exhibit_pages_notsigned:
                exhibit_pages_notsigned.append(exhibit_pages[-2])
                exhibit_pages.pop(-2)
        if signed == 0 and index != 0 and index_sign != 0 and index_sign2 != 0:
            if d['text'][index-2].lower() == 'date:' or d['text'][index-2].lower() == 'dare':
                if len(d['text'][index_sign]) > 0 or len(d['text'][index_sign2]) > 0:
                    signed = 1
                    big_signed = signed
            elif index_printed > index and len(d['text'][index_printed - 1]) > 0 and d['text'][index_printed - 1] != date:
                signed = 1
                big_signed = signed
        if k == (num - 1):
            if len(exhibit_pages) == 0 and big_signed > 0:
                signed = big_signed
            if len(exhibit_pages) > len(exhibit_dates) :
                if exhibit_pages[-1] not in exhibit_pages_notsigned:
                    exhibit_pages_notsigned.append(exhibit_pages[-1])
            df.loc[row, ['File Name']] = pdf_name

            if len(exhibit_pages_signed) > 0 or len(exhibit_pages_notsigned) > 0:
                if len(exhibit_pages_signed) > 0:
                    df.loc[row, ['Found']] = str(sorted(exhibit_pages_signed)).replace('[', '').replace(']', '')
                if len(exhibit_pages_notsigned) > 0:
                    df.loc[row, ['Not Found']] = str(sorted(exhibit_pages_notsigned)).replace('[', '').replace(']', '')
                    
            elif signed != 0:
                df.loc[row, ['Found']] = 'Signed'
            else:
                if signature == 'Yes':
                    df.loc[row, ['Found']] = 'Signed'
                else:
                    df.loc[row, ['Not Found']] = 'Not signed'
            if len(exhibit_dates) > 0:
                df.loc[row, ['Date']] = exhibit_dates[0]
            elif len(date) > 0:
                df.loc[row, ['Date']] = date

            row += 1  

    if len(exhibit_pages_notsigned) > 0:
        failures += 1   # to copy not signed file to a different directory    
    return d