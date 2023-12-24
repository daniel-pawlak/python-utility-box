udt_scraper_numbers.py

Table of contents
1. Purpose of the project
2. Short description of the actions
3. Manual guide for the user
4. Libraries and Versions


1. Purpose of the project
Purpose of the project is to automatically download Protocols from eUDT website which contain information about EV chargers that are
under our control.

2. Short description of the actions 
Script logs into eUDT website with given credentials, then goes to device register and looks for details of the device 
for given Evidence Number. List of Evidence Numbers is downloaded earlier by the user from eUDT website. 

3. Manual guide for the user

1) Log into eUDT website (https://eudt.gov.pl/)
2) Go to "Rejestr urządzeń" link under "Urządzenia" tab on left menu
3) Export Excel file by clicking Eksportuj > Excel on the right side
4) Copy path of that newly exported file and place it in script as a value of "excel_report" variable (at the end of script)
remembering to keep convention of naming python file path
5) Create .json file with credentials to your eUDT account in following convention:

{
"password":"your password",
"email":"your email"
} 

6) Copy path to that file and place it as a value of f variable in udt_scraper function
7) Download edgedriver and provide path to it in script to "path" variable in udt_scraper function
8) Run script
9) Copy downloaded PDFs to desirable folder

4. Libraries and Versions
List of used libraries:
- selenium
- pandas
- json
[Optional]
- time
- functools
- datetime
- traceback

Python version: 3.11.3

