'''
PURPOSE:
Quickly and easily generate a calendar
table with many columns of date dimensions
and metadata. Output to dataframe or CSV
to ingest into a database or for use in
an application like Excel or PowerBI.

WHAT KIND OF COLUMNS?
First of all, you'll find the usual dimensions:
o year number, month number, day number, yearmonth, yearquarter
o month name, day name, full date w ordinal suffix (e.g., "January 3rd, 2012")
o etc.
Additionally, some interesting and unique data elements include:
o holiday identification including Easter in any year (including pre-1583)
o moon phase identification
o sunrise/sunset for UTC as well as user-provided lat/lon coordinates
o length of daylight / darkness each day/evening

WHY?
Calendar tables have myriad uses.  Examples:
o PROCESS FLOW CONTROLS
  Check today's date.  If it is a Sunday or the
  last day of the month, then run a code block.
o SLICING DATA FOR ANALYSIS
  From the revenue dataset, show me all sales that
  fall between Thanksgiving and Christmas, and
  determine which days be best for best door-
  buster promotions
o FEATURES FOR MACHINE LEARNING MODELS
  Using a polynomial linear regression, predict
  the end-of-month sales using the month-to-date
  sales along with the knowledge of what percent
  through the month the data is, comparing
  to similar data from prior months.
o DATA VISUALIZATION
  In Microsoft PowerBI, or in Excel, or in Tableau,
  or in any tool... Use the workday of the month as
  the x-axis in a bar chart that shows the change
  in time clocked by employees on a given project
  in a given month
o AND MORE?
  Send me more examples to add!

NOTES:
o Example CSV output is provided in git repo
o When this code is run for a span of 5 years:
  + ~2,200 rows of data are created with ~100 columns (~220k cells)
  + the resulting CSV's filesize is about 1.4 MiB
  + the script takes 25 seconds on my raspberry pi 4B (very low specs)
  + code will run much faster on a modern laptop or desktop
o No special import statements needed besides standard Python
  3.7+ packages
o 32-bit OS and hardware may cause limitations in the ability
  to generate table data for years far in the future (2040)
  and throw "OverflowError: timestamp out of range for
  platform time_t"; no limitation has been observed on
  64-bit systems.  

AUTHOR:
This file was authored by TeneoPython01 with select
code excerpts leveraged from other authors where
noted.  In some cases the noted authors' code has
been materially modified.  In other cases it has
been used verbatim.  All other code is original.

ABOUT AUTHOR:
Contact me at https://github.com/TeneoPython01

TO DO:
o modularize codes with classes/functions
o use config file to set main params (start,
  end, holiday rules, lat/lon for localized
  data like moon phase, sunrise, etc.)
o add columns
  + percent through w / ym / y / etc
  + add season based on official start/end of seasons? (equinox, etc)
o fix bugs in the following:
  + night duration utc / night duration local

COLLABORATION?
Collaboration is sought and encouraged on this project!

LICENSE:
See license information in git repo.  The software
is released in the public domain as-is without any
warranty.  More details can be found in the
license file.

'''


import math
import pandas as pd
import numpy as np
from datetime import datetime
from datetime import timedelta
from dateutil import tz
import requests as r
import calendar

print(datetime.now())
print('calendar table process started')

#class to determine moon phases (approximate)
#class code from https://gist.github.com/mrrrk/
class Moon:

    # average length of a lunar cycle (Wikipedia)
    @staticmethod
    def lunar_month_days(): return 29.530588853

    @staticmethod
    def day_of_cycle(test_date=None):
        if test_date is None:
            #test_date = datetime.datetime.now()
            test_date = datetime.now()
        # the closer the base date (a known new-moon) is to the dates we're interested with, the better
        #base_new_moon = datetime.datetime(2017, 8, 21, 18, 30, 0)
        base_new_moon = datetime(2017, 8, 21, 18, 30, 0)
        days = (test_date - base_new_moon).total_seconds() / (24.0 * 60.0 * 60.0)
        return days % Moon.lunar_month_days()

    @staticmethod
    def illumination(day_of_cycle):
        # translate daily position as an angle between 0 and 360°
        angle = 2 * math.pi * day_of_cycle / Moon.lunar_month_days()
        # move and resize cosine curve so it represents waxing and waning as value from 0 to 1
        return (1 + (-math.cos(angle))) / 2.0

    # This isn't strictly accurate because new moon and full moon do not actually last for 1/8th of a cycle
    @staticmethod
    def phase(day_of_cycle):
        proportion = (day_of_cycle) / Moon.lunar_month_days()
        # add 0.5 to put value in 'middle' of phase
        #  - which might put it past end of array, so use bitwise AND to lop it off
        index = int(proportion * 8.0 + 0.5) & 7
        index_float = (proportion * 8.0 + 0.5)
        return {
             0: "New Moon",
             1: "Waxing Crescent",
             2: "First Quarter",
             3: "Waxing Gibbous",
             4: "Full Moon",
             5: "Waning Gibbous",
             6: "Last Quarter",
             7: "Waning Crescent"
        }[index], index, index_float


