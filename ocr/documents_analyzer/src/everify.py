import re
import cv2
from pytesseract import Output
import pytesseract

from src.utils import file_name_func, lines_remover, resizing
from documents_analyzer.documents_analyzer import pytesseract_path, custom_config

pytesseract.pytesseract.tesseract_cmd = pytesseract_path 

def everify_words_loop(image, date_patterns, d):
    date_short_eu, date_short_us, date_month, months, only_year, date_pattern, date_pattern2, date_pattern3, date_pattern4 = [*date_patterns]
    # loop through every found word and look for date and signature 
    n_boxes = len(d['text'])
    index = 0
    index_not = 0
    too_little = 0
    text_report = 'report'      # text to be found inside file
    text_report_long = 'reportstatus'
    text_complete = 'complete'
    text_employ = 'employment'
    text_employ_long = 'employmentauthorized'
    date = ''
    for i in range(n_boxes):  
        # condition to only pick boxes with a confidence > 30%
        if float(d['conf'][i]) > 30:    
            # looking for report status
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
            # if date is in format Apr 23, 2021
            elif d['text'][i].strip() in months:
                if re.match(date_month, d['text'][i + 1]):
                    date = d['text'][i] + d['text'][i + 1]
                    index = i + 2
                elif re.match(date_month, (d['text'][i + 1] + d['text'][i + 2])):
                    date = d['text'][i] + d['text'][i + 1] + d['text'][i + 2] 
                    index = i + 3
                    
            if re.match(text_report, d['text'][i].lower()):
                new_text = d['text'][i] + d['text'][i+1]
                if re.search(text_report_long, new_text.lower()):
                    if re.search(text_complete, d['text'][i+2].lower()):
                        index = i + 2    
                    else:
                        index_not = i + 2
                        
            elif re.match(text_employ, d['text'][i].lower()):
                new_text = d['text'][i] + d['text'][i+1]
                if re.search(text_employ_long, new_text.lower()):                  
                    if d['text'][i+2].lower() != 'result' and d['text'][i+2].lower() != 'result.':
                        index = i + 2                   
                    else:
                        index_not = i + 2                           
                else:
                    index_not = i + 2
                    
            elif re.search('verify', d['text'][i].lower()):
                if re.match(text_complete, d['text'][i+1].lower()):
                    if d['text'][i+1].lower() != 'not':
                        index = i + 2                           
                    else:
                        index_not = i + 2              
                else:
                    try:
                        if re.search(text_complete, d['text'][i+2].lower()):
                            if d['text'][i+1].lower() != 'not' and d['text'][i+2].lower() != 'incomplete':
                                index = i + 2
                            else:
                                index_not = i + 2                            
                    except:
                        pass

        elif float(d['conf'][i]) > 10 and float(d['conf'][i]) <= 30: 
            if re.match(text_report, d['text'][i].lower()):
                new_text = d['text'][i] + d['text'][i+1]
                if re.search(text_report_long, new_text.lower()):
                    too_little += 1
            elif re.match(text_employ, d['text'][i].lower()):
                new_text = d['text'][i] + d['text'][i+1]
                if re.search(text_employ_long, new_text.lower()):
                    too_little += 1

    return too_little, index, image, index_not, date

def everify_pages_loop(df, failures, start, num, row, pdf_index, pdf_name, file_format):
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
        # remove lines from image
        image = lines_remover(file_name)
        # create copy in case of enlarging
        image_copy = image.copy()       
        # read image 
        d = pytesseract.image_to_data(image, config=custom_config, output_type=Output.DICT)
        # loop through every word
        too_little, index, image, index_not, date = everify_words_loop(image, d)
        
        # resize image if it's too little
        if too_little != 0:
            d = resizing(image_copy)
            too_little, index, image, index_not, date = everify_words_loop(image_copy, d)
        
        # if date exists, look for signature in 2 ways: one step to the right from index or one step to the right from 'Signature'
        if index > 1:
            signed += 1 
    df.loc[row, ['File Name']] = pdf_name
    if signed > 0:
        df.loc[row, ['Found']] = 'Signed'
        df.loc[row, ['Date']] = date 
    elif index_not != 0:
        df.loc[row, ['Not Found']] = 'Not signed'

        failures += 1   # to copy not signed file to a different directory
    row += 1   
        
    return d