import pandas as pd
from ping3 import ping
from icecream import ic
from time import perf_counter
import time
import datetime
import logging
import pytz


# Configure the logging settings
logging.basicConfig(
    filename=r"path\to\your\ip_checker_info.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Create a StreamHandler and set its log level to INFO
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARNING)

# Create a formatter and add it to the StreamHandler
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
stream_handler.setFormatter(formatter)

# Add the StreamHandler to the logger
logger = logging.getLogger()
logger.addHandler(stream_handler)

warsaw_tz = pytz.timezone("Europe/Warsaw")

def measure_execution_time(func):
    def wrapper(*args, **kwargs):
        start_time = perf_counter()
        result = func(*args, **kwargs)
        end_time = perf_counter()
        run_time = end_time - start_time
        end_hour = datetime.datetime.now(warsaw_tz).strftime("%H:%M:%S")
        logging.info(
            f"Execution time of {func.__name__}: {run_time:.4f} seconds at {end_hour}, which is {time.strftime('%H:%M:%S', time.gmtime(run_time))}."
        )
        return result

    return wrapper

@measure_execution_time
def ip_check(excel_file_path):
    """
    This function is created to check group of IPs whether they are active or not. IPs are kept in excel file.
    As a result user gets new file, which is a copy of his main file with column added at the end.
    This column contains an information if checked IP is active.
    """

    # Read the Excel file into a Pandas DataFrame
    xls = pd.ExcelFile(excel_file_path)

    # Load the specific sheet ("SIM cards") into a DataFrame
    df = xls.parse("Sheet in your file", header=0)

    # Create an empty list to store "Active?" values
    active_values = []

    # Loop through IP addresses and ping, then add "Yes" or "No" based on the response
    for index, row in df.iterrows():
        ip = row["IP"]
        if not pd.isna(ip):
            response_time = ping(ip)
            if response_time is not None:
                active_values.append("Yes")
            else:
                active_values.append("No")
        else:
            active_values.append("N/A")

        # print useful information with usage of ic imported from icecream
        ic(index, response_time)

    # Add the "Active?" column to the DataFrame
    df["Active?"] = active_values

    try:
        df.to_excel(
            r"path\New_file_with_ips.xlsx",
            sheet_name="New IPs",
            index=False,
        )
    except:
        input("Close Excel and try again...")
        df.to_excel(
            r"path\New_file_with_ips.xlsx",
            sheet_name="New IPs",
            index=False,
        )

# Define the path to your Excel file which is a source for your code
excel_file_path = r"path\File_with_ips.xlsx"

ip_check(excel_file_path)