#class to raise expception for Sun class
class SunTimeException(Exception):

    def __init__(self, message):
        super(SunTimeException, self).__init__(message)

#class to find sunrise and sunset times by day and lat/lon location
class Sun:
    """
    Approximated calculation of sunrise and sunset datetimes. Adapted from:
    https://stackoverflow.com/questions/19615350/calculate-sunrise-and-sunset-times-for-a-given-gps-coordinate-within-postgresql
    """
    def __init__(self, lat, lon):
        self._lat = lat
        self._lon = lon

    def get_sunrise_time(self, date=None):
        """
        Calculate the sunrise time for given date.
        :param lat: Latitude
        :param lon: Longitude
        :param date: Reference date. Today if not provided.
        :return: UTC sunrise datetime
        :raises: SunTimeException when there is no sunrise and sunset on given location and date
        """
        date = datetime.date.today() if date is None else date
        sr = self._calc_sun_time(date, True)
        if sr is None:
            raise SunTimeException('The sun never rises on this location (on the specified date)')
        else:
            return sr

    def get_local_sunrise_time(self, date=None, local_time_zone=tz.tzlocal()):
        """
        Get sunrise time for local or custom time zone.
        :param date: Reference date. Today if not provided.
        :param local_time_zone: Local or custom time zone.
        :return: Local time zone sunrise datetime
        """
        date = datetime.date.today() if date is None else date
        sr = self._calc_sun_time(date, True)
        if sr is None:
            raise SunTimeException('The sun never rises on this location (on the specified date)')
        else:
            return sr.astimezone(local_time_zone)

    def get_sunset_time(self, date=None):
        """
        Calculate the sunset time for given date.
        :param lat: Latitude
        :param lon: Longitude
        :param date: Reference date. Today if not provided.
        :return: UTC sunset datetime
        :raises: SunTimeException when there is no sunrise and sunset on given location and date.
        """
        date = datetime.date.today() if date is None else date
        ss = self._calc_sun_time(date, False)
        if ss is None:
            raise SunTimeException('The sun never sets on this location (on the specified date)')
        else:
            return ss

    def get_local_sunset_time(self, date=None, local_time_zone=tz.tzlocal()):
        """
        Get sunset time for local or custom time zone.
        :param date: Reference date
        :param local_time_zone: Local or custom time zone.
        :return: Local time zone sunset datetime
        """
        date = datetime.date.today() if date is None else date
        ss = self._calc_sun_time(date, False)
        if ss is None:
            raise SunTimeException('The sun never sets on this location (on the specified date)')
        else:
            return ss.astimezone(local_time_zone)

    def _calc_sun_time(self, date, isRiseTime=True, zenith=90.8):
        """
        Calculate sunrise or sunset date.
        :param date: Reference date
        :param isRiseTime: True if you want to calculate sunrise time.
        :param zenith: Sun reference zenith
        :return: UTC sunset or sunrise datetime
        :raises: SunTimeException when there is no sunrise and sunset on given location and date
        """
        # isRiseTime == False, returns sunsetTime
        day = date.day
        month = date.month
        year = date.year

        TO_RAD = math.pi/180.0

        # 1. first calculate the day of the year
        N1 = math.floor(275 * month / 9)
        N2 = math.floor((month + 9) / 12)
        N3 = (1 + math.floor((year - 4 * math.floor(year / 4) + 2) / 3))
        N = N1 - (N2 * N3) + day - 30

        # 2. convert the longitude to hour value and calculate an approximate time
        lngHour = self._lon / 15

        if isRiseTime:
            t = N + ((6 - lngHour) / 24)
        else: #sunset
            t = N + ((18 - lngHour) / 24)

        # 3. calculate the Sun's mean anomaly
        M = (0.9856 * t) - 3.289

        # 4. calculate the Sun's true longitude
        L = M + (1.916 * math.sin(TO_RAD*M)) + (0.020 * math.sin(TO_RAD * 2 * M)) + 282.634
        L = self._force_range(L, 360 ) #NOTE: L adjusted into the range [0,360)

        # 5a. calculate the Sun's right ascension

        RA = (1/TO_RAD) * math.atan(0.91764 * math.tan(TO_RAD*L))
        RA = self._force_range(RA, 360 ) #NOTE: RA adjusted into the range [0,360)

        # 5b. right ascension value needs to be in the same quadrant as L
        Lquadrant  = (math.floor( L/90)) * 90
        RAquadrant = (math.floor(RA/90)) * 90
        RA = RA + (Lquadrant - RAquadrant)

        # 5c. right ascension value needs to be converted into hours
        RA = RA / 15

        # 6. calculate the Sun's declination
        sinDec = 0.39782 * math.sin(TO_RAD*L)
        cosDec = math.cos(math.asin(sinDec))

        # 7a. calculate the Sun's local hour angle
        cosH = (math.cos(TO_RAD*zenith) - (sinDec * math.sin(TO_RAD*self._lat))) / (cosDec * math.cos(TO_RAD*self._lat))

        if cosH > 1:
            return None     # The sun never rises on this location (on the specified date)
        if cosH < -1:
            return None     # The sun never sets on this location (on the specified date)

        # 7b. finish calculating H and convert into hours

        if isRiseTime:
            H = 360 - (1/TO_RAD) * math.acos(cosH)
        else: #setting
            H = (1/TO_RAD) * math.acos(cosH)

        H = H / 15

        #8. calculate local mean time of rising/setting
        T = H + RA - (0.06571 * t) - 6.622

        #9. adjust back to UTC
        UT = T - lngHour
        UT = self._force_range(UT, 24)   # UTC time in decimal format (e.g. 23.23)

        #10. Return
        hr = self._force_range(int(UT), 24)
        min = round((UT - int(UT))*60, 0)
        if min == 60:
            hr += 1
            min = 0

        #10. check corner case https://github.com/SatAgro/suntime/issues/1
        if hr == 24:
            hr = 0
            day += 1
            
            if day > calendar.monthrange(year, month)[1]:
                day = 1
                month += 1

                if month > 12:
                    month = 1
                    year += 1

        #return datetime.datetime(year, month, day, hr, int(min), tzinfo=tz.tzutc())
        return datetime(year, month, day, hr, int(min), tzinfo=tz.tzutc())

    @staticmethod
    def _force_range(v, max):
        # force v to be >= 0 and < max
        if v < 0:
            return v + max
        elif v >= max:
            return v - max

        return v



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




