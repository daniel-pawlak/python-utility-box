import os
import re
import cv2 
# import numpy as np
import pytesseract
from pytesseract import Output
from matplotlib import pyplot as plt
from pdf2image import convert_from_path
# from PIL import Image
from numpy import *
import datetime
import pandas as pd
# from shutil import copy
# import shutil
# import aspose.words as aw
import time
import functools
import traceback
# links
# https://github.com/oschwartz10612/poppler-windows/releases/

def timer(func):
    """Timer checks how much time does it take to run the script"""
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        
        start_time = time.perf_counter()

        try:
            value = func(*args, **kwargs)
            end_time = time.perf_counter()
            run_time = end_time - start_time
            end_hour = datetime.datetime.now().strftime('%H:%M:%S')
            print(f"Finished {func.__name__!r} in {run_time:.4f} secs at {end_hour}. It took {time.strftime('%H:%M:%S', time.gmtime(run_time))}.")
            
            return value
        except (RuntimeError, TypeError, NameError, OSError, BaseException, ValueError) as err:
            end_time = time.perf_counter()
            run_time = end_time - start_time
            end_hour = datetime.datetime.now().strftime('%H:%M:%S')
            print(f"\n\nATTENZIONE\n\n{func.__name__} failed after {run_time:.4f} secs at {end_hour}. It took {time.strftime('%H:%M:%S', time.gmtime(run_time))}.\n\nUnexpected {err=}, {type(err)=}\n\n")
            # print(traceback.format_exc())

    return wrapper_timer

def display_image(image):
    """display image"""
    b,g,r = cv2.split(image)
    rgb_img = cv2.merge([r,g,b])
    plt.figure(figsize=(16,12))
    plt.imshow(rgb_img)
    plt.title('SAMPLE DOCUMENT WITH WORD LEVEL BOXES')
    plt.show()

