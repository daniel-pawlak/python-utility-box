# import libraries
import os
import re
import cv2 
import pytesseract
from pytesseract import Output
from pdf2image import convert_from_path
from numpy import *
import datetime
import pandas as pd
import time
import functools

from suppliers import *
from modules import *

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

def invoice_type(d):
    """
    Function which analyses first page of the document to find service deliverer, then returns number which is assigned to that company.
    """
    # key words
    type1_1, type1_2 = "plus", "energia"

    type4_1, type4_2 = "enea", "operator"

    type6_1, type6_2, type6_3 = "energa", "-", "operator" 

    type11_1, type11_2, type11_3 = "energa", "-", "obr" 

    type25_1, type25_2, type25_3 = "pge", "dystrybucja", "sp"

    type26_1, type26_2 = "polenergia", "sprzed"  

    n_boxes = len(d['text'])
    # print(d['text'])

    # loop through every word
    for i in range(n_boxes):
        if i < 500:
            # Plus Energia
            if re.match(type1_1, d['text'][i].lower()) and re.match(type1_2, d['text'][i + 1].lower()):
                return 1, "Plus Energia"
            
            # Enea Operator
            if re.match(type4_1, d['text'][i].lower()) and re.match(type4_2, d['text'][i + 1].lower()):
                return 4, "Enea Operator"
            
            # Energa Operator
            if re.match(type6_1, d['text'][i].lower()) and re.match(type6_2, d['text'][i + 1].lower()) and re.match(type6_3, d['text'][i + 2].lower()):
                return 6, "Energa Operator"
  
            # Energa Obrót
            if re.match(type11_1, d['text'][i].lower()) and re.match(type11_2, d['text'][i + 1].lower()) and re.match(type11_3, d['text'][i + 2].lower()):
                return 11, "Energa Obrót"
            
            # PGE
            if re.match(type25_1, d['text'][i].lower()) and re.match(type25_2, d['text'][i + 1].lower()) and re.search(type25_3, d['text'][i + 2].lower()):
                return 25, "PGE"
            
            # Polenergia Sprzedaż
            if re.match(type26_1, d['text'][i].lower()) and re.search(type26_2, d['text'][i + 1].lower()):
                return 26, "Polenergia Sprzedaż"

    return 0, "Nie znaleziono"

def invoice_recognizer(directory, filename, df, source):
    """
    Function to convert pdf to image and then analyze words in order to find needed information from invoices
    """
    # path to tesseract
    pytesseract.pytesseract.tesseract_cmd = 'C:/Users/DanielPawlak/AppData/Local/Programs/Tesseract-OCR/tesseract.exe'      # may be changed

    # tesseract's config
    custom_config = r'--oem 1 --psm 6'

    # Images source
    IMGS_DIR = directory + 'Images\\'        # may be changed
    PDF_DIR = directory + source   

    # path to poppler
    poppler_path = r"path\to\poppler-23.01.0\Library\bin" 
    
    # convert pdf to images
    pages = convert_from_path(PDF_DIR + "/" + filename, poppler_path=poppler_path)

    num = 0
    for page in pages:
        file_name = "{}{}.jpg".format(filename, num)
        if num == 0:
            first_page = file_name
        page.save(IMGS_DIR + file_name)
        num += 1

    # read image
    image_first_page = cv2.imread(IMGS_DIR + first_page) 
 
    # display_image(image)

    # read image 
    d_first_page = pytesseract.image_to_data(image_first_page, config=custom_config, output_type=Output.DICT)


    inv_type, name = invoice_type(d_first_page)
    # print(inv_type)

    if inv_type != 0:
        df = pages_loop(inv_type, pages, IMGS_DIR, filename, custom_config, name)

    return df, inv_type

