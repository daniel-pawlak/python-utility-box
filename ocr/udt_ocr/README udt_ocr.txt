udt_ocr.py

Table of contents
1. Purpose of the project
2. Short description of the actions
3. Manual guide for the user
4. Libraries and Versions


1. Purpose of the project
Purpose of the project is to analyze Protocols from eUDT website which contain information about EV chargers that are
under our control.

2. Short description of the actions 
Script goes to directory with PDF files, converts every single file to image, then finds key words and puts those information in
dataframe, which is at the end exported to excel file.

3. Manual guide for the user

1) Download tesseract and provide path to it.
2) Download poppler and provide path to it.
3) Provide path to general directory, resulted file name and name of folder with PDFs.
4) Run script.
5) Analyze resulted Excel file with key information and look for missing data.

4. Libraries and Versions
List of used libraries:
- os
- re
- cv2
- pytesseract
- matplotlib
- pdf2image
- PIL
- numpy
- pandas
- shutil
- aspose.words

[Optional]
- time
- functools
- datetime
- traceback

Python version: 3.11.3

