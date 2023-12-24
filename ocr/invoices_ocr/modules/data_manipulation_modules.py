import numpy as np
from .deadline_modules import leap_year

def money_manipulation(df_row):
    """
    This function is created to manipulate money data, means to correct wrong characters and check whether there are
    some mistakes or not.
    """
    df_row["Brutto RAZEM"] = df_row["Brutto RAZEM"].astype("str")
    df_row["Netto RAZEM"] = df_row["Netto RAZEM"].astype("str")

    df_row["Brutto RAZEM"] = df_row["Brutto RAZEM"].str.replace("B", "8").replace(",", ".").replace(" ", "").replace(":", "").replace("]", "")
    df_row["Netto RAZEM"] = df_row["Netto RAZEM"].str.replace("B", "8").replace(",", ".").replace(" ", "").replace(":", "").replace("]", "")

    # replace first dot, keep the second one and decimal numbers
    df_row.loc[df_row["Brutto RAZEM"].str.count("\.") > 1, "Brutto RAZEM"] = df_row["Brutto RAZEM"].str.replace(".", "", 1)
    df_row.loc[df_row["Netto RAZEM"].str.count("\.") > 1, "Netto RAZEM"] = df_row["Netto RAZEM"].str.replace(".", "", 1)

    # print("\n\n\nDATA IN NETTO AND BRUTTO COLUMN IS NOT A STRING TYPE\n\n\n")
    try:
        df_row["Brutto RAZEM"] = df_row["Brutto RAZEM"].astype("float")
        df_row["Netto RAZEM"] = df_row["Netto RAZEM"].astype("float")
    except:
        pass

    # divide gross by net values, to check if there is anomaly
    try:
        # first check on division - result should be 1.23 (Net + VAT)
        df_row.loc[df_row["Iloraz kwot"].isnull(), "Iloraz kwot"] = (df_row["Brutto RAZEM"] / df_row["Netto RAZEM"]).round(2)
        df_row["Iloraz kwot"] = df_row["Iloraz kwot"].astype("float")

        # repairing anomalys - wrongly read value
        df_row["Brutto RAZEM"] = df_row["Brutto RAZEM"].astype("str")
        df_row.loc[((df_row["Iloraz kwot"] > 1.23) & (df_row["Brutto RAZEM"].str.startswith("4"))), "Brutto RAZEM"] = df_row["Brutto RAZEM"].str.replace("4", "3", 1)
        df_row["Brutto RAZEM"] = df_row["Brutto RAZEM"].astype("float")
        df_row.loc[df_row["Iloraz kwot"] > 1.23, "Iloraz kwot"] = (df_row["Brutto RAZEM"] / df_row["Netto RAZEM"]).round(2)

        df_row["Netto RAZEM"] = df_row["Netto RAZEM"].astype("str")
        df_row.loc[((df_row["Iloraz kwot"] < 1.23) & (df_row["Netto RAZEM"].str.startswith("4"))), "Netto RAZEM"] = df_row["Netto RAZEM"].str.replace("4", "1", 1)
        df_row["Netto RAZEM"] = df_row["Netto RAZEM"].astype("float")
        df_row.loc[df_row["Iloraz kwot"] < 1.23, "Iloraz kwot"] = (df_row["Brutto RAZEM"] / df_row["Netto RAZEM"]).round(2)
        
    except:
        pass
    
    df_row.loc[df_row["Iloraz kwot"] != 1.23, "UWAGA"] = 1

    return df_row

def data_post_processing(df):
    """
    This function is cretated to clean the data after getting all the information, so it can be presented in an understandable way
    and be used without any user involvement
    """

    df["PPE"] = df["PPE"].str.replace("§", "5").replace("^58", "59", regex=True).replace(" ", "")
    df["Nr konta"] = df["Nr konta"].str.replace("PL", "")
    df.loc[df['Nr konta'].str.len() == 26, 'Nr konta'] = df['Nr konta'].str[:2] + " " + df['Nr konta'].str[2:6] + " " + df['Nr konta'].str[6:10] + " " + df['Nr konta'].str[10:14] + " " + df['Nr konta'].str[14:18] + " " + df['Nr konta'].str[18:22] + " " + df['Nr konta'].str[22:]
    df["NIP"] = df["NIP"].str.replace("NIP:", "").str.replace("SBS", "583").str.replace("S", "5").str.replace("=", "-").str.replace(":", "").str.replace("e", "3")
    df["Taryfa"] = df["Taryfa"].str.replace("tem", "1em").str.replace("EM", "em").str.replace("it", "11").str.replace("1i1", "11").str.replace("c", "C").str.replace("i1", "11").str.replace("1ii", "11").str.replace("Cii", "C11").str.replace("‘", "")
    df["Sm"] = df["Sm"].str.replace(";", "")
    df["Data (okres)"] = df["Data (okres)"].str.replace("do", "-").str.replace("  ", " ").str.replace('[a-zA-Z]', '')

    return df