def ppe_counter(d):
    """
    This function counts how many PPE numbers are visible on invoice to get the information for every single PPE number
    """
    n_boxes = len(d['text'])
    ppe = 0
    word_1 = "poboru"
    word_2 = "poberu"
    for i in range(n_boxes):
        if re.match("PPE", d['text'][i].replace(":", "")) and (re.match('^[0-9]{2}', d['text'][i + 1]) or re.match('^PE', d['text'][i + 1])):
            print(d['text'][i], d['text'][i + 1])
            ppe += 1
        elif (re.match("punktu", d['text'][i]) and (re.match(word_1, d['text'][i + 1].replace(":", "")) or re.match(word_2, d['text'][i + 1].replace(":", "")))) and (re.match('^PLZ', d['text'][i + 2]) or re.match('^[0-9]{2}', d['text'][i + 2]) or re.match('^§[0-9]{2}', d['text'][i + 2]) or re.match('^5§[0-9]{2}', d['text'][i + 2])):
            print(d['text'][i], d['text'][i + 2])
            ppe += 1
            
    return ppe

def ppe_counter_polenergia(d):
    """
    This function counts how many PPE numbers are visible on invoice to get the information for every single PPE number in Polenergia invoices
    """
    n_boxes = len(d['text'])
    ppe = 0

    for i in range(n_boxes):
        if re.match('^PL\w?\w?\w?\w?\w?\w?[0-9]{2}', d['text'][i]) or re.match('^PL_\w?\w?\w?\w?_', d['text'][i]) or re.match('^GL\w?[0-9]{2}', d['text'][i]) or re.match('^590[0-9]{2}', d['text'][i]) or re.match('^480[0-9]{2}', d['text'][i]) or re.match('^§90[0-9]{2}', d['text'][i]):
            ppe += 1
        elif re.match("^PL$", d['text'][i]) and re.search("^ZE", d['text'][i + 1]):
            ppe += 1
    return ppe

def pages_loop(inv_type, pages, IMGS_DIR, filename, custom_config, name):
    """
    Function to loop analyze all the pages of the document and export information to dataframe
    """
    df_row = pd.DataFrame(columns=["Nazwa dostawcy", "Nazwa pliku", "Nr Faktury", "Data (okres)", "Data wystawienia", "NIP", "Netto RAZEM", "Brutto RAZEM",
                          	"Termin płatności",	"Nr konta",	"Liczba dni na płatność", "Moc umowna", "Taryfa", "Sm", "Nota odsetkowa", "PPE", "Iloraz kwot", "UWAGA"], index=range(1))

    
    # list of distributors which provide more than one calculation on the invoice
    ppe_types = [6, 11, 26]

    # loop through every page of the file
    if inv_type not in ppe_types:
        for num in range(len(pages)):
            file = IMGS_DIR + "{}{}.jpg".format(filename, num)

            # image = cv2.imread(file) 
            # remove lines from the image
            image = lines_remover(file)

            # d = pytesseract.image_to_data(image, config=custom_config, output_type=Output.DICT)
            # make the image bigger so it's more readable for engine
            d = resizing(image, custom_config)

            if inv_type == 1:
                df_row = plus_energia(d, num, df_row)
            elif inv_type == 4:
                df_row = enea(d, num, df_row)
            elif inv_type == 25:
                df_row = pge(d, num, df_row) 
    else:
        # loop through files with many PPE
        print("\nChecking number of PPE on invoice...\n")
        number_of_ppe = 0

        for num in range(len(pages)):
            file = IMGS_DIR + "{}{}.jpg".format(filename, num)

            image = lines_remover(file)
            # image = cv2.imread(file)

            d = resizing(image, custom_config)    

            if inv_type == 26:
                number_of_ppe += ppe_counter_polenergia(d)
            else:
                number_of_ppe += ppe_counter(d)

        # create empty df with new length
        df_row = pd.DataFrame(columns=["Nazwa dostawcy", "Nazwa pliku", "Nr Faktury", "Data (okres)", "Data wystawienia", "NIP", "Netto RAZEM", "Brutto RAZEM",
                          	"Termin płatności",	"Nr konta",	"Liczba dni na płatność", "Moc umowna", "Taryfa", "Sm", "Nota odsetkowa", "PPE", "Iloraz kwot", "UWAGA"], index=range(number_of_ppe))
        
        ppe_num, period_num, single_amounts, tariff_num, power_num, netto_num, brutto_num = 0, 0, 0, 0, 0, 0, 0

        print(f"\n number_of_ppe {number_of_ppe} \n")

        for num in range(len(pages)):
            file = IMGS_DIR + "{}{}.jpg".format(filename, num)

            image = lines_remover(file)

            d = resizing(image, custom_config)    

            if inv_type == 6:
                df_row, ppe_num, period_num, single_amounts, tariff_num, power_num, netto_num, brutto_num = energa_operator(number_of_ppe, d, num, df_row, ppe_num, period_num, single_amounts, tariff_num, power_num, netto_num, brutto_num)

            elif inv_type == 11:
                df_row, ppe_num, period_num, single_amounts, tariff_num, power_num, netto_num, brutto_num = energa_obrot(number_of_ppe, d, num, df_row, ppe_num, period_num, single_amounts, tariff_num, power_num, netto_num, brutto_num)

            elif inv_type == 26:
                df_row, ppe_num, period_num, single_amounts, tariff_num, power_num, netto_num, brutto_num = polenergia_sprzedaz(number_of_ppe, d, num, df_row, ppe_num, period_num, single_amounts, tariff_num, power_num, netto_num, brutto_num)

        if inv_type != 26:
            df_row = df_row[:number_of_ppe]

    df_row.loc[df_row["Nazwa dostawcy"].isnull(), "Nazwa dostawcy"] = name
    df_row.loc[df_row["Nazwa pliku"].isnull(), "Nazwa pliku"] = filename
    
    # correct money data
    df_row = money_manipulation(df_row)

    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified too
    #     print(df_row)       

    return df_row