def words_loop(image, d, df, row, filename):
    """Loop through every found word and look for necessary information"""

    # date pattern EU format, dots ., catches years 2000s and 1900s - 1.12.2021 | 07.12.2021 | 7.07.2021 
    date_pattern = '^([1-9]|0[1-9]|[12][0-9]|3[01]).(0[1-9]|1[012]).((19|20)\d\d)$' 

    # list of key words for every information 
    text_op1 = 'eksploatujacy'  
    text_op2 = 'eksploatujący'      
    
    text_dev1 = "urządzenie"
    text_dev2 = "urzadzenie"

    text_evidence = "ewidencyjny"
    text_factory = "fabryczny"
    text_construct = "budowy"
    text_type = "typ"

    text_points1 = "ładowania"
    text_points2 = "ladowania"
    text_points3 = "tadowania"

    text_result = "wynik"
    text_result_cd = "badania"

    text_inspection = "wykonano"
    text_inspection_cd = "badanie"

    text_faults1 = "niezgodności"
    text_faults2 = "niezgodnosci"

    # index for getting device information
    dev_index = 0
    al_index = 0

    # index for getting inspection information
    ins_index = 0
    res_index = 0

    # index for getting faults text
    faults_index = 0
    faults_index2 = 0

    # index for getting just type of charger
    type_index = 0
    plz_index = 0

    # charger's address
    address_index = 0
    year_index = 0

    # number of recognized boxes
    n_boxes = len(d['text'])

    date = ''
    operator = '' 
    device = ''
    evidence = ''
    factory = ''
    construction = ''
    type = ''
    points = ''
    result = ''
    inspection = ''
    faults = ''
    address = ''

    for i in range(n_boxes):
        # date
        if re.match(date_pattern, d['text'][i]):
            if i < 50:
                date = d['text'][i]   

        # operator
        if re.search(text_op1, d['text'][i].lower().replace(":", "")):
            operator = d['text'][i + 1]
        elif re.search(text_op2, d['text'][i].lower().replace(":", "")):
            operator = d['text'][i + 1]

        # device
        if i < 50:                
            if re.search(text_dev1, d['text'][i].lower().replace(":", "")):
                device = d['text'][i + 1 : i + 11]
            elif re.search(text_dev2, d['text'][i].lower().replace(":", "")):
                device = d['text'][i + 1 : i + 11]
            dev_index = i + 1
        
        # index for extracting device name only
        if re.search("al.", d['text'][i].lower()):
            al_index = i

        # evidence
        if re.search(text_evidence, d['text'][i].lower().replace(":", "")):
            evidence = d['text'][i + 1].replace("£", "E")

        # factory
        if re.search(text_factory, d['text'][i].lower().replace(":", "")):
            factory = d['text'][i + 1].replace("$", "S")
            address_index = i + 2
            address = d['text'][i + 2:]

        # construction
        if re.search(text_construct, d['text'][i].lower().replace(":", "")):
            construction = d['text'][i + 1]
            year_index = i - 1
        
        # type
        if re.search(text_type, d['text'][i].lower().replace(":", "")):
            type = d['text'][i + 1:]
            type_index = i + 1

        # index for extracting only type
        if re.search('81-451', d['text'][i].lower().replace(":", "")) and i > type_index and (i - type_index) < 9:
            plz_index = i
        elif re.search('AL.', d['text'][i].lower().replace(":", "")) and i > type_index and (i - type_index) < 9:
            plz_index = i
        elif re.search('ALEJA', d['text'][i].lower().replace(":", "")) and i > type_index and (i - type_index) < 9:
            plz_index = i
        elif re.search('AL.ZWYCIESTWA', d['text'][i].lower().replace(":", "")) and i > type_index and (i - type_index) < 9:
            plz_index = i

        # number charging points
        if re.search('liczba', d['text'][i].lower().replace(":", "")):
            if re.search(text_points1, d['text'][i + 2].lower().replace(":", "")):
                points = d['text'][i + 3]
            elif re.search(text_points2, d['text'][i + 2].lower().replace(":", "")):
                points = d['text'][i + 3]
            elif re.search(text_points3, d['text'][i + 2].lower().replace(":", "")):
                points = d['text'][i + 3]              

        # result
        if re.search(text_result, d['text'][i].lower().replace(":", "")) and re.search(text_result_cd, d['text'][i + 1].lower().replace(":", "")):
            result = d['text'][i + 2]
            res_index = i

        # inspection
        if re.search(text_inspection, d['text'][i].lower().replace(":", "")) and re.search(text_inspection_cd, d['text'][i + 1].lower().replace(":", "")):            
            inspection = d['text'][i + 2 : i + 8]
            ins_index = i + 2

        # faults
        if re.search(text_faults1, d['text'][i].lower().replace(":", "")):
            faults = d['text'][i + 1:]
            faults_index = i + 1
        elif re.search(text_faults2, d['text'][i].lower().replace(":", "")):
            faults = d['text'][i + 1:]
            faults_index = i + 1

        # index for extracting faults only
        if re.search("§13.1", d['text'][i].lower()):
            if i > faults_index:
                faults_index2 = i

    # piece of code to extract only the necessary information about the device
    dev_index = al_index - dev_index
    device = device[:dev_index]

    to_del = ['POLSKA', 'SP.', 'Z', '0.0.', 'O.O.', '', 'SP.zZ', 'SPOLKA', 'OGRANICZONA', 'AL.ZWYCIESTWA', 'ALEJA', 'ODPOWIEDZIALNOSCIA,', \
              "EV", "Z.0.0.", "ZOGRANICZONA", "ODPOWIEDZIALNOSCIA"]
    
    for i in to_del:
        try:
            device.remove(i)
        except:
            pass

    device = " ".join(device).strip()

    device = device.replace("OGOLNODOSTEFNA", "OGÓLNODOSTĘPNA").replace("STACA", "STACJA").replace("STACIA", "STACJA"). \
                    replace("tADOWANIA", "ŁADOWANIA").replace("  ", " ").replace("POZOSTAtE", "POZOSTAŁE"). \
                    replace("LADOWANIA", "ŁADOWANIA").replace("OGOLNODOSTEPNA", "OGÓLNODOSTĘPNA")
    
    # piece of code to extract type of inspection
    ins_index = res_index - ins_index
    inspection = inspection[:ins_index]
    inspection = " ".join(inspection).replace("wstepne", "wstępne").replace("|", "").strip()

    # piece of code to extract faults
    faults_index = faults_index2 - faults_index - 2
    faults = faults[:faults_index]
    faults = " ".join(faults).strip()

    # piece of code to extract type
    type_index = plz_index - type_index
    type = type[:type_index]

    # piece of code to extract charger's place
    year_index = year_index - address_index
    address = address[:year_index]
    address = " ".join(address).strip()

    # if type is too long, then shorten it
    if len(type) > 7:
        al_ind = 0

        if 'AL.' in type and type.index("AL.") < 10:
            al_ind = type.index("AL.")
        elif 'ALEJA' in type and type.index('ALEJA') < 10:
            al_ind = type.index('ALEJA')
        elif 'AL.ZWYCIESTWA' in type and type.index('AL.ZWYCIESTWA') < 10:
            al_ind = type.index('AL.ZWYCIESTWA')

        type = type[:al_ind]

    type = " ".join(type).strip()

    df.loc[row, 'FileName'] = filename
    df.loc[row, 'Date'] = date
    df.loc[row, 'Operator'] = operator
    df.loc[row, 'Device'] = device
    df.loc[row, 'Device Type'] = type
    df.loc[row, 'Evidence Number'] = evidence
    df.loc[row, 'Factory Number'] = factory
    df.loc[row, 'Year of Construction'] = construction
    df.loc[row, 'Number of Charging Points'] = points
    df.loc[row, 'Address'] = address
    df.loc[row, 'Inspection Type'] = inspection
    df.loc[row, 'Inspection Result'] = result
    df.loc[row, 'Comments'] = faults
    
    return df

