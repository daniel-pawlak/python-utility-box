import numpy as np
import re

def polenergia_sprzedaz(number_of_ppe, d, num, df_row, ppe_num, period_num, single_amounts, tariff_num,
    power_num, netto_num, brutto_num):
    """
    Piece of code to analyze invoice received from Polenergia Sprzedaż
    """   
    word_vat = "vat"
    word_vat_nr = "nr"
    word_1_1 = "kWh"
    word_1_2 = "mc"
    word_1_3 = "mec"
    word_3 = "wystawienia:"
    word_nip = "nip:"
    word_4_1 = "termin"
    word_4_2 = "ptatnosci"
    vat = np.nan
    vat_index = len(d['text'])

    netto = np.nan
    netto2 = np.nan
    brutto = np.nan

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
    # if num == 1:
    #     print(d['text'])
    #     input()
    
    # loop through every word
    for i in range(n_boxes):

        # analyze only first page for some information
        if num == 0:
            # vat
            if re.match(word_vat, d['text'][i].lower()) and re.match(word_vat_nr, d['text'][i + 1].lower()):
                if i < vat_index:
                    vat = d['text'][i + 2]
                    vat_index = i
                    print("vat", vat)
            
            # date
            if re.match(word_3, d['text'][i].lower()):
                date = d['text'][i + 1]
                print("date", date)

            # nip
            if re.search(word_nip, d['text'][i].lower()):
                if i < nip_index:
                    if bool(re.search("5833195289", d['text'][i + 1])) == False and bool(re.search("583-319-52-89", d['text'][i + 1])) == False and bool(re.search("5833195289", d['text'][i])) == False and bool(re.search("583-319-52-89", d['text'][i])) == False:
                        if re.match("^[0-9]{3}", d['text'][i + 1]):
                            nip = d['text'][i + 1]
                        elif re.search("[0-9]{3}", d['text'][i]):
                            nip = d['text'][i]
                        nip_index = i
                        print("nip", nip)

            # deadline for payment
            if re.match(word_4_1, d['text'][i].lower()) and re.match(word_4_2, d['text'][i + 1].lower()) and re.match('^[0-9]{2}', d['text'][i + 2]):
                deadline = d['text'][i + 2].replace(",", "")
                print("deadline", deadline)
        
        # variables
        # total 
        # netto
        if re.match(word_1_1, d['text'][i]) and re.match("^[0-9]", d['text'][i + 2]):
            if len(d['text'][i + 2]) <= 2:
                netto = d['text'][i + 2] + d['text'][i + 3]
            else:
                netto = d['text'][i + 2]
            
            netto = netto.replace(",", ".").replace(":", "").replace("]", "").replace("B", "8")

            if netto.count(".") > 1:
                netto = netto.replace(".", "", 1)

            netto = float(netto)
          
            df_row.loc[period_num - 1, "Netto RAZEM"] = netto

        if (re.match(word_1_2, d['text'][i]) or re.match(word_1_3, d['text'][i])) and re.match("^[0-9]", d['text'][i + 2]):
            if len(d['text'][i + 2]) <= 2:
                netto2 = d['text'][i + 2] + d['text'][i + 3]
            else:
                netto2 = d['text'][i + 2] 

           
            netto2 = netto2.replace(",", ".").replace(":", "").replace("]", "").replace("B", "8")

            if netto2.count(".") > 1:
                netto2 = netto2.replace(".", "", 1)

            netto2 = float(netto2)

            print("netto", netto, netto2)
            #######################
            # limit number of rows that can be created
            if netto_num > number_of_ppe:
                netto_num = number_of_ppe
            if brutto_num > number_of_ppe:
                brutto_num = number_of_ppe

            df_row.loc[period_num - 1, "Netto RAZEM"] = df_row.loc[period_num - 1, "Netto RAZEM"] + netto2
            netto_num += 1     

        # calculation period #######################
        if re.match("[0-9]{4}-[0-9]{2}-[0-9]{2}", d['text'][i].lower()) and re.match("-", d['text'][i + 1].lower()) and re.match("[0-9]{4}-[0-9]{2}-[0-9]{2}", d['text'][i + 2].lower()):

            period = f"{d['text'][i]} {d['text'][i + 1]} {d['text'][i + 2]}"
            print("period", period)

            # limit number of rows that can be created
            if period_num > number_of_ppe:
                period_num = number_of_ppe

            df_row.loc[period_num, "Data (okres)"] = period
            period_num += 1

            # tariff #############################
            tariff = d['text'][i + 3]
            print("tariff", tariff)
            
            # limit number of rows that can be created
            if tariff_num > number_of_ppe:
                tariff_num = number_of_ppe
            
            df_row.loc[period_num - 1, "Taryfa"] = tariff
            tariff_num += 1

            # power from agreement ###################### - hashed because there is no value except kW
            # power = d['text'][i + 5]
            # print("power", power)

            ## limit number of rows that can be created
            # if power_num > number_of_ppe:
            #     power_num = number_of_ppe

            # df_row.loc[period_num - 1, "Moc umowna"] = power
            # power_num += 1

        # account
        if re.match('^[0-9]{2}$', d['text'][i]) and re.match('^\d\d\d\d', d['text'][i + 1]) and re.match('^\d\d\d\d', d['text'][i + 2]):
            account = f"{d['text'][i]} {d['text'][i + 1]} {d['text'][i + 2]} {d['text'][i + 3]} {d['text'][i + 4]} {d['text'][i + 5]} {d['text'][i + 6]}"
            account = account.replace("W", "").strip()
            print("account", account)

        # PPE ######################## '^PL\w?\w?\w?\w?\w?\w?[0-9]{2}'
        if re.match('^PL\w?\w?\w?\w?\w?\w?[0-9]{2}', d['text'][i]) or re.match('^GL\w?[0-9]{2}', d['text'][i]) or re.match('^590[0-9]{2}', d['text'][i]) or re.match('^480[0-9]{2}', d['text'][i]) or re.match('^§90[0-9]{2}', d['text'][i]):
            ppe = d['text'][i].replace("§", "5").replace("GL0", "GLO")

            if len(ppe.replace("_", "")) < 18:
                ppe +="_" + d['text'][i + 1]

                if len(ppe.replace("_", "")) < 18:
                    ppe +="_" + d['text'][i + 2]
                 
            ppe = ppe.replace("__", "_")

            if len(ppe) > 18 and ppe.startswith("59"):
                ppe = ppe.replace("_", "")

            if "GL" in ppe:
                ppe = ppe[:10]

            # limit number of rows that can be created
            if ppe_num > number_of_ppe:
                ppe_num = number_of_ppe

            print("ppe", ppe, "num", ppe_num)
            df_row.loc[period_num - 1, "PPE"] = ppe
            ppe_num += 1

        elif re.match('^PL_\w?\w?\w?\w?_', d['text'][i]):
            if len(d['text'][i]) == 8:
                ppe = d['text'][i] + d['text'][i + 1]

            if re.match('^[0-9]{2}', d['text'][i + 2]):
                ppe = f"{ppe}_{d['text'][i + 2]}"
            elif re.match('^_[0-9]{2}', d['text'][i + 2]):
                ppe = f"{ppe}{d['text'][i + 2]}"

            elif len(ppe) < 19:
                ppe += d['text'][i + 3]

            print("ppe", ppe, "num", ppe_num)
            df_row.loc[period_num - 1, "PPE"] = ppe
            ppe_num += 1

        elif re.match("^PL$", d['text'][i]) and re.match("\w?\w?\w?\w?", d['text'][i + 1]):
            print("SPR PPE", d['text'][i], d['text'][i + 1], d['text'][i + 2], d['text'][i + 3])
            if len(d['text'][i]) == 2:
                ppe = d['text'][i] + "_" + d['text'][i + 1]
                
                if len(ppe) == 7:
                    ppe += "_" + d['text'][i + 2]

                    if len(ppe) < 19:
                        ppe += d['text'][i + 3]

                        if len(ppe) < 19:
                            ppe += "_" + d['text'][i + 4]

                            if len(ppe) < 19:
                                ppe += "_" + d['text'][i + 5]

                elif len(ppe) < 19:
                    ppe += d['text'][i + 2]
                    
                    if len(ppe) < 19:
                        ppe += "_" + d['text'][i + 3]

            print("ppe", ppe, "num", ppe_num)
            df_row.loc[period_num - 1, "PPE"] = ppe
            ppe_num += 1

    # calculate number of days from receiveing the invoice till the deadline
    try:  
        if str(deadline)[3:5] == str(date)[3:5]:
            no_of_days = int(str(deadline)[-2:]) - int(str(date)[-2:]) - 1
        else:
            no_of_days = int(str(deadline)[-2:]) - int(str(date)[-2:]) - 1 + 30
        print("no of days", no_of_days)
    except:
        try:
            if str(deadline)[3:5] == str(df_row.loc[0, "Data wystawienia"])[3:5]:
                no_of_days = int(str(deadline)[-2:]) - int(str(df_row.loc[0, "Data wystawienia"])[-2:]) - 1
            else:
                no_of_days = int(str(deadline)[-2:]) - int(str(df_row.loc[0, "Data wystawienia"])[-2:]) - 1 + 30
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

    # variable
    # df_row.loc[df_row["PPE"].isnull(), "PPE"] = ppe
    df_row.loc[df_row["Data (okres)"].isnull(), "Data (okres)"] = period
    df_row.loc[df_row["Netto RAZEM"].isnull(), "Netto RAZEM"] = netto
    df_row.loc[df_row["Brutto RAZEM"].isnull(), "Brutto RAZEM"] = brutto 
    df_row.loc[df_row["Moc umowna"].isnull(), "Moc umowna"] = power
    df_row.loc[df_row["Taryfa"].isnull(), "Taryfa"] = tariff

    # constant - if empty
    try:
        df_row.loc[df_row["Nr Faktury"].isnull(), "Nr Faktury"] = df_row.loc[0, "Nr Faktury"]
        df_row.loc[df_row["Data wystawienia"].isnull(), "Data wystawienia"] = df_row.loc[0, "Data wystawienia"] 
        df_row.loc[df_row["NIP"].isnull(), "NIP"] = df_row.loc[0, "NIP"]
        df_row.loc[df_row["Termin płatności"].isnull(), "Termin płatności"] = df_row.loc[0, "Termin płatności"] 
        df_row.loc[df_row["Sm"].isnull(), "Sm"] = df_row.loc[0, "Sm"] 
        df_row.loc[df_row["Nota odsetkowa"].isnull(), "Nota odsetkowa"] = df_row.loc[0, "Nota odsetkowa"]
        df_row.loc[df_row["Nr konta"].isnull(), "Nr konta"] = df_row.loc[0, "Nr konta"]
        df_row.loc[df_row["Liczba dni na płatność"].isnull(), "Liczba dni na płatność"] = df_row.loc[0, "Liczba dni na płatność"] 
    except:
        pass

    return df_row, ppe_num, period_num, single_amounts, tariff_num, power_num, netto_num, brutto_num
