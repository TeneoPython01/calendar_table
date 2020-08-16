##

import math
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil import tz

class Holiday:

    #find date of easter for given year; not accurate for year 1582 or earlier.
    #compared output of 2000-2029 to known list of gregorian (western) Easter
    #dates and output was accurate
    #written with help from https://www.linuxtopia.org/online_books/programming_books/python_programming/python_ch38.html
    def findEasterAfterYear1582(self, year):

        calculation_method = '1583 or later'

        golden_number = (year % 19) + 1
        century = (year // 100) + 1 #not technically correct, but this is how the Easter calculation works; counts years that are evenly divisible by 100 as in the prior century
        corrections_dropped_leap_years = ( (3 * century) // 4) - 12 #e.g. in 1900 Leap Year is dropped
        corrections_moon = ( ( (8 * century) + 5 ) // 25 ) - 5
        sunday = ( (5 * year) // 4 ) - corrections_dropped_leap_years - 10
        epact = ((11 * golden_number) + 20 + corrections_moon - corrections_dropped_leap_years) % 30

        #adjust for special circumstances
        if ( (epact == 25) & (golden_number > 11) ) | (epact == 24):
            epact = epact + 1

        full_moon = 44 - epact

        #Easter is the “first Sunday following the first full moon which occurs on
        #or after March 21.” note -- calendar moon, rather than lunar moon!
        if (full_moon < 21):
            full_moon = full_moon + 30

        upcoming_sunday = full_moon + 7 - ( (sunday + full_moon) % 7 )

        if (upcoming_sunday > 31):
            date = (year, 4, upcoming_sunday - 31, calculation_method)
        else:
            date = (year, 3, upcoming_sunday, calculation_method)

        #date is tuple with format (year, month, day, calculation_method)
        return date

    #find date of easter for given year; only accurate for year 1582 or earlier.
    #compared output of 1501-1503 to known list of gregorian (western) Easter
    #dates and output was accurate
    #written with help from https://www.linuxtopia.org/online_books/programming_books/python_programming/python_ch38.html
    def findEasterBeforeYear1583(self, year):

        calculation_method = '1582 or earlier'

        a = year % 19
        b = year // 100
        c = year % 100
        d = b // 4
        e = b % 4
        g = ( (8 * b) + 13) // 25
        h = ( (19 * a) + b - d - g + 15) % 30
        m = ( a + (11 * h) ) // 319 
        i = c // 4
        k = c % 4
        f = ( (2 * e) + (2 * i) - k - h + m + 32 ) % 7
        n = (h - m + f + 90) // 25
        p = (h - m + f + n + 19) % 32

        date = (year, n, p, calculation_method)

        #date is tuple in format (year, month, day, calulation_method)
        return date

    #comprehensive function to find any easter regardless of year
    #returns a tuple in format (year, month, day, calculation_method)
    def findEaster(self, year):
        if year < 1583:
            return self.findEasterBeforeYear1583(year)
        else:
            return self.findEasterAfterYear1582(year)


    #def identifyHoliday(self, dt, hf):
    #    if dt in hf['dt'].unique(): return 1
