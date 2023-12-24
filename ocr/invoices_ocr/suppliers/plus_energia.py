import numpy as np
import re

def plus_energia(d, num, df_row):
    """
    Piece of code to analyze invoice received from Plus Energia
    """   
    word_vat = "vat"
    word_1 = "razem"
    word_2 = "rozliczenie"
    word_3 = "sprzedawca:"
    word_nip = "nip:"
    word_4 = "termin"
    word_5 = "konta:"
    word_6 = "taryfa:"
    word_8 = 'PPE'

    vat = np.nan
    vat_index = len(d['text'])

    netto = np.nan
    brutto = np.nan
    total_index = len(d['text'])

    nip = np.nan
    nip_index = len(d['text'])

    period = np.nan
    date = np.nan
    deadline = np.nan
    account = np.nan
    tariff = np.nan
    power = np.nan
    sm = np.nan
    interest = np.nan
    no_of_days = np.nan
    ppe = np.nan

    month_1 = ""
    month_2 = ""
    day_1 = ""
    day_2 = ""

    d['text'] = [x for x in d['text'] if x != "zt"]
    n_boxes = len(d['text'])
    
    # if num == 0:
    #     print(d['text'])

    # loop through every word
    for i in range(n_boxes):
        if i < 800:
            # analyze only first page for some information
            if num == 0:
                # vat
                if re.match(word_vat, d['text'][i].lower()):
                    if i < vat_index:
                        vat = d['text'][i + 2]
                        vat_index = i
                        print("vat", vat)
                # total 
                if re.match(word_1, d['text'][i].lower()):
                    if i < total_index:
                        if len(d['text'][i + 1]) <= 2:
                            netto = d['text'][i + 1] + d['text'][i + 2]
                            if len(d['text'][i + 3]) <= 2:
                                brutto = d['text'][i + 5] + d['text'][i + 6]
                            else:
                                brutto = d['text'][i + 4] + d['text'][i + 5]
                        else:
                            netto = d['text'][i + 1]
                            if len(d['text'][i + 3]) <= 2:
                                brutto = d['text'][i + 3] + d['text'][i + 4]
                            else:
                                brutto = d['text'][i + 3]  
                        total_index = i 
                        print("total", netto, brutto)
                # calculation period
                if re.match(word_2, d['text'][i].lower()):
                    period = d['text'][i + 1]
                    print(period)
                # date
                if re.match(word_3, d['text'][i].lower()):
                    date = f"{d['text'][i + 2]} {d['text'][i + 3]} {d['text'][i + 4]}"
                    month_1 = d['text'][i + 3]
                    day_1 = int(d['text'][i + 2])
                    print(date)
                # nip
                if re.match(word_nip, d['text'][i].lower()):
                    if i < nip_index:
                        nip = d['text'][i + 1]
                        nip_index = i
                        print("nip", nip)
                # deadline for payment
                if re.match(word_4, d['text'][i].lower()) and re.match('^[0-9]', d['text'][i + 2]):
                    deadline = f"{d['text'][i + 2]} {d['text'][i + 3]} {d['text'][i + 4]}"
                    print(deadline)
                    month_2 = d['text'][i + 3]
                    day_2 = int(d['text'][i + 2]) 
                # account
                if re.match(word_5, d['text'][i].lower()) and re.match('^[0-9]', d['text'][i + 1]):
                    account = f"{d['text'][i + 1]} {d['text'][i + 2]} {d['text'][i + 3]} {d['text'][i + 4]} {d['text'][i + 5]} {d['text'][i + 6]} {d['text'][i + 7]}"
                    print(account)
                
            # analyze next page
            # tariff
            if re.match(word_6, d['text'][i].lower()):
                tariff = d['text'][i + 1]
                print(tariff)
            # PPE
            if re.match(word_8, d['text'][i].replace(":", "")):
                ppe = d['text'][i + 1]
                print("ppe", ppe)

    # calculate number of days from receiveing the invoice till the deadline
    if num == 0:
        if month_1 == month_2:
            no_of_days = day_2 - day_1 - 1
        else:
            no_of_days = day_2 - day_1 - 1 + 30
        print("no_of_days", no_of_days)

    df_row.loc[df_row["Nr Faktury"].isnull(), "Nr Faktury"] = vat
    df_row.loc[df_row["Data (okres)"].isnull(), "Data (okres)"] = period
    df_row.loc[df_row["Data wystawienia"].isnull(), "Data wystawienia"] = date 
    df_row.loc[df_row["NIP"].isnull(), "NIP"] = nip
    df_row.loc[df_row["Netto RAZEM"].isnull(), "Netto RAZEM"] = netto
    df_row.loc[df_row["Brutto RAZEM"].isnull(), "Brutto RAZEM"] = brutto 
    df_row.loc[df_row["Termin płatności"].isnull(), "Termin płatności"] = deadline 
    df_row.loc[df_row["Nr konta"].isnull(), "Nr konta"] = account
    df_row.loc[df_row["Liczba dni na płatność"].isnull(), "Liczba dni na płatność"] = no_of_days 
    df_row.loc[df_row["Moc umowna"].isnull(), "Moc umowna"] = power
    df_row.loc[df_row["Taryfa"].isnull(), "Taryfa"] = tariff
    df_row.loc[df_row["Sm"].isnull(), "Sm"] = sm 
    df_row.loc[df_row["Nota odsetkowa"].isnull(), "Nota odsetkowa"] = interest
    df_row.loc[df_row["PPE"].isnull(), "PPE"] = ppe

    return df_row

if __name__ == "__main__":
    print("Plus Energia")
