from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import pandas as pd
import time
import functools
import datetime
import json
import traceback
import logging
import pytz
from time import perf_counter


logging.basicConfig(level=logging.INFO)

def measure_execution_time(func):
    """Timer checks how much time does it take to run the script"""
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        warsaw_tz = pytz.timezone("Europe/Warsaw")
        start_time = perf_counter()

        try:
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            run_time = end_time - start_time
            end_hour = datetime.datetime.now(warsaw_tz).strftime("%Y-%m-%d %H:%M:%S")
            
            logging.info(
                f"Execution time of {func.__name__}: {run_time:.2f} seconds on {end_hour}, which is {time.strftime('%H:%M:%S', time.gmtime(run_time))}."
            )
           
            return result
            
        except Exception as err:
            end_time = time.perf_counter()
            run_time = end_time - start_time
            end_hour = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            logging.warning(
                f"""
                
                ATTENZIONE
                
                {func.__name__} failed after {run_time:.4f} secs on {end_hour}. It took {time.strftime('%H:%M:%S', time.gmtime(run_time))}.
                
                Unexpected {err=}, {type(err)=}.
                """
            )

            logging.warning(traceback.format_exc())

    return wrapper_timer

def site_scraper(ev_number, driver, not_founds):
    """Function to open every single site for given evidence number and download protocol"""
    # input evidence number in search field
    ev_box = driver.find_element(By.XPATH, "//input[@id='UdtNumber15']")
    ev_box.send_keys(Keys.CONTROL, 'a')
    ev_box.send_keys(ev_number)
    ev_box.send_keys(Keys.ENTER)

    try:
        # slide to the right
        slider = driver.find_element(By.XPATH, "//div[@class='table-first-top-scroll']")
        move = ActionChains(driver)
        move.click_and_hold(slider).move_by_offset(400, 0).release().perform()
    except:
        pass        

    # open site with details - whole part
    try:
        details = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, f"//td[@id='0details']//button[@type='button'][contains(text(),'Szczegóły')]"))).click()

        time.sleep(1)
        print('Opened')
    except:
        try:
            # slide to the right
            slider = driver.find_element(By.XPATH, "//div[@class='table-first-top-scroll']")
            move = ActionChains(driver)
            move.click_and_hold(slider).move_by_offset(600, 0).release().perform()
            
            details = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//td[@id='0details']//button[@type='button'][contains(text(),'Szczegóły')]"))).click()

            time.sleep(2)
            print('Opened after exception')
        except:
            print('No details')
            not_founds.append(f'{ev_number}')
            return print("No slider", ev_number, "Not found")
        
    # open e-documentation tab
    e_docs = driver.find_element(By.XPATH, "//span[normalize-space()='E-dokumentacja']").click()
    time.sleep(2)

    # download the protocol
    try:
        protocol = driver.find_element(By.XPATH, "//td[contains(text(),'Protokół z czynności UDT')]/following-sibling::td").click()
        time.sleep(2)
    except:
        try:
            print('tried again')
            # slide down
            driver.execute_script(f"window.scrollTo(0, window.scrollY + 50)")
            time.sleep(1)
            
            protocol = driver.find_element(By.XPATH, "//td[contains(text(),'Protokół z czynności UDT')]/following-sibling::td").click()
            time.sleep(2)

        except:
            try:
                print('tried again x2')
                # slide down
                driver.execute_script(f"window.scrollTo(0, window.scrollY + 200)")
                time.sleep(1)
                
                protocol = driver.find_element(By.XPATH, "//td[contains(text(),'Protokół z czynności UDT')]/following-sibling::td").click()
                time.sleep(2)

            except:
                print("Not found")
                not_founds.append(f'{ev_number}')
                return print("No protocol", ev_number, "Not found")

@measure_execution_time
def udt_scraper(excel_report):
    """Scraper for downloading PDF of acceptance protocols"""
    
    """
    Function to run selenium, log into eUDT site, read Excel file with Evidence Numbers 
    and download protocols for those numbers
    """
    
    # path for edgedriver and options for driver
    path = 'msedgedriver'       # path to be changed

    driver = webdriver.Edge(path)

    # Opening JSON file
    f = open('udt.json')  # d.paw email
    
    # returns JSON object as a dictionary
    data = json.load(f)

    # login credentials
    email = data['email']
    password = data['password']

    # open browser
    url = 'https://eudt.gov.pl'

    driver.maximize_window()
    driver.get(url)

    # send login
    login = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Login (e-mail)"]')))
    
    login.send_keys(email)
    time.sleep(1)

    # send password
    password_elem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Hasło"]')))
    
    password_elem.send_keys(password)
    time.sleep(1)

    # log to udt site after passing email and password
    logging = driver.find_element(By.XPATH, "//button[contains(text(),'Zaloguj się')]").click()
    time.sleep(2)

    # close cookie
    try:
        cookie = driver.find_element(By.XPATH, "//a[contains(text(),'Zamknij')]").click()
        time.sleep(1)
    except:
        pass

    # open site with list of devices
    new_url = "https://eudt.gov.pl/device/list"
    driver.get(new_url)
    time.sleep(3)

    # create empty list to collect not found elements
    not_founds = []

    # read excel file with evidence numbers
    df = pd.read_excel(excel_report)
    evidence = df.iloc[:-3, 0]

    # keep number of not found files and general counter
    c_general = 0
    c_not_found = 0
    # loop to get all the elements from a page
    for ev_number in evidence:
        c_general += 1
        print(ev_number, c_general)
        
        try:
            site_scraper(ev_number, driver, not_founds)
        except:
            try:
                driver.get(new_url)
                time.sleep(2)
                site_scraper(ev_number, driver, not_founds)
            except:
                c_not_found += 1
                print(ev_number, "Not found", c_not_found, c_general)
                not_founds.append(f'{ev_number}')
                continue

    print("\n\nNot found: \n\n", not_founds, "\n\n")
    print("Number of not founds:", len(not_founds))
    print("General number:", c_general)

    # new list for not found items
    new_not_found = []

    # looping through not_found list to make a second try of catching items
    for ev_number in not_founds:
        try:
            site_scraper(ev_number, driver, new_not_found)
        except:
            try:
                driver.get(new_url)
                time.sleep(2)
                site_scraper(ev_number, driver, new_not_found)
            except:
                c_not_found += 1
                print(ev_number, "Not found", c_not_found, c_general)
                new_not_found.append(f'{ev_number}')
                continue
    
    print("\n\nNot found: \n\n", new_not_found, "\n\n")
    print("Number of not founds:", len(new_not_found))

    nf_df = pd.DataFrame(new_not_found)
    nf_df.to_excel("Not found evidences.xlsx")

# path to excel report with evidence numbers
excel_report = 'devices.xlsx'
udt_scraper(excel_report)