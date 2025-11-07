##

import math
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil import tz

#find date of easter for given year; not accurate for year 1582 or earlier.
#compared output of 2000-2029 to known list of gregorian (western) Easter
#dates and output was accurate
#written with help from https://www.linuxtopia.org/online_books/programming_books/python_programming/python_ch38.html
def findEasterAfterYear1582(year):

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
def findEasterBeforeYear1583(year):

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
def findEaster(year):
    if year < 1583:
        return findEasterBeforeYear1583(year)
    else:
        return findEasterAfterYear1582(year)


#def identifyHoliday(dt, hf):
#    if dt in hf['dt'].unique(): return 1

class Holiday():

    def __init__(self):
        """
        Create the class object for adding holiday rules
        """

        self.holiday_col_list = ['lit_m',
                                 'lit_d',
                                 'rel_m',
                                 'rel_dow',
                                 'rel_occur',
                                 'rel_last',
                                 'is_easter',
                                 'is_lit_rule',
                                 'holiday_name']
        self.holiday_rule_list = []
        

    def addHolidayByRule(self,
                       literal_month=-1,
                       literal_d=-1,
                       relative_month=-1,
                       relative_dow=-1,
                       relative_occurrence=-1,
                       relative_is_last_occurrence=-1,
                       holiday_name=''):
        """
        Adds a holiday rule to the class object's rule list
        
        :param literal_month:  month number (if literal rule)
        :param literal_d:      calendar day number (if literal rule)
        :param relative_month: month number (if relative rule)
        :param relative_dow:   day of week number (if relative rule)
        :param relative_occurrence: occurrence of dow within yearmonth (if relative rule)
        :param relative_is_last_occurrence: is the holiday on the last occurrence of the dow within the ym? (1=yes, 0=no; only for relative rule)
        :param holiday_name:   name of holiday

        :usage: addHolidayByRule(literal_month=1, literal_day=1, holiday_name='New Years Day')
        :usage: addHolidayByRule(relative_month=5, relative_dow=0, relative_is_last_occurrence=1, holiday_name='Memorial Day')
        :usage: addHolidayByRule(relative_month=11, relative_dow=3, relative_occurrence=4, holiday_name='Thanksgiving')
        """
        
        #set flag to define whether the rule being added is
        #based on a literal month/day (flag=1) or based on
        #a relative occurrence (flag=0)
        if (literal_month > 0) & (literal_d >= 0):
            is_literal_rule = 1
        else:
            is_literal_rule = 0

        #this isn't the method to add easter to the rule frame,
        #so all rules added via this method will set easter to
        #the off position
        easter=-1

        self.holiday_rule_list.append([literal_month,
                                       literal_d,
                                       relative_month,
                                       relative_dow,
                                       relative_occurrence,
                                       relative_is_last_occurrence,
                                       easter,
                                       is_literal_rule,
                                       holiday_name]
                                      )

    def addEaster(self):
        """
        Adds Easter to the holiday rule list
        """

        self.holiday_rule_list.append([-1, #literal_month (OFF)
                                       -1, #literal_d (OFF)
                                       -1, #relative_month (OFF)
                                       -1, #relative_dow (OFF)
                                       -1, #relative_occurrence (OFF)
                                       -1, #relative_is_last_occurrence (OFF)
                                       1,  #easter (ON)
                                       -1, #is_literal_rule (OFF)
                                       'Easter'] #holiday_name
                                      )

        
    def createHolidayFrame(self):
        """
        Convert the holiday rules list into a pandas dataframe
        """
        
        self.holiday_df = pd.DataFrame(columns = self.holiday_col_list,
                                       data = self.holiday_rule_list
                                       )

    def identifyHolidays(self, cal_df):
        """
        Identify any dates on the calendar table that are holiday
        that match the holiday rule list.

        :param cal_df: a calendar table dataframe with a very specific format.
        :returns: a calendar table dataframe with new holiday columns added
        """

        index_list = []

        for i, df_row in cal_df.iterrows():
            for j, hf_row in self.holiday_df.iterrows():

                #find holidays based on a set literal month and day (e.g., "Christmas Day is always on December 25th"
                if (hf_row['is_lit_rule'] == 1) & \
                (df_row['month'] == hf_row['lit_m']) & \
                (df_row['day'] == hf_row['lit_d']):
                    index_list.append((i, hf_row['holiday_name']))

                #find holidays based on a relative month and day (e.g., "Thanksgiving is the 4th Thursday in November")
                if (hf_row['is_lit_rule'] == 0) & \
                (df_row['month'] == hf_row['rel_m']) & \
                (df_row['dow'] == hf_row['rel_dow']) & \
                (df_row['dow_om'] == hf_row['rel_occur']):
                    index_list.append((i, hf_row['holiday_name']))

                #find holidays based on being the last dow in a month (e.g., "Memorial Day is the last Monday in May")
                if (hf_row['is_lit_rule'] == 0) & \
                (hf_row['rel_last'] == 1) & \
                (df_row['month'] == hf_row['rel_m']) & \
                (df_row['dow'] == hf_row['rel_dow']) & \
                (df_row['dow_om'] == df_row['dow_om_max']):
                    index_list.append((i, hf_row['holiday_name']))

                #find Easter Sunday
                if (hf_row['is_easter'] == 1) & \
                (findEaster(df_row['year'])[0:3] == (df_row['year'], df_row['month'], df_row['day'])):
                    index_list.append((i, 'Easter Sunday'))

        cal_df['is_holiday']=0
        cal_df['holiday']=''

        for i in index_list:
            cal_df['is_holiday'].at[i[0]] = 1
            cal_df['holiday'].at[i[0]] = i[1]

        return cal_df