def date_manipulation(df, date_format, delim):
    """
    This piece of code manipulates dates to keep one format chosen by the user
    """

    df['Data wystawienia'] = df['Data wystawienia'].fillna("0")
    df['Termin płatności'] = df['Termin płatności'].fillna("0")

    if date_format == "DDMMYYYY":
        df.loc[df['Data wystawienia'].str.match("[0-9]{4}.[0-9]{2}.[0-9]{2}") == True, 'Data wystawienia'] = df['Data wystawienia'].str[8:] + delim + df['Data wystawienia'].str[5:7] + delim + df['Data wystawienia'].str[:4] 
        df.loc[df['Termin płatności'].str.match("[0-9]{4}.[0-9]{2}.[0-9]{2}") == True, 'Termin płatności'] = df['Termin płatności'].str[8:] + delim + df['Termin płatności'].str[5:7] + delim + df['Termin płatności'].str[:4]  

        df.loc[df['Data wystawienia'].str.match("[0-9]{2}.[0-9]{2}.[0-9]{4}") == True, 'Data wystawienia'] = df['Data wystawienia'].str[:2] + delim + df['Data wystawienia'].str[3:5] + delim + df['Data wystawienia'].str[6:10]       
        df.loc[df['Termin płatności'].str.match("[0-9]{2}.[0-9]{2}.[0-9]{4}") == True, 'Termin płatności'] = df['Termin płatności'].str[:2] + delim + df['Termin płatności'].str[3:5] + delim + df['Termin płatności'].str[6:10]

        df.loc[(df['Data wystawienia'].str[-2:].astype('int64') > df['Termin płatności'].str[-2:].astype('int64')) & (df['Termin płatności'] != "0"), 'Data wystawienia'] = df['Data wystawienia'].str[:-2] + df['Termin płatności'].str[-2:]
      
    else:
        df.loc[df['Data wystawienia'].str.match("[0-9]{4}.[0-9]{2}.[0-9]{2}") == True, 'Data wystawienia'] = df['Data wystawienia'].str[:2] + delim + df['Data wystawienia'].str[3:5] + delim + df['Data wystawienia'].str[6:10] 
        df.loc[df['Termin płatności'].str.match("[0-9]{4}.[0-9]{2}.[0-9]{2}") == True, 'Termin płatności'] = df['Termin płatności'].str[:2] + delim + df['Termin płatności'].str[3:5] + delim + df['Termin płatności'].str[6:10]  

        df.loc[df['Data wystawienia'].str.match("[0-9]{2}.[0-9]{2}.[0-9]{4}") == True, 'Data wystawienia'] = df['Data wystawienia'].str[8:] + delim + df['Data wystawienia'].str[5:7] + delim + df['Data wystawienia'].str[:4]       
        df.loc[df['Termin płatności'].str.match("[0-9]{2}.[0-9]{2}.[0-9]{4}") == True, 'Termin płatności'] = df['Termin płatności'].str[8:] + delim + df['Termin płatności'].str[5:7] + delim + df['Termin płatności'].str[:4]

        df.loc[(df['Data wystawienia'].str[2:4].astype('int64') > df['Termin płatności'].str[2:4].astype('int64')) & (df['Termin płatności'] != "0"), 'Data wystawienia'] = df['Termin płatności'].str[:4] + df['Data wystawienia'].str[4:]
    
    df.loc[df['Data wystawienia'] == "0", 'Data wystawienia'] = np.nan
    df.loc[df['Termin płatności'] == "0", 'Termin płatności'] = np.nan

    return df

def days_for_payment(df, date_format):
    """
    NOT IN USE FOR NOW, TOO MANY PROBLEMS
    This function calculates difference between deadline and date of issue.
    """
    df['Data wystawienia'] = df['Data wystawienia'].fillna("0")
    df['Termin płatności'] = df['Termin płatności'].fillna("0")
    # print((df['Data wystawienia'].str == "\d\d.\d......"))
    date = df['Data wystawienia'].loc[df['Data wystawienia'].str.match(r'^\d\d.\d......')]
    deadline = df['Termin płatności'].loc[df['Termin płatności'].str.match(r'^\d\d.\d......')]
    
    # date = df['Data wystawienia']
    # deadline = df['Termin płatności']
    # days = df["Liczba dni na płatność"]
    print(date, deadline)
    days_30 = [4, 6, 9, 11]

    if date_format == "DDMMYYYY":
        dd_1 = int(date.str[:2])
        mm_1 = int(date.str[3:5])
        yyyy_1 = int(date.str[6:])

        dd_2 = int(deadline.str[:2])
        mm_2 = int(deadline.str[3:5])

    elif date_format == "YYYYMMDD":
        dd_1 = int(date.str[-2:])
        mm_1 = int(date.str[5:7])
        yyyy_1 = int(date.str[:4])
        
        dd_2 = int(date.str[-2:])
        mm_2 = int(date.str[5:7])

    days = np.nan

    if mm_2 - mm_1 == 0:
        days = dd_2 - dd_1 - 1

    elif mm_2 - mm_1 > 0:
        if mm_1 == 2:
            if leap_year(yyyy_1) == True:
                days = 29 - dd_1 + dd_2 - 1
            else:
                days = 28 - dd_1 + dd_2 - 1       
                    
        elif mm_1 in days_30:
            days = 30 - dd_1 + dd_2 - 1

        else:
            days = 31 - dd_1 + dd_2 - 1

        if mm_2 - mm_1 != 1:
            days += 30 * (mm_2 - mm_1)

    elif mm_1 - mm_2 > 0:
        mm = mm_1 + 12 - mm_2
        days == mm * 30 + dd_2 - dd_1 - 1

    df["Liczba dni na płatność"] = days

    return df