def identifyHoliday(dt, hf):
    if dt in hf['dt'].unique(): return 1



#used to find fields based on dow value
def mapDayOfWeekToOrdinalFieldName(dow_number):
    if   dow_number == 0: return 'mon'
    elif dow_number == 1: return 'tue'
    elif dow_number == 2: return 'wed'
    elif dow_number == 3: return 'thu'
    elif dow_number == 4: return 'fri'
    elif dow_number == 5: return 'sat'
    elif dow_number == 6: return 'sun'

"""
request = r.get('http://api.sunrise-sunset.org/json?lat=-32.7767&lng=96.7970&formatted=0')
timestring = r.html
utcsunrise = timestring[34:39]
utcsunset = timestring[71:76]
utcmorning = timestring[182:187]
utcnight = timestring[231:236]
"""

#print(utcsunrise, utcsunset, utcmorning, utcnight)


pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)



"""
def findHoliday(dt=None, month_dow_and_ct=None):
    if dt is None:
        pass
    else:
        pass

    return None
"""


df = pd.DataFrame()


#create base date range
start_dt='01-01-2020'
end_dt='12-31-2025'

df['dt'] = pd.date_range(start=start_dt, end=end_dt, freq='D')


#year as int
df['y'] = pd.DatetimeIndex(df['dt']).year

#month as int
df['m'] = pd.DatetimeIndex(df['dt']).month

#calendar day as int
df['d'] = pd.DatetimeIndex(df['dt']).day

#yearmonth as int
df['ym'] = df['y']*100 + df['m']

#date in yyyymmdd as int
df['dt_int'] = df['y']*10000 + df['m']*100 + df['d']

#day of week name (Monday, Tuesday, ...)
df['dow_name'] = df['dt'].dt.day_name()

#day of week number as int (Monday=0, Sunday=6)
df['dow'] = df['dt'].dt.dayofweek

#day of year number as int
df['doy'] = df['dt'].dt.dayofyear


#month name (January, February, ...)
df['m_name'] = df['dt'].dt.month_name()

