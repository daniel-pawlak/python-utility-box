import numpy as np
import re

def energa_operator(number_of_ppe, d, num, df_row, ppe_num, period_num, single_amounts, tariff_num,
    power_num, netto_num, brutto_num):
    """
    Piece of code to analyze invoice received from Energa Operator
    """   
    word_vat = "vat"
    word_1_1 = "razem"
    word_1_2 = "wart"
    word_1_3 = "netto"
    word_2_1 = "rozliczenie"
    word_2_2 = "okres"
    word_3 = "wystawiono"
    word_nip = "nip"
    word_4_1 = "termin"
    # word_4_2 = "platnosci:"
    # word_4_3 = "ptatnosci:"
    word_5_1 = "numer"
    word_5_2 = "PPE"
    word_6 = "taryfowa"
    word_7_1 = "moc"
    word_7_2 = "umowna:"
    word_8 = "Sm"
    word_9 = "odsetki"
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
        # limit number of rows that can be created
        if single_amounts > number_of_ppe:
            single_amounts = number_of_ppe

        if i < 1800:
            # analyze only first page for some information
            if num == 0:
                # vat
                if re.match(word_vat, d['text'][i].lower()):
                    if i < vat_index:
                        vat = d['text'][i + 1]

                        if len(vat) < 25:
                            vat += d['text'][i + 2]

                            if len(vat) < 25:
                                vat += d['text'][i + 3]

                        vat_index = i
                        print("vat", vat)
                             
                
                # date
                if re.match(word_3, d['text'][i].lower()):
                    date = d['text'][i + 2]
                    print("date", date)
                # nip
                if re.match(word_nip, d['text'][i].lower()) and d['text'][i + 1] != "5833195289" and d['text'][i + 1] != "583-319-52-89":
                    if i < nip_index:
                        nip = d['text'][i + 1]
                        nip_index = i
                        print("nip", nip)
                # deadline for payment
                if re.match(word_4_1, d['text'][i].lower()) and re.match("^\d\d.\d\d.\d\d\d\d$", d['text'][i + 2]):
                    deadline = d['text'][i + 2]
                    print("deadline", deadline)
                # interest rate
                if re.match(word_9, d['text'][i].lower()):
                    interest = d['text'][i + 4]
                    print("interest", interest)

            # variables       
            # total 
            if re.match(word_1_1, d['text'][i].lower()) and re.match(word_1_3, d['text'][i + 2].lower()) and re.match('^[0-9]', d['text'][i + 3]):

                netto = d['text'][i + 3]
                if len(netto) < 6:
                    netto += d['text'][i + 4]

                # limit number of rows that can be created
                if netto_num > number_of_ppe:
                    netto_num = number_of_ppe
                if brutto_num > number_of_ppe:
                    brutto_num = number_of_ppe

                print(netto)
                
                df_row.loc[netto_num, "Netto RAZEM"] = netto
                netto_num += 1                
                df_row.loc[brutto_num, "Brutto RAZEM"] = brutto
                brutto_num += 1  

            # calculation period
            if re.match(word_2_1, d['text'][i].lower()) and re.match(word_2_2, d['text'][i + 2].lower()):
                period = f"{d['text'][i + 3]} {d['text'][i + 4]} {d['text'][i + 5]}"
                print("period", period)

                # limit number of rows that can be created
                if period_num > number_of_ppe:
                    period_num = number_of_ppe

                df_row.loc[period_num, "Data (okres)"] = period
                period_num += 1

            # account
            if re.match('^[0-9]{2}$', d['text'][i]) and re.match('^\d\d\d\d', d['text'][i + 1]) and re.match('^\d\d\d\d', d['text'][i + 2]):
                account = f"{d['text'][i]} {d['text'][i + 1]} {d['text'][i + 2]} {d['text'][i + 3]} {d['text'][i + 4]} {d['text'][i + 5]} {d['text'][i + 6]}"
                account = account.replace("W", "").strip()
                print("account", account)

            # power from agreement
            if re.match(word_7_1, d['text'][i].lower()) and re.match(word_7_2, d['text'][i + 1].lower()):
                power = d['text'][i + 2]
                print("power", power)

                # limit number of rows that can be created
                if power_num > number_of_ppe:
                    power_num = number_of_ppe

                df_row.loc[power_num, "Moc umowna"] = power
                power_num += 1

            # tariff
            if re.match(word_6, d['text'][i].lower()):
                tariff = d['text'][i + 1]
                print("tariff", tariff)

                # limit number of rows that can be created
                if tariff_num > number_of_ppe:
                    tariff_num = number_of_ppe

                df_row.loc[tariff_num, "Taryfa"] = tariff
                tariff_num += 1
                
            # sm
            if re.match(word_8, d['text'][i].replace(":", "")):
                sm = d['text'][i + 1]
                print("sm", sm)

                df_row.loc[power_num, "Sm"] = sm

            # PPE
            if re.match(word_5_1, d['text'][i].replace(":", "").lower()) and re.match(word_5_2, d['text'][i + 1].replace(":", "")) and re.match('^[0-9]', d['text'][i + 2]):
                ppe = d['text'][i + 2]
                print("ppe", ppe)

                # limit number of rows that can be created
                if ppe_num > number_of_ppe:
                    ppe_num = number_of_ppe

                if ppe not in df_row['PPE']:
                    print("ppe", ppe, "num", ppe_num)
                    df_row.loc[ppe_num, "PPE"] = ppe
                    ppe_num += 1

    # calculate number of days from receiveing the invoice till the deadline
    if num == 0:  
        try:      
            if str(deadline)[3:5] == str(date)[3:5]:
                no_of_days = int(str(deadline)[:2]) - int(str(date)[:2]) - 1
            else:
                no_of_days = int(str(deadline)[:2]) - int(str(date)[:2]) - 1 + 30
            print("no of days", no_of_days)
        except:
            pass

    # constant
    df_row.loc[df_row["Nr Faktury"].isnull(), "Nr Faktury"] = vat
    df_row.loc[df_row["Data wystawienia"].isnull(), "Data wystawienia"] = date 
    df_row.loc[df_row["NIP"].isnull(), "NIP"] = nip
    df_row.loc[df_row["Termin płatności"].isnull(), "Termin płatności"] = deadline 
    df_row.loc[df_row["Sm"].isnull(), "Sm"] = sm 
    df_row.loc[df_row["Nota odsetkowa"].isnull(), "Nota odsetkowa"] = interest
    df_row.loc[df_row["Nr konta"].isnull(), "Nr konta"] = account
    df_row.loc[df_row["Liczba dni na płatność"].isnull(), "Liczba dni na płatność"] = no_of_days 

    # variable - fill empty with general value in case it is added just once
    df_row.loc[df_row["PPE"].isnull(), "PPE"] = ppe
    df_row.loc[df_row["Data (okres)"].isnull(), "Data (okres)"] = period
    df_row.loc[df_row["Netto RAZEM"].isnull(), "Netto RAZEM"] = netto
    df_row.loc[df_row["Brutto RAZEM"].isnull(), "Brutto RAZEM"] = brutto 
    df_row.loc[df_row["Moc umowna"].isnull(), "Moc umowna"] = power
    df_row.loc[df_row["Taryfa"].isnull(), "Taryfa"] = tariff

 
    return df_row, ppe_num, period_num, single_amounts, tariff_num, power_num, netto_num, brutto_num
