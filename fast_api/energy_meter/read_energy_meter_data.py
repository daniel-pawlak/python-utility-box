from fastapi import FastAPI, Request
import mariadb
import logging
import time
import json
import re
import configparser
from datetime import datetime

logging.basicConfig(level=logging.INFO)

app = FastAPI()


def get_database_connection():
    """This function is created to get database connection."""
    
    config_path = configparser.ConfigParser()
    config_path.read(r"path\to\\config.ini")
    user_db = config_path["database"]["username"]
    password_db = config_path["database"]["password"]
    host_db = config_path["database"]["host"]
    port_db = int(config_path["database"]["port"])
    try:
        connection = mariadb.connect(
            user=user_db,
            password=password_db,
            host=host_db,
            port=port_db,
            database="your_db_table_name",
        )
        return connection
    except mariadb.Error as e:
        logging.warning(f"Error connecting to MariaDB Platform: {e} at {time}")
        return None


def convert_timestamp(timestamp_str):
    """This function is created to convert timestamp from UNIX format to datetime format."""

    timestamp = datetime.fromtimestamp(int(timestamp_str)).strftime("%Y-%m-%d %H:%M:%S")
    return timestamp


def swap_letters(val):
    """This function is created to correct provided data - when value is send in a mixed format, even characters have
    to be swapped with odd characters to get correct data."""

    lst_odd = [val[x] for x in range(0, len(val)) if x % 2 == 0]
    lst_even = [val[x] for x in range(0, len(val)) if x % 2 != 0]
    new_lst = []

    for i, j in zip(lst_even, lst_odd):
        new_lst.append(i)
        new_lst.append(j)

    if len(val) % 2 != 0:
        new_lst.append(lst_odd[-1])

    new_val = "".join(new_lst)

    return new_val


@app.post("/meters/")
async def receive_item(request: Request):
    """This function is created to receive data from meters and insert it into database. 
    Data is received in a form of a list of dictionaries, each dictionary contains data from one meter.
    However, if there are two meters on one location, data from both meters will be in one list of dictionaries.
    Therefore, data has to be split into separate lists of dictionaries, each list containing data from one meter.
    It is done by creating a dictionary with ModbusID as a key and list of dictionaries as a value.
    Then, each list of dictionaries is processed separately.
    """
    connection = get_database_connection()

    if connection is None:
        return {"message": "Database connection error"}

    data_bytes = await request.body()
    data_str = data_bytes.decode("utf-8")
    data_str = data_str.replace('""', '"')

    response_data = json.loads(data_str)

    modbus_data = {}

    for data_dict in response_data:
        modbus_id = data_dict.get("ModbusID", None)

        if modbus_id:
            if modbus_id not in modbus_data:
                modbus_data[modbus_id] = []

            modbus_data[modbus_id].append(data_dict)

    for modbus_id, data_list in modbus_data.items():
        # Process each ModbusID's data list as needed
        process_modbus_data(modbus_id, data_list, connection)

    connection.commit()
    connection.close()

    return {"message": "Request received successfully"}


def process_modbus_data(modbus_id, data_list, connection):
    sql_columns = [
        "Ea_plus",
        "Ea_minus",
        "Er_plus",
        "Er_minus",
        "P_avg",
        "I1_avg",
        "I2_avg",
        "I3_avg",
        "Device_name",
        "Metering_point",
        "Serial_number",
    ]

    row_values = [None] * len(sql_columns)
    row_timestamp = None
    table_name = "daq_Measurements"

    # Use a set to store the unique combinations of timestamp and ModbusID that have already been inserted
    inserted_rows = set()

    for data_dict in data_list:
        timestamp = data_dict.get("Timestamp", None)
        location = data_dict.get("Location", None)
        meter = data_dict.get("Meter", None)

        if timestamp:
            timestamp_match = re.match(r"^\d{10}$", str(timestamp))

            if timestamp_match:
                timestamp_sql = convert_timestamp(timestamp)
                row_timestamp = timestamp_sql

                for index, key in enumerate(sql_columns):
                    value = data_dict.get(key)

                    if value is not None:
                        if index < 8:
                            try:
                                row_values[index] = round(float(value), 2)
                            except ValueError:
                                pass

                        elif type(value) is str:
                            try:
                                val = value.replace("\x00", "").replace(" ", "")

                                if meter == "Siemens":
                                    if index == 9:
                                        val = val.replace(row_values[8], "")
                                    elif index == 10:
                                        val = val[-16:]
                                    row_values[index] = val

                                elif meter == "Phoenix":
                                    row_values[index] = swap_letters(val)

                            except:
                                pass

                        elif type(value) is int:
                            try:
                                row_values[index] = int(value)
                            except:
                                pass
                    else:
                        pass

                if all(val is not None for val in row_values):
                    # Check if the row has already been inserted
                    row_identifier = (timestamp_sql, modbus_id, location)
                    logging.info("ROW   ", row_identifier)
                    logging.info(row_values)
                    if row_identifier not in inserted_rows:
                        insert_values = (
                            [row_timestamp]
                            + row_values[:-3]
                            + [location]
                            + row_values[-3:]
                        )

                        insert_sql = f"INSERT INTO {table_name} VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                        cursor = connection.cursor()
                        cursor.execute(insert_sql, insert_values)
                        logging.info("INSERTED:", row_identifier)
                        inserted_rows.add(row_identifier)

                    row_values = [None] * len(sql_columns)
                    row_timestamp = None


@app.get("/test/")
async def test_endpoint():
    return {"message": "Works well"}