#week number of year, using iso conventions (Monday is first DOW)
df['iso_week'] = df['dt'].dt.week

#normalized week number of year, using logic where first week (partial or full) is always 1
#and where Sunday is first DOW
#strftime"(%U" ) finds the week starting on Sunday; isoweek starts on sat
#strftime starts with week 0 in some cases; adjust to add 1 to all weeks for years with
#this situation so the first week of the year (partial or full) is always week 1.  note
#this differs from the isoweek approach above in addition to the starting DOW noted.
df['norm_week'] = df['dt'].apply(lambda x: x.strftime("%U")).astype(int)

df['norm_week_adj'] = np.where(
    (df['doy']==1) & (df['norm_week']==0),
    1,
    np.where(
        (df['doy']==1),
        0,
        np.nan
        )
    )

df['norm_week_adj'] = df[['y','norm_week_adj']].groupby('y')['norm_week_adj'].ffill()
df['norm_week_adj'] = df['norm_week_adj'].fillna(0)
df['norm_week'] = df['norm_week'] + df['norm_week_adj']
df['norm_week'] = df['norm_week'].astype(int)
df.drop('norm_week_adj', axis=1, inplace=True)

#quarter number of year
df['q'] = ((df['m']-1) // 3) + 1

#yearquarter as int
df['yq'] = df['y']*10+df['q']

#half number of year
df['h'] = ((df['q']-1) // 2) + 1

#yearhalf as int
df['yh'] = df['y']*10+df['h']

#yearmonth name
df['ym_name'] = df['m_name'] + ', ' + df['y'].apply(lambda x: str(x))

#ordinal dom suffix
df['dom_suffix'] = df['d'].apply(lambda x: ordinalSuffix(x))

#date name
df['dt_name'] = df['m_name'] + ' ' + df['d'].apply(lambda x: str(x)) + df['dom_suffix'] + ', ' + df['y'].apply(lambda x: str(x))

#is weekday (1=True, 0=False)
df['is_weekd'] = np.where(df['dow'].isin([0,1,2,3,4,]), 1, 0)

#weekdays in yearmonth through date
df['weekdom'] = df[['ym','is_weekd']].groupby('ym')['is_weekd'].cumsum()

#total weekdays in yearmonth
df['tot_weekd_in_mo'] = df.merge(
    df[['ym','is_weekd']].groupby('ym')['is_weekd'].sum().reset_index(),
    how='inner',
    on='ym',
    suffixes=('','_r')
    )['is_weekd_r']

#total caldays in yearmonth
df['tot_cald_in_mo'] = df.merge(
    df[['ym','dt_int']].groupby('ym')['dt_int'].count().reset_index(),
    how='inner',
    on='ym',
    suffixes=('','_r')
    )['dt_int_r']

#print(df_temp)

#weekdays in year through date
df['weekdoy'] = df[['y','is_weekd']].groupby('y')['is_weekd'].cumsum()

#total weekdays in year
df['tot_weekd_in_y'] = df.merge(
    df[['y','is_weekd']].groupby('y')['is_weekd'].sum().reset_index(),
    how='inner',
    on='y',
    suffixes=('','_r')
    )['is_weekd_r']

#total caldays in year
df['tot_cald_in_y'] = df.merge(
    df[['y','dt_int']].groupby('y')['dt_int'].count().reset_index(),
    how='inner',
    on='y',
    suffixes=('','_r')
    )['dt_int_r']

#is monday (1=True, 0=False)
df['is_dow_mon'] = (df['dow']==0).astype(int)

#is tuesday 1=True, 0=False)
df['is_dow_tue'] = (df['dow']==1).astype(int)

#is wednesday (1=True, 0=False)
df['is_dow_wed'] = (df['dow']==2).astype(int)

#is thursday 1=True, 0=False)
df['is_dow_thu'] = (df['dow']==3).astype(int)

#is friday 1=True, 0=False)
df['is_dow_fri'] = (df['dow']==4).astype(int)

#is saturday (1=True, 0=False)
df['is_dow_sat'] = (df['dow']==5).astype(int)

#is sunday (1=True, 0=False)
df['is_dow_sun'] = (df['dow']==6).astype(int)


#total mondays in yearmonth
field_to_sum = 'is_dow_mon'
df['tot_mon_in_ym'] = df.merge(
    df[['ym',field_to_sum]].groupby('ym')[field_to_sum].sum().reset_index(),
    how='inner',
    on='ym',
    suffixes=('','_r')
    )[field_to_sum+'_r']

#total mondays in yearmonth
field_to_sum = 'is_dow_tue'
df['tot_tue_in_ym'] = df.merge(
    df[['ym',field_to_sum]].groupby('ym')[field_to_sum].sum().reset_index(),
    how='inner',
    on='ym',
    suffixes=('','_r')
    )[field_to_sum+'_r']

#total mondays in yearmonth
field_to_sum = 'is_dow_wed'
df['tot_wed_in_ym'] = df.merge(
    df[['ym',field_to_sum]].groupby('ym')[field_to_sum].sum().reset_index(),
    how='inner',
    on='ym',
    suffixes=('','_r')
    )[field_to_sum+'_r']

#total mondays in yearmonth
field_to_sum = 'is_dow_thu'
df['tot_thu_in_ym'] = df.merge(
    df[['ym',field_to_sum]].groupby('ym')[field_to_sum].sum().reset_index(),
    how='inner',
    on='ym',
    suffixes=('','_r')
    )[field_to_sum+'_r']

#total mondays in yearmonth
field_to_sum = 'is_dow_fri'
df['tot_fri_in_ym'] = df.merge(
    df[['ym',field_to_sum]].groupby('ym')[field_to_sum].sum().reset_index(),
    how='inner',
    on='ym',
    suffixes=('','_r')
    )[field_to_sum+'_r']

#total mondays in yearmonth
field_to_sum = 'is_dow_sat'
df['tot_sat_in_ym'] = df.merge(
    df[['ym',field_to_sum]].groupby('ym')[field_to_sum].sum().reset_index(),
    how='inner',
    on='ym',
    suffixes=('','_r')
    )[field_to_sum+'_r']

#total mondays in yearmonth
field_to_sum = 'is_dow_sun'
df['tot_sun_in_ym'] = df.merge(
    df[['ym',field_to_sum]].groupby('ym')[field_to_sum].sum().reset_index(),
    how='inner',
    on='ym',
    suffixes=('','_r')
    )[field_to_sum+'_r']




#total mondays in yearmonth
field_to_sum = 'is_dow_mon'
df['tot_mon_in_y'] = df.merge(
    df[['y',field_to_sum]].groupby('y')[field_to_sum].sum().reset_index(),
    how='inner',
    on='y',
    suffixes=('','_r')
    )[field_to_sum+'_r']

#total mondays in yearmonth
field_to_sum = 'is_dow_tue'
df['tot_tue_in_y'] = df.merge(
    df[['y',field_to_sum]].groupby('y')[field_to_sum].sum().reset_index(),
    how='inner',
    on='y',
    suffixes=('','_r')
    )[field_to_sum+'_r']

#total mondays in yearmonth
field_to_sum = 'is_dow_wed'
df['tot_wed_in_y'] = df.merge(
    df[['y',field_to_sum]].groupby('y')[field_to_sum].sum().reset_index(),
    how='inner',
    on='y',
    suffixes=('','_r')
    )[field_to_sum+'_r']

#total mondays in yearmonth
field_to_sum = 'is_dow_thu'
df['tot_thu_in_y'] = df.merge(
    df[['y',field_to_sum]].groupby('y')[field_to_sum].sum().reset_index(),
    how='inner',
    on='y',
    suffixes=('','_r')
    )[field_to_sum+'_r']

#total mondays in yearmonth
field_to_sum = 'is_dow_fri'
df['tot_fri_in_y'] = df.merge(
    df[['y',field_to_sum]].groupby('y')[field_to_sum].sum().reset_index(),
    how='inner',
    on='y',
    suffixes=('','_r')
    )[field_to_sum+'_r']

#total mondays in yearmonth
field_to_sum = 'is_dow_sat'
df['tot_sat_in_y'] = df.merge(
    df[['y',field_to_sum]].groupby('y')[field_to_sum].sum().reset_index(),
    how='inner',
    on='y',
    suffixes=('','_r')
    )[field_to_sum+'_r']

#total mondays in yearmonth
field_to_sum = 'is_dow_sun'
df['tot_sun_in_y'] = df.merge(
    df[['y',field_to_sum]].groupby('y')[field_to_sum].sum().reset_index(),
    how='inner',
    on='y',
    suffixes=('','_r')
    )[field_to_sum+'_r']




#mondays of yearmonth through date
df['dow_mon_om'] = df[['ym','is_dow_mon']].groupby('ym')['is_dow_mon'].cumsum()

#tuesdays of yearmonth through date
df['dow_tue_om'] = df[['ym','is_dow_tue']].groupby('ym')['is_dow_tue'].cumsum()

#wednesdays of yearmonth through date
df['dow_wed_om'] = df[['ym','is_dow_wed']].groupby('ym')['is_dow_wed'].cumsum()

#thursdays of yearmonth through date
df['dow_thu_om'] = df[['ym','is_dow_thu']].groupby('ym')['is_dow_thu'].cumsum()

#fridays of yearmonth through date
df['dow_fri_om'] = df[['ym','is_dow_fri']].groupby('ym')['is_dow_fri'].cumsum()

#saturdays of yearmonth through date
df['dow_sat_om'] = df[['ym','is_dow_sat']].groupby('ym')['is_dow_sat'].cumsum()

#sundays of yearmonth through date
df['dow_sun_om'] = df[['ym','is_dow_sun']].groupby('ym')['is_dow_sun'].cumsum()




#mondays of year through date
df['dow_mon_oy'] = df[['y','is_dow_mon']].groupby('y')['is_dow_mon'].cumsum()

#tuesdays of year through date
df['dow_tue_oy'] = df[['y','is_dow_tue']].groupby('y')['is_dow_tue'].cumsum()

#wednesdays of year through date
df['dow_wed_oy'] = df[['y','is_dow_wed']].groupby('y')['is_dow_wed'].cumsum()

#thursdays of year through date
df['dow_thu_oy'] = df[['y','is_dow_thu']].groupby('y')['is_dow_thu'].cumsum()

#fridays of year through date
df['dow_fri_oy'] = df[['y','is_dow_fri']].groupby('y')['is_dow_fri'].cumsum()

#saturdays of year through date
df['dow_sat_oy'] = df[['y','is_dow_sat']].groupby('y')['is_dow_sat'].cumsum()

#sundays of year through date
df['dow_sun_oy'] = df[['y','is_dow_sun']].groupby('y')['is_dow_sun'].cumsum()

#dow of month based on dow: first find the appropriate col to ref, then grab its value
df['dow_om'] = 'dow_' + df['dow'].apply(lambda x: mapDayOfWeekToOrdinalFieldName(x)) + '_om'
df['dow_om'] = df[df['dow_om'].values]

#is last dow of yearmonth based on dow:
dimension = 'ym'
field_to_take = 'dow_om'
df['dow_om_max'] = df.merge(
    df[[dimension,field_to_take]].groupby(dimension)[field_to_take].max().reset_index(),
    how='inner',
    on=dimension,
    suffixes=('','_r')
    )[field_to_take+'_r']


#dow of year based on dow: first find the appropriate col to ref, then grab its value
df['dow_oy'] = 'dow_' + df['dow'].apply(lambda x: mapDayOfWeekToOrdinalFieldName(x)) + '_oy'
df['dow_oy'] = df[df['dow_oy'].values]

#is holiday (and if so, what is the holiday name)
#first, identify rules for holidays
#second, iterate through all rows of the calendar table to find dates that match the rules
#third, where they match, mark them as a holiday and record the name of the holiday
df_standard_holidays = pd.DataFrame(
    columns = ['lit_m','lit_d','rel_m','rel_dow','rel_occur','rel_last','is_literal','holiday_name'],
    data = [
        [ 1, 1,-1,-1,-1,-1, 1, "New Year's Day"], #jan 1
        [-1,-1, 5, 0,-1, 1, 0, 'Memorial Day'], # last monday in may
        [ 7, 4,-1,-1,-1,-1, 1, 'Fourth of July'], #jul 4
        [-1,-1, 9, 0, 1, 0, 0, 'Labor Day'], # 1st monday in sep
        [-1,-1,11, 3, 4, 0, 0, 'Thanksgiving'], #4th thursday in nov
        [12,25,-1,-1,-1,-1, 1, 'Christmas Day'] #dec 25
        ]
    )

index_list = []

for i, df_row in df.iterrows():
    for j, hf_row in df_standard_holidays.iterrows():

        #find holidays based on a set literal month and day (e.g., "Christmas Day is always on December 25th"
        if (hf_row['is_literal'] == 1) & (df_row['m'] == hf_row['lit_m']) & (df_row['d'] == hf_row['lit_d']):
            index_list.append((i, hf_row['holiday_name']))

        #find holidays based on a relative month and day (e.g., "Thanksgiving is the 4th Thursday in November")
        if (hf_row['is_literal'] == 0) & (df_row['m'] == hf_row['rel_m']) & (df_row['dow'] == hf_row['rel_dow']) & (df_row['dow_om'] == hf_row['rel_occur']):
            index_list.append((i, hf_row['holiday_name']))

        #find holidays based on being the last dow in a month (e.g., "Memorial Day is the last Monday in May")
        if (hf_row['is_literal'] == 0) & \
        (hf_row['rel_last'] == 1) & \
        (df_row['m'] == hf_row['rel_m']) & \
        (df_row['dow'] == hf_row['rel_dow']) & \
        (df_row['dow_om'] == df_row['dow_om_max']):
            index_list.append((i, hf_row['holiday_name']))

        #find Easter Sunday
        if (findEaster(df_row['y'])[0:3] == (df_row['y'], df_row['m'], df_row['d'])):
            index_list.append((i, 'Easter Sunday'))
                
df['is_holiday']=0
df['holiday']=''
for i in index_list:
    df['is_holiday'].at[i[0]] = 1
    df['holiday'].at[i[0]] = i[1]

#is day Leap Year day
df['is_d_leapyr'] = np.where(
    (df['m']==2) & (df['d']==29),
    1,
    0
    )

#is yearmonth a Feb that contains Leap Year day
df['is_ym_leapyr'] = df.merge(
    df[['ym','is_d_leapyr']].groupby('ym')['is_d_leapyr'].sum().reset_index(),
    how='inner',
    on='ym',
    suffixes=('','_r')
    )['is_d_leapyr_r']

#is year a leap year
df['is_y_leapyr'] = df.merge(
    df[['y','is_d_leapyr']].groupby('y')['is_d_leapyr'].sum().reset_index(),
    how='inner',
    on='y',
    suffixes=('','_r')
    )['is_d_leapyr_r']

#first day of month datetime
dimension = 'ym'
field_to_take = 'dt'
df['first_dom_dt'] = df.merge(
    df[[dimension,field_to_take]].groupby(dimension)[field_to_take].min().reset_index(),
    how='inner',
    on=dimension,
    suffixes=('','_r')
    )[field_to_take+'_r']

#first day of month int
dimension = 'ym'
field_to_take = 'dt_int'
df['first_dom_int'] = df.merge(
    df[[dimension,field_to_take]].groupby(dimension)[field_to_take].min().reset_index(),
    how='inner',
    on=dimension,
    suffixes=('','_r')
    )[field_to_take+'_r']

#last day of month datetime
dimension = 'ym'
field_to_take = 'dt'
df['last_dom_dt'] = df.merge(
    df[[dimension,field_to_take]].groupby(dimension)[field_to_take].max().reset_index(),
    how='inner',
    on=dimension,
    suffixes=('','_r')
    )[field_to_take+'_r']

#last day of month datetime
dimension = 'ym'
field_to_take = 'dt_int'
df['last_dom_int'] = df.merge(
    df[[dimension,field_to_take]].groupby(dimension)[field_to_take].max().reset_index(),
    how='inner',
    on=dimension,
    suffixes=('','_r')
    )[field_to_take+'_r']

#first day of yearquarter datetime
dimension = 'yq'
field_to_take = 'dt'
df['first_doyq_dt'] = df.merge(
    df[[dimension,field_to_take]].groupby(dimension)[field_to_take].min().reset_index(),
    how='inner',
    on=dimension,
    suffixes=('','_r')
    )[field_to_take+'_r']

#first day of yearquarter int
dimension = 'yq'
field_to_take = 'dt_int'
df['first_doyq_int'] = df.merge(
    df[[dimension,field_to_take]].groupby(dimension)[field_to_take].min().reset_index(),
    how='inner',
    on=dimension,
    suffixes=('','_r')
    )[field_to_take+'_r']

#last day of yearquarter datetime
dimension = 'yq'
field_to_take = 'dt'
df['last_doyq_dt'] = df.merge(
    df[[dimension,field_to_take]].groupby(dimension)[field_to_take].max().reset_index(),
    how='inner',
    on=dimension,
    suffixes=('','_r')
    )[field_to_take+'_r']

#last day of yearquarter datetime
dimension = 'yq'
field_to_take = 'dt_int'
df['last_doyq_int'] = df.merge(
    df[[dimension,field_to_take]].groupby(dimension)[field_to_take].max().reset_index(),
    how='inner',
    on=dimension,
    suffixes=('','_r')
    )[field_to_take+'_r']

#first day of yearhalf datetime
dimension = 'yh'
field_to_take = 'dt'
df['first_doyh_dt'] = df.merge(
    df[[dimension,field_to_take]].groupby(dimension)[field_to_take].min().reset_index(),
    how='inner',
    on=dimension,
    suffixes=('','_r')
    )[field_to_take+'_r']

#first day of yearhalf int
dimension = 'yh'
field_to_take = 'dt_int'
df['first_doyh_int'] = df.merge(
    df[[dimension,field_to_take]].groupby(dimension)[field_to_take].min().reset_index(),
    how='inner',
    on=dimension,
    suffixes=('','_r')
    )[field_to_take+'_r']

#last day of yearhalf datetime
dimension = 'yh'
field_to_take = 'dt'
df['last_doyh_dt'] = df.merge(
    df[[dimension,field_to_take]].groupby(dimension)[field_to_take].max().reset_index(),
    how='inner',
    on=dimension,
    suffixes=('','_r')
    )[field_to_take+'_r']

#last day of yearhalf datetime
dimension = 'yh'
field_to_take = 'dt_int'
df['last_doyh_int'] = df.merge(
    df[[dimension,field_to_take]].groupby(dimension)[field_to_take].max().reset_index(),
    how='inner',
    on=dimension,
    suffixes=('','_r')
    )[field_to_take+'_r']

#first day of year datetime
dimension = 'y'
field_to_take = 'dt'
df['first_doy_dt'] = df.merge(
    df[[dimension,field_to_take]].groupby(dimension)[field_to_take].min().reset_index(),
    how='inner',
    on=dimension,
    suffixes=('','_r')
    )[field_to_take+'_r']

#first day of year int
dimension = 'y'
field_to_take = 'dt_int'
df['first_doy_int'] = df.merge(
    df[[dimension,field_to_take]].groupby(dimension)[field_to_take].min().reset_index(),
    how='inner',
    on=dimension,
    suffixes=('','_r')
    )[field_to_take+'_r']

#last day of year datetime
dimension = 'y'
field_to_take = 'dt'
df['last_doy_dt'] = df.merge(
    df[[dimension,field_to_take]].groupby(dimension)[field_to_take].max().reset_index(),
    how='inner',
    on=dimension,
    suffixes=('','_r')
    )[field_to_take+'_r']

#last day of year datetime
dimension = 'y'
field_to_take = 'dt_int'
df['last_doy_int'] = df.merge(
    df[[dimension,field_to_take]].groupby(dimension)[field_to_take].max().reset_index(),
    how='inner',
    on=dimension,
    suffixes=('','_r')
    )[field_to_take+'_r']

#moon phase name (approximate)
moon = Moon()
df['moon_phase_name'] = df['dt'].apply(lambda x: moon.phase(moon.day_of_cycle(x))[0])

#moon phase index number as int (approximate)
df['moon_phase_index_int'] = df['dt'].apply(lambda x: moon.phase(moon.day_of_cycle(x))[1])

#moon phase index number as float (approximate)
df['moon_phase_index_full'] = df['dt'].apply(lambda x: moon.phase(moon.day_of_cycle(x))[2])

#moon illumination percentage (approximate)
df['moon_illum_pct'] = df['dt'].apply(lambda x: moon.illumination(moon.day_of_cycle(x)))

#set locale; dallas, tx is lat 32.7, lon -96.8
cal_lat = 32.7
cal_lon = -96.8
sun = Sun(lat=cal_lat, lon=cal_lon)

#sunrise UTC time
df['sunrise_utc'] = df['dt'].apply(lambda x: sun.get_sunrise_time(date = x))
#sunset UTC time
df['sunset_utc'] = df['dt'].apply(lambda x: sun.get_sunset_time(date = x))
#sunlight duration utc
df['sun_duration_utc'] = df['sunset_utc'] - df['sunrise_utc']
#darkness duration utc (midnight to sunrise plus sunset to following midnight)
df['dark_duration_utc'] = timedelta(hours=24) - df['sun_duration_utc']
#night duration utc (time from sunset on date until sunrise on following day)

#sunrise local time
df['sunrise_local'] = df['dt'].apply(lambda x: sun.get_local_sunrise_time(date = x))
#sunset local time
df['sunset_local'] = df['dt'].apply(lambda x: sun.get_local_sunset_time(date = x))
#sunlight duration local
df['sun_duration_local'] = df['sunset_local'] - df['sunrise_local']
#darkness duration local (midnight to sunrise plus sunset to following midnight)
df['dark_duration_local'] = timedelta(hours=24) - df['sun_duration_local']


df.to_csv('./temp_csv.csv')

print(datetime.now())
print('calendar table process completed')
