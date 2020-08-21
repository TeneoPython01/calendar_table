'''
PURPOSE:
Quickly and easily generate a calendar table with many columns of date dimensions
and metadata. Output to dataframe or CSV to ingest into a database or for use in
an application like Excel or PowerBI. See readme.md in git repo for more info @
https://github.com/TeneoPython01
'''

import math
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil import tz
from udfs import moon, sun, holiday, date_udfs, df_udfs, html_udfs, misc_udfs
from docs import create_docs

#set pandas display options for printing to screen
pd.set_option('display.max_rows', 1000) #allow printing lots of rows to screen
pd.set_option('display.max_columns', 1000) #allow printsin lots of cols to screen
pd.set_option('display.width', 1000) #don't wrap lots of columns

#print metadata about the script and the user to start the script
misc_udfs.printHeader()

#set important user-defined variables
#TODO: set these via a config.ini file
start_dt='01-01-2020'
end_dt='12-31-2025'
cal_lat = 32.7  #set locale latitude;  dallas, tx is lat 32.7, lon -96.8
cal_lon = -96.8 #set locale longitude; dallas, tx is lat 32.7, lon -96.8

#start the process
misc_udfs.tprint('calendar table process started for ' + start_dt + ' through ' + end_dt + ' inclusive')

df = pd.DataFrame()
#create base date range

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
#TODO: modularize this code
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
df['dom_suffix'] = df['d'].apply(lambda x: date_udfs.ordinalSuffix(x))

#date name
df['dt_name'] = df['m_name'] + ' ' + df['d'].apply(lambda x: str(x)) + df['dom_suffix'] + ', ' + df['y'].apply(lambda x: str(x))

#is weekday (1=True, 0=False)
df['is_weekd'] = np.where(df['dow'].isin([0,1,2,3,4,]), 1, 0)

#weekdays in yearmonth through date
df['weekdom'] = df[['ym','is_weekd']].groupby('ym')['is_weekd'].cumsum()

#total weekdays in yearmonth
df = df_udfs.addColumnFromGroupbyOperation(df, 'tot_weekd_in_mo', 'ym', 'is_weekd', 'sum')

#weekdays remaining in ym
df['weekd_remain_ym'] = df['tot_weekd_in_mo'] - df['weekdom']

#total caldays in yearmonth
df = df_udfs.addColumnFromGroupbyOperation(df, 'tot_cald_in_mo', 'ym', 'dt_int', 'count')

#calendar days remaining in yearmonth
df['cald_remain_ym'] = df['tot_cald_in_mo'] - df['d']

#weekdays in year through date
df['weekdoy'] = df[['y','is_weekd']].groupby('y')['is_weekd'].cumsum()

#total weekdays in year
df = df_udfs.addColumnFromGroupbyOperation(df, 'tot_weekd_in_y', 'y', 'is_weekd', 'sum')

#weekdays remaining in year
df['weekd_remain_y'] = df['tot_weekd_in_y'] - df['weekdoy']

#total caldays in year
df = df_udfs.addColumnFromGroupbyOperation(df, 'tot_cald_in_y', 'y', 'dt_int', 'count')

#calendar days remaining in year
df['cald_remain_y'] = df['tot_cald_in_y'] - df['doy']

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
df = df_udfs.addColumnFromGroupbyOperation(df, 'tot_mon_in_ym', 'ym', 'is_dow_mon', 'sum')

#total mondays in yearmonth
df = df_udfs.addColumnFromGroupbyOperation(df, 'tot_tue_in_ym', 'ym', 'is_dow_tue', 'sum')

#total mondays in yearmonth
df = df_udfs.addColumnFromGroupbyOperation(df, 'tot_wed_in_ym', 'ym', 'is_dow_wed', 'sum')

#total mondays in yearmonth
df = df_udfs.addColumnFromGroupbyOperation(df, 'tot_thu_in_ym', 'ym', 'is_dow_thu', 'sum')

#total mondays in yearmonth
df = df_udfs.addColumnFromGroupbyOperation(df, 'tot_fri_in_ym', 'ym', 'is_dow_fri', 'sum')

#total mondays in yearmonth
df = df_udfs.addColumnFromGroupbyOperation(df, 'tot_sat_in_ym', 'ym', 'is_dow_sat', 'sum')

#total mondays in yearmonth
df = df_udfs.addColumnFromGroupbyOperation(df, 'tot_sun_in_ym', 'ym', 'is_dow_sun', 'sum')

#total mondays in yearmonth
df = df_udfs.addColumnFromGroupbyOperation(df, 'tot_mon_in_y', 'y', 'is_dow_mon', 'sum')