@timer 
def directory_recognizer(directory, excel_name, source, date_format="DDMMYYYY", delim="."):
    """
    Function to analyze whole directory of PDFs
    """
    # list of columns visible in data frame
    columns = ["Nr Faktury", "Data (okres)", "Data wystawienia", "NIP",	"Netto RAZEM", "Brutto RAZEM",
                          	"Termin płatności",	"Nr konta",	"Liczba dni na płatność", "Moc umowna", "Taryfa", "Sm", "Nota odsetkowa", "PPE", "Iloraz kwot", "UWAGA", "Nazwa dostawcy", "Nazwa pliku"]
    
    # main data frame
    df = pd.DataFrame(columns=columns, index=range(0))
    
    # data frame created for particular invoice
    df_inv = pd.DataFrame(columns=columns, index=range(0))

    # counter - serves for monitoring number of analyzed invoices
    count = 1

    # loop through every file inside given folder
    for file in os.listdir(directory + source):  
        filename = os.fsdecode(file)
        print(count, filename)

        # analyze only pdf format
        if filename.endswith("pdf") or filename.endswith("PDF"):
            # just testing - to get errors immediately
            # df_inv, invoice_type_num = invoice_recognizer(directory, filename, df, source)

            # exception block to catch documents that provide errors
            try:
                df_inv, invoice_type_num = invoice_recognizer(directory, filename, df, source)
                if invoice_type_num == 0:
                    df_inv = pd.DataFrame(columns=columns, index=range(0))
                    df_inv.loc[0, "Nazwa pliku"] = filename
                    df_inv.loc[0, "Nazwa dostawcy"] = "Nie znaleziono"
            except:
                df_inv = pd.DataFrame(columns=columns, index=range(0))
                df_inv.loc[0, "Nazwa pliku"] = filename
                df_inv.loc[0, "Nazwa dostawcy"] = "Niewspierany format"
                print('\n\nERROR - File did not recognized\n\n')

            # concatenate main data frame and data frame with information from invoice
            df = pd.concat([df, df_inv], ignore_index=True)

            count += 1

    # clean the data
    df = data_post_processing(df)

    # keep one date format if it's numeric type
    df = date_manipulation(df, date_format, delim)

    # NOT FINISHED 
    # calculate days for payment
    # df = days_for_payment(df, date_format)

    # save found information in excel file
    try:
        df.to_excel(directory + excel_name, index=False)
    except:
        input("Close Excel File and Press Enter to continue...")
        df.to_excel(directory + excel_name, index=False)

# general directory for analyzed files  
directory = '/invoices/'

# run script to analyze directory with documents
# give path to general directory, name of resulted excel file, name of folder with PDFs, expected date format and delimeter in the date format
directory_recognizer(directory, "Invoices.xlsx", "2023 December", "DDMMYYYY", ".")