import os
import re
import cv2 
import numpy as np
import pytesseract
from pytesseract import Output
from matplotlib import pyplot as plt
from pdf2image import convert_from_path
from PIL import Image
from numpy import *
import datetime
import pandas as pd
from shutil import copy
import shutil
import aspose.words as aw


from src.utils import file_name_func, lines_remover, resizing
from src.ups import ups_pages_loop
from src.everify import everify_pages_loop
from src.exhibit import exhibit_pages_loop

pytesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'      # may be changed

pytesseract.pytesseract.tesseract_cmd = pytesseract_path     # may be changed



# Images source
imgs_dir_short = 'path'
IMGS_DIR = imgs_dir_short + 'Images\\'        # may be changed
IMG_FAIL_DIR = imgs_dir_short + 'Failures\\'      # may be changed
IMG_PROPER_DIR = imgs_dir_short + 'Propers\\'      # may be changed

custom_config = r'--oem 1 --psm 6'      # may be changed
poppler_path = r"C:\poppler-21.11.0\Library\bin"     # may be changed


class PDFRecognizer():
    # class to recognize pdf files and extract data from them
    def __init__(self, pdf_name, row, directory, file_format, df):
        self.pdf_name = pdf_name
        self.row = row
        self.directory = directory
        self.file_format = file_format
        self.df = df
        self.pdf_index = 0       # for dataframe purpose
        self.df = pd.DataFrame(columns=['File Name', 'Document Type', 'Found', 'Not Found', 'Date'])
        self.failures = 0



    date_pattern = '^([1-9]|0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[012])/([0-2][0-9]|((19|20)\d\d))$'  # EU format, slashes /, catches year 2021 and 21 - 7/12/2021 | 07/12/2021 / 7/07/2021 | 7/7/2021 etc
    date_pattern2 = '^([1-9]|0[1-9]|1[012])/([1-9]|0[1-9]|[12][0-9]|3[01])/([0-2][0-9]|((19|20)\d\d))$' # US format, slashes /, catches year 2021 and 21 
    date_pattern3 = '^([1-9]|0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[012])-(19|20)\d\d$'                # EU format, dash -, catches year 2021
    date_pattern4 = '^([1-9]|0[1-9]|1[012])-([1-9]|0[1-9]|[12][0-9]|3[01])-(19|20)\d\d$'                # US format, dash -, catches year 2021
    date_short_eu = '^([1-9]|0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[012])'
    date_short_us = '^([1-9]|0[1-9]|1[012])/(0[1-9]|[12][0-9]|3[01])'
    date_month = '^([1-9]|0[1-9]|[12][0-9]|3[01]),([0-2][0-9]|((19|20)\d\d))$'
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    only_year = '^(19|20)\d\d$'

    date_patterns = [date_short_eu, date_short_us, date_month, months, only_year, date_pattern, date_pattern2, date_pattern3, date_pattern4]
       

    def convert_pdf_to_image(self):
        # convert pdf to image
        if self.file_format == 0:
            pages = convert_from_path(self.directory + '/' + self.pdf_name, poppler_path=poppler_path)
            num = 0
            for page in pages:
                page.save(r"path\Images\{}{}.jpg".format(self.pdf_name, num))       # may be changed
                num += 1
        else:
            copy(self.directory + '/' + self.pdf_name, IMGS_DIR)
            num = 1

        return num

    def pages_loop(self, num, row):
        # loop through every page and look for date and signature with usage of different functions, like words_loop
        global pdf_name

        for k in range(num):   
            file_name = file_name_func(k, self.file_format)
            image = cv2.imread(IMGS_DIR + file_name) 
            if self.file_format == 0:
                if type(image) is np.ndarray:
                    pass
                else:
                    new_name = pdf_name.replace('-', '').replace('–', '').replace('+', '')
                    shutil.copy(self.directory + '/' + pdf_name, self.directory + '/' + new_name)
                    file_name = new_name
                    pages = convert_from_path(self.directory + '/' + file_name, poppler_path=poppler_path)
                    num = 0
                    for page in pages:
                        page.save(r"path\Images\{}{}.jpg".format(file_name, num))       # may be changed
                        num += 1

                    file_name = "{}{}.jpg".format(file_name, k)
                    pdf_name = file_name

            image = lines_remover(file_name)
            # create copy in case of enlarging
            image_copy = image.copy()

            # read image 
            d = pytesseract.image_to_data(image, config=custom_config, output_type=Output.DICT)
           
           # loop through every word 
            too_little, index = self.words_loop(image, d)

            if too_little != 0:
                d = resizing(image_copy)
                too_little, index = self.words_loop(image_copy, d)
            if index != 0:
                break

        self.df.loc[row, ['File Name']] = pdf_name
        start = 0
        if index == 0:
            self.df.loc[row, ['Document Type']] = 'Not Found'
            d = everify_pages_loop(start, num, row, self.pdf_index)
        elif index == 1:
            self.df.loc[row, ['Document Type']] = 'E-Verify'
            d = everify_pages_loop(start, num, row, self.pdf_index)
        elif index == 2:
            self.df.loc[row, ['Document Type']] = 'UPS Onboarding'
            d = ups_pages_loop(start, num, row, self.pdf_index)
        elif index == 3:
            self.df.loc[row, ['Document Type']] = 'Exhibit'
            d = exhibit_pages_loop(start, num, row, self.pdf_index)

        return d
    
    def analyze_documents(self):
        num = self.convert_pdf_to_image()

        d = self.pages_loop(num, self.row)

        # Check if file is signed properly. If so, copy it to Propers folder, else copy it to Failures folder.
        if self.failures != 0:
            copy(self.directory + '/' + pdf_name, IMG_FAIL_DIR)
        else:
            copy(self.directory + '/' + pdf_name, IMG_PROPER_DIR)

        return self.df 

    def file_loop(self, directory):
        new_df = pd.DataFrame(columns=['File Name', 'Document Type', 'Found', 'Not Found', 'Date'])

        row = 0
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if filename.endswith(".pdf"): 
                self.file_format = 0
                new_df = new_df.append(self.analyze_documents(filename, row, directory, self.file_format))
                continue
            elif filename.endswith(".jpg"): 
                self.file_format = 1
                new_df = new_df.append(self.analyze_documents(filename, row, directory, self.file_format))
            elif filename.endswith(".PNG"): 
                self.file_format = 2
                new_df = new_df.append(self.analyze_documents(filename, row, directory, self.file_format))
            elif filename.endswith(".GIF"): 
                self.file_format = 3
                new_df = new_df.append(self.analyze_documents(filename, row, directory, self.file_format))
            elif filename.endswith(".doc") or filename.endswith(".docx"):
                # convert('{}/{}'.format(directory, filename) , '{}/{}.pdf'.format(directory, filename))
                doc = aw.Document('{}/{}'.format(directory, filename))
                doc.save('{}/{}.pdf'.format(directory, filename))
                self.file_format = 0
                filename = filename + '.pdf'
                new_df = new_df.append(self.analyze_documents(filename, row, directory, self.file_format))
            else:
                continue
        current_hour = datetime.datetime.now().strftime('%H_%M_%S')        
        file_path = 'path/Summary_files_uipath_{}.xlsx'.format(current_hour)
        
        new_df.to_excel(file_path, index=False)

        return file_path

analyzer = PDFRecognizer()
analyzer.file_loop("path\\N\\")