#total mondays in yearmonth
df = df_udfs.addColumnFromGroupbyOperation(df, 'tot_tue_in_y', 'y', 'is_dow_tue', 'sum')

#total mondays in yearmonth
df = df_udfs.addColumnFromGroupbyOperation(df, 'tot_wed_in_y', 'y', 'is_dow_wed', 'sum')

#total mondays in yearmonth
df = df_udfs.addColumnFromGroupbyOperation(df, 'tot_thu_in_y', 'y', 'is_dow_thu', 'sum')

#total mondays in yearmonth
df = df_udfs.addColumnFromGroupbyOperation(df, 'tot_fri_in_y', 'y', 'is_dow_fri', 'sum')

#total mondays in yearmonth
df = df_udfs.addColumnFromGroupbyOperation(df, 'tot_sat_in_y', 'y', 'is_dow_sat', 'sum')

#total mondays in yearmonth
df = df_udfs.addColumnFromGroupbyOperation(df, 'tot_sun_in_y', 'y', 'is_dow_sun', 'sum')

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
df['dow_om'] = 'dow_' + df['dow'].apply(lambda x: date_udfs.mapDayOfWeekToOrdinalFieldName(x)) + '_om'
df['dow_om'] = df[df['dow_om'].values]

#is last dow of yearmonth based on dow:
df = df_udfs.addColumnFromGroupbyOperation(df, 'dow_om_max', 'ym', 'dow_om', 'max')

#dow of year based on dow: first find the appropriate col to ref, then grab its value
df['dow_oy'] = 'dow_' + df['dow'].apply(lambda x: date_udfs.mapDayOfWeekToOrdinalFieldName(x)) + '_oy'
df['dow_oy'] = df[df['dow_oy'].values]

#add the rules for holidays that are not workdays in the calendar table
holiday_obj = holiday.Holiday()
holiday_obj.addHolidayByRule(literal_month=1, literal_d=1, holiday_name="New Year's Day")
holiday_obj.addHolidayByRule(relative_month=5, relative_dow=0, relative_is_last_occurrence=1, holiday_name="Memorial Day")
holiday_obj.addHolidayByRule(literal_month=7, literal_d=4, holiday_name="Fourth of July")
holiday_obj.addHolidayByRule(relative_month=9, relative_dow=0, relative_occurrence=1, holiday_name="Labor Day")
holiday_obj.addHolidayByRule(relative_month=11, relative_dow=3, relative_occurrence=4, holiday_name="Thanksgiving")
holiday_obj.addHolidayByRule(literal_month=12, literal_d=25, holiday_name="Christmas Day")
holiday_obj.addEaster()
holiday_obj.createHolidayFrame()

#is holiday and holiday name
df = holiday_obj.identifyHolidays(df)

#is workday
df['is_workd'] = np.where( (df['is_weekd']==1) & (df['is_holiday']==0), 1, 0)

#workday of month
df['workdom'] = df[['ym','is_workd']].groupby('ym')['is_workd'].cumsum()

#total workdays in month
df = df_udfs.addColumnFromGroupbyOperation(df, 'tot_workdom', 'ym', 'is_workd', 'sum')

#workdays remaining in yearmonth
df['workd_remain_ym'] = df['tot_workdom'] - df['workdom']

#workday of year
df['workdoy'] = df[['y','is_workd']].groupby('y')['is_workd'].cumsum()

#total workdays in year
df = df_udfs.addColumnFromGroupbyOperation(df, 'tot_workdoy', 'y', 'is_workd', 'sum')

#workdays remaining in yearmonth
df['workd_remain_y'] = df['tot_workdoy'] - df['workdoy']

#is day Leap Year day
df['is_d_leapyr'] = np.where(
    (df['m']==2) & (df['d']==29),
    1,
    0
    )

#is yearmonth a Feb that contains Leap Year day
df = df_udfs.addColumnFromGroupbyOperation(df, 'is_ym_leapyr', 'ym', 'is_d_leapyr', 'sum')

#is year a leap year
df = df_udfs.addColumnFromGroupbyOperation(df, 'is_y_leapyr', 'y', 'is_d_leapyr', 'sum')

#first day of month datetime
df = df_udfs.addColumnFromGroupbyOperation(df, 'first_dom_dt', 'ym', 'dt', 'min')

#first day of month int
df = df_udfs.addColumnFromGroupbyOperation(df, 'first_dom_int', 'ym', 'dt_int', 'min')

#last day of month datetime
df = df_udfs.addColumnFromGroupbyOperation(df, 'last_dom_dt', 'ym', 'dt', 'max')