def pdf_recognizer(directory, filename, row, df, source):
    """Function to convert pdf to image and then analyze words in order to find needed information"""
    # path to tesseract
    pytesseract.pytesseract.tesseract_cmd = 'path\to/Tesseract-OCR/tesseract.exe'      # may be changed

    # tesseract's config
    custom_config = r'--oem 1 --psm 6'

    # Images source
    IMGS_DIR = directory + 'Images\\'        # may be changed
    PDF_DIR = directory + source   

    # path to poppler
    poppler_path = r"path\to\poppler-23.01.0\Library\bin" 
    
    # convert pdf to images
    pages = convert_from_path(PDF_DIR + "/" + filename, poppler_path=poppler_path)

    for page in pages:
        file_name = "{}.jpg".format(filename)
        page.save(IMGS_DIR + file_name)
    
    # read image
    image = cv2.imread(IMGS_DIR + file_name) 
 
    # display_image(image)

    # read image 
    d = pytesseract.image_to_data(image, config=custom_config, output_type=Output.DICT)
    
    # find all the needed information and place them in dataframe
    df = words_loop(image, d, df, row, filename)

    return df

@timer 
def directory_recognizer(directory, excel_name, source):
    """Function to analyze whole directory of PDFs"""
    df = pd.DataFrame(columns=['Date', 'Operator', 'Device', 'Device Type', 'Evidence Number', 'Factory Number', 'Year of Construction', 
                               'Number of Charging Points', 'Address', 'Inspection Type', 'Inspection Result', 'Comments'], index=range(0))
    row = 0
    count = 1
    
    # loop through every file inside given folder
    for file in os.listdir(directory + source):        
        filename = os.fsdecode(file)
        print(count, filename)

        # start analyzing document
        df = pdf_recognizer(directory, filename, row, df, source)

        row += 1
        count += 1

    # save found information in excel file
    try:
        df.to_excel(excel_name, index=False)
    except:
        input("Close Excel File and Press Enter to continue...")
        df.to_excel(excel_name, index=False)

# general directory for analyzed files  
directory = 'path/to/your/directory'

# run script to analyze directory with documents
# give path to general directory, name of resulted excel file and name of folder with PDFs
directory_recognizer(directory, "your_excel_name.xlsx", "folder_with_pdfs")