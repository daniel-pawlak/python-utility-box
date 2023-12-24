import numpy as np
import re

def enea(d, num, df_row):
    """
    Piece of code to analyze invoice received from Enea
    """   
    word_vat = "oryginal"
    word_1_1 = "razem"
    word_1_2 = "dystrybucji"
    word_1_3 = "dyslrybucji"
    word_2_1 = "okres"
    word_2_2 = "od"
    word_3 = "wystawienia:"
    word_nip = "nip:"
    word_4_1 = "termin"
    # word_4_2 = "platnosci:"
    word_5 = "PPE"
    word_6 = "taryfa:"
    word_7_1 = "moc"
    word_7_2 = "umowna"

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
                        vat = d['text'][i - 2]
                        if len(vat) < 5:
                           vat = d['text'][i - 1] 
                        vat_index = i
                        print("vat", vat)
                # total 
                if re.match(word_1_1, d['text'][i].lower()) and (re.match(word_1_2, d['text'][i + 3].lower()) or re.match(word_1_3, d['text'][i + 3].lower())):
                    if i < total_index:
                        netto = d['text'][i + 4]
                        brutto = d['text'][i + 7]
                        total_index = i
                        print("total", netto, brutto)
                # date
                if re.match(word_3, d['text'][i].lower()):
                    date = d['text'][i + 1]
                    print("date", date)
                # nip
                if re.match(word_nip, d['text'][i].lower()) and d['text'][i + 1] != "5833195289":
                    if i < nip_index:
                        nip = d['text'][i + 1]
                        nip_index = i
                        print("nip", nip)
                # deadline for payment
                if re.match(word_4_1, d['text'][i].lower()) and re.match("^\d\d.\d\d.\d\d\d\d", d['text'][i + 2]):
                    deadline = d['text'][i + 2]
                    print("deadline", deadline)

            # calculation period
            if re.match(word_2_1, d['text'][i].lower()) and re.match(word_2_2, d['text'][i + 1].lower()):
                period = f"{d['text'][i + 2]} {d['text'][i + 3]} {d['text'][i + 4]}"
                print("period", period)

            # account
            if i < (n_boxes - 6):
                if re.match('^[0-9]{2}$', d['text'][i]) and re.match('^\d\d\d\d', d['text'][i + 1]) and re.match('^\d\d\d\d', d['text'][i + 2]):
                    account = f"{d['text'][i]} {d['text'][i + 1]} {d['text'][i + 2]} {d['text'][i + 3]} {d['text'][i + 4]} {d['text'][i + 5]} {d['text'][i + 6]}"
                    account = account.replace("W", "").strip()
                    print("account", account)
            # power from agreement
            if re.match(word_7_1, d['text'][i].lower()) and re.match(word_7_2, d['text'][i + 1].lower()):
                power = d['text'][i + 2]
                print("power", power)
            # tariff
            if re.match(word_6, d['text'][i].lower()):
                tariff = d['text'][i + 1]
                print("tariff", tariff)
            # PPE
            if re.match(word_5, d['text'][i].replace(":", "")):
                ppe = d['text'][i + 1]
                print("ppe", ppe)
    # calculate number of days from receiveing the invoice till the deadline
    try:
        if num == 0:        
            if str(deadline)[3:5] == str(date)[3:5]:
                no_of_days = int(str(deadline)[:2]) - int(str(date)[:2]) - 1
            else:
                no_of_days = int(str(deadline)[:2]) - int(str(date)[:2]) - 1 + 30
            print("no of days", no_of_days)
    except:
        pass

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