#last day of month datetime
df = df_udfs.addColumnFromGroupbyOperation(df, 'last_dom_int', 'ym', 'dt_int', 'max')

#first day of yearquarter datetime
df = df_udfs.addColumnFromGroupbyOperation(df, 'first_doyq_dt', 'yq', 'dt', 'min')

#first day of yearquarter int
df = df_udfs.addColumnFromGroupbyOperation(df, 'first_doyq_int', 'yq', 'dt_int', 'min')

#last day of yearquarter datetime
df = df_udfs.addColumnFromGroupbyOperation(df, 'last_doyq_dt', 'yq', 'dt', 'max')

#last day of yearquarter datetime
df = df_udfs.addColumnFromGroupbyOperation(df, 'last_doyq_int', 'yq', 'dt_int', 'max')

#first day of yearhalf datetime
df = df_udfs.addColumnFromGroupbyOperation(df, 'first_doyh_dt', 'yh', 'dt', 'min')

#first day of yearhalf int
df = df_udfs.addColumnFromGroupbyOperation(df, 'first_doyh_int', 'yh', 'dt_int', 'min')

#last day of yearhalf datetime
df = df_udfs.addColumnFromGroupbyOperation(df, 'last_doyh_dt', 'yh', 'dt', 'max')

#last day of yearhalf datetime
df = df_udfs.addColumnFromGroupbyOperation(df, 'last_doyh_int', 'yh', 'dt_int', 'max')

#first day of year datetime
df = df_udfs.addColumnFromGroupbyOperation(df, 'first_doy_dt', 'y', 'dt', 'min')

#first day of year int
df = df_udfs.addColumnFromGroupbyOperation(df, 'first_doy_int', 'y', 'dt_int', 'min')

#last day of year datetime
df = df_udfs.addColumnFromGroupbyOperation(df, 'last_doy_dt', 'y', 'dt', 'max')

#last day of year datetime
df = df_udfs.addColumnFromGroupbyOperation(df, 'last_doy_int', 'y', 'dt_int', 'max')

#moon phase name (approximate)
moon = moon.Moon()
df['moon_phase_name'] = df['dt'].apply(lambda x: moon.phase(moon.day_of_cycle(x))[0])

#moon phase index number as int (approximate)
df['moon_phase_index_int'] = df['dt'].apply(lambda x: moon.phase(moon.day_of_cycle(x))[1])

#moon phase index number as float (approximate)
df['moon_phase_index_full'] = df['dt'].apply(lambda x: moon.phase(moon.day_of_cycle(x))[2])

#moon illumination percentage (approximate)
df['moon_illum_pct'] = df['dt'].apply(lambda x: moon.illumination(moon.day_of_cycle(x)))

#sunrise UTC time
sun = sun.Sun(lat=cal_lat, lon=cal_lon)
df['sunrise_utc'] = df['dt'].apply(lambda x: sun.get_sunrise_time(date = x))

#sunset UTC time
df['sunset_utc'] = df['dt'].apply(lambda x: sun.get_sunset_time(date = x))

#sunlight duration utc
df['sun_duration_utc'] = df['sunset_utc'] - df['sunrise_utc']

#darkness duration utc (midnight to sunrise plus sunset to following midnight)
df['dark_duration_utc'] = timedelta(hours=24) - df['sun_duration_utc']

#sunrise local time
df['sunrise_local'] = df['dt'].apply(lambda x: sun.get_local_sunrise_time(date = x))
#sunset local time
df['sunset_local'] = df['dt'].apply(lambda x: sun.get_local_sunset_time(date = x))
#sunlight duration local
df['sun_duration_local'] = df['sunset_local'] - df['sunrise_local']
#darkness duration local (midnight to sunrise plus sunset to following midnight)
df['dark_duration_local'] = timedelta(hours=24) - df['sun_duration_local']

#timestamp when the calendar table was generated by this script
df['created_on'] = datetime.now()

#save the calendar table to a CSV file
df.to_csv('./calendar_table_output.csv')
misc_udfs.tprint('Calendar table process completed for ' + start_dt + ' through ' + end_dt + ' inclusive')

#generate the CSV support document that
create_docs.createColumnDescriptions(df, './docs/input/desc.csv').to_csv('./docs/col_descriptions.csv')

#generate the HTML support document that explains each column in tha calendar_table
create_docs.writeHTMLToFile(
    html_udfs.df_to_html('Documentation: Calendar Table Field Information',
        create_docs.createColumnDescriptions(df, './docs/input/desc.csv')
    ),'./docs/col_descriptions.html')

misc_udfs.tprint('Documention about column descriptions and datatypes loaded to ./docs/col_descriptions.html')
