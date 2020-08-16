#return the suffix of the ordinal day number. e.g., the "st" in "31st day of March"
#only works for two-digit or smaller integers
#only uses the whole number portion of any number passed (won't account for decimals)
def ordinalSuffix(number):

    #truncate any decimals, and use only last 2 digits of resutling integer
    number = number // 1 % 100

    if ( (number % 10 == 1) & (number // 10 != 1) ):
        suffix = 'st'
    elif ( (number % 10 == 2) & (number // 10 != 1) ):
        suffix = 'nd'
    elif ( (number % 10 == 3) & (number // 10 != 1) ):
        suffix = 'rd'
    else:
        suffix = 'th'

    return suffix

#used to find fields based on dow value
def mapDayOfWeekToOrdinalFieldName(dow_number):
    if   dow_number == 0: return 'mon'
    elif dow_number == 1: return 'tue'
    elif dow_number == 2: return 'wed'
    elif dow_number == 3: return 'thu'
    elif dow_number == 4: return 'fri'
    elif dow_number == 5: return 'sat'
    elif dow_number == 6: return 'sun'
