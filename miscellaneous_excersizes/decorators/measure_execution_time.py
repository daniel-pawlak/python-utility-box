import functools
import time
import datetime
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