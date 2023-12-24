def deadline_processor(days, date, date_type):
    """
    Function to export deadline for payment based on date of the invoice and number of days for payment
    """
    days_30 = [4, 6, 9, 11]

    if date_type == "DDMMYYYY":
        dd = int(date[:2])
        mm = int(date[3:5])
        yyyy = int(date[6:])
        delim = date[2]
    elif date_type == "YYYYMMDD":
        dd = int(date[-2:])
        mm = int(date[5:7])
        yyyy = int(date[:4])
        delim = date[4]
        
    new_dd = dd + days

    if new_dd > 28:
        if mm == 2:
            return february(new_dd, delim, mm, yyyy)
        else:
            if mm in days_30:
                new_dd -= 30
                mm += 1

                if new_dd > 31:
                    new_dd -= 31
                    mm += 1
                    if mm == 13:
                        mm = 1
            
            else:                 
                new_dd -= 31     
                mm += 1
                if mm == 13:
                    mm = 1
                if mm != 2: 
                    if new_dd > 30:
                        new_dd -= 30
                        mm += 1
                        
                else:
                    return february(new_dd, delim, mm, yyyy)
                
    else:
        pass

    if mm < 10:
        mm = f"0{mm}"
    return f'{new_dd}{delim}{mm}{delim}{yyyy}'

def february(new_dd, delim, mm, yyyy):
    """
    Processing Febrary - check if this is the leap year and based on that add days to month
    """
    if leap_year(yyyy) == True:
        if new_dd == 29:
            pass
        
        else:
            new_dd -= 29
            mm += 1

            if new_dd > 31:
                new_dd -= 31
                mm += 1
        
    else:
        new_dd -= 28
        mm += 1

        if new_dd > 31:
            new_dd -= 31
            mm += 1

    if mm < 10:
        mm = f"0{mm}"
    return f'{new_dd}{delim}{mm}{delim}{yyyy}'

def leap_year(year):
    """
    Function to check whether a year is a leap year"""
    if year % 4 == 0:
        if year % 400 == 0:
            return True
        elif year % 100 == 0:
            return False
        else:
            return True
    else:
        return False
