import numpy as np
import re

def pge(d, num, df_row):
    """
    Piece of code to analyze invoice received from PGE
    """   
    word_vat = "faktura"
    word_vat_nr = "nr"
    word_1_1 = "warto"
    word_1_2 = "og"
    word_1_3 = "oq"
    word_2_1 = "okres"
    word_2_2 = "od"
    word_3 = "wystawiona"
    word_nip = "nip"
    word_4_1 = "termin"
    word_5 = "PPE"
    word_6 = "taryfa"
    word_7_1 = "moc"
    word_7_2 = "umowna:"
    word_8 = "Sm"

    vat = np.nan
    vat_index = len(d['text'])

    netto = np.nan
    brutto = np.nan
    total_index = len(d['text'])

    nip = np.nan
    nip_index = len(d['text'])

    date_index = len(d['text'])

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

    d['text'] = [x for x in d['text'] if x != "|"]

    n_boxes = len(d['text'])
    # if num == 1:
    #     print(d['text'])

    # loop through every word
    for i in range(n_boxes):
        if i < 1800:
            # analyze only first page for some information
            if num == 0:
                # vat
                if re.match("\w?\w?/[0-9]{6}/\w?\w?\w?/FK/\w?\w?\w?\w?", d['text'][i]):
                    if i < vat_index:
                        vat = d['text'][i]
                        vat_index = i
                        print("vat", vat)
                
                # date
                if re.match(word_3, d['text'][i].lower().replace(":", "")) and re.match('^[0-9]{2}/[0-9]{2}/[0-9]{4}', d['text'][i + 2]):
                    if i < date_index:
                        date = d['text'][i + 2]
                        date_index = i
                        print("date", date)

                # nip
                if re.match(word_nip, d['text'][i].lower()):
                    if i < nip_index:
                        if d['text'][i + 1].lower() != "|" and d['text'][i + 1] != ":":
                            if d['text'][i + 1] != "5833195289" and d['text'][i + 1] != "583-319-52-89":
                                nip = d['text'][i + 1]
                                nip_index = i
                        else:
                            if d['text'][i + 2] != "5833195289" and d['text'][i + 2] != "583-319-52-89":
                                nip = d['text'][i + 2]
                                nip_index = i
                        print("nip", nip)

            # deadline for payment
            if re.match(word_4_1, d['text'][i].lower()) and re.match('^[0-9]{2}.[0-9]{2}.[0-9]{4}', d['text'][i + 2]):
                deadline = d['text'][i + 2]
                print("deadline", deadline)

            # total
            # netto
            if i + 1 < n_boxes and re.search(word_1_1, d['text'][i].lower()) and (re.search(word_1_2, d['text'][i + 1].lower()) or re.search(word_1_3, d['text'][i + 1].lower())) and re.match('^[0-9]', d['text'][i + 2]) and re.match('^[0-9]', d['text'][i + 4]):
                if i < total_index:   
                    if len(d['text'][i + 2]) <= 2:
                        netto = d['text'][i + 2] + d['text'][i + 3]
                        if len(d['text'][i + 5]) <= 2:
                            brutto = d['text'][i + 7] + d['text'][i + 8]
                        else:
                            brutto = d['text'][i + 6] + d['text'][i + 7]
                    else:
                        netto = d['text'][i + 2]
                        if len(d['text'][i + 5]) <= 2:
                            brutto = d['text'][i + 5] + d['text'][i + 6]
                        else:
                            brutto = d['text'][i + 5]  
                    total_index = i 
                    print("total", netto, brutto)
          
            # period
            if re.match(word_2_1, d['text'][i].lower()) and re.match(word_2_2, d['text'][i + 1].lower()) and re.match('^[0-9]{2}/[0-9]{2}/[0-9]{4}', d['text'][i + 2]):
                period = f"{d['text'][i + 2]} {d['text'][i + 3]} {d['text'][i + 4]}"
                print("period", period)           

            # account
            if re.match('\w?\w?[0-9]{2}$', d['text'][i]) and re.match('^[0-9]{4}$', d['text'][i + 1]) and re.match('^[0-9]{4}$', d['text'][i + 2]) and re.match('^[0-9]{4}$', d['text'][i + 3]) and re.match('^[0-9]{4}$', d['text'][i + 4]) and re.match('^[0-9]{4}$', d['text'][i + 5]) and re.match('^[0-9]{4}$', d['text'][i + 6]):
                account = f"{d['text'][i]} {d['text'][i + 1]} {d['text'][i + 2]} {d['text'][i + 3]} {d['text'][i + 4]} {d['text'][i + 5]} {d['text'][i + 6]}"
                print("account", account)

            # power from agreement
            if re.match(word_7_1, d['text'][i].lower()) and re.match(word_7_2, d['text'][i + 1].lower()):
                power = d['text'][i + 2]
                print("power", power)

            # tariff
            if re.match(word_6, d['text'][i].lower().replace(":", "")) and d['text'][i + 1] != "PGE":
                tariff = d['text'][i + 1]
                print("tariff", tariff)

            # sm
            if re.match(word_8, d['text'][i].replace(":", "").replace(")", "").replace("(", "")):
                sm = d['text'][i + 1]
                print("sm", sm)

            # PPE
            if re.match(word_5, d['text'][i].replace(":", "")):
                ppe = d['text'][i + 1]

                if len(ppe.replace("_", "")) < 18:
                    ppe += d['text'][i + 2]
                print("ppe", ppe)
    
    # calculate number of days from receiveing the invoice till the deadline
    try:  
        if str(deadline)[3:5] == str(date)[3:5]:
            no_of_days = int(str(deadline)[:2]) - int(str(date)[:2]) - 1
        else:
            no_of_days = int(str(deadline)[:2]) - int(str(date)[:2]) - 1 + 30
        print("no of days", no_of_days)
    except:
        try:
            if str(deadline)[3:5] == str(df_row.loc[0, "Data wystawienia"])[3:5]:
                no_of_days = int(str(deadline)[:2]) - int(str(df_row.loc[0, "Data wystawienia"])[:2]) - 1
            else:
                no_of_days = int(str(deadline)[:2]) - int(str(df_row.loc[0, "Data wystawienia"])[:2]) - 1 + 30
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
