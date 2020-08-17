import pandas as pd #to handle data in pandas dataframes
pd.set_option('display.max_rows', 1000) #allow printing lots of rows to screen
pd.set_option('display.max_columns', 1000) #allow printsin lots of cols to screen
pd.set_option('display.width', 1000) #don't wrap lots of columns

import requests #to pull JSON data
import numpy as np #to do conditional pandas operations
import datetime as dt #to track datetime stamps
global_now = dt.datetime.now()

from dateutil import tz #for timezone handling with datetime dtypes

#this is the datetime mask native to the API output
api_mask = '%Y-%m-%dT%H:%M:%S.000Z' 
#this is the datetime mask for readable format
readable_mask = "%a %m/%d/%Y %I:%M%p %Z" #this is a readable format
year_mask = "%Y" #just the year
from_zone = tz.tzutc() #API datetimes are in UTC time
to_zone = tz.tzlocal() #Used for converting to local timezone

#FUNCTION RETURNS HTML CODE FOR THE HEADER PORTION OF
#AN HTML FILE
def html_header(my_title=''):
    html_script = """
    <!DOCTYPE html>
    <HTML>
        <HEAD>
            <TITLE>"""
    
    html_title = my_title + '</TITLE>'
    
    html_script = html_script + '\n' + html_title    
    
    return html_script

#FUNCTION RETURNS HTML CODE FOR THE STYLE TAG PORTION OF
#AN HTML FILE
def html_style_header(my_title=''):

    html_script = """
    <!-- CSS goes in the document HEAD or added to your external stylesheet -->
    <style type="text/css">
    table.gridtable {
        font-family: verdana,arial,sans-serif;
        font-size:11px;
        border-width: 1px;
        border-color: #666666;
        border-collapse: collapse;
    }
    table.gridtable th{
        border-width: 1px;
        padding: 18px;
        border-style: solid;
        border-color: #666666;
        background-color: #dedede;
    }
    table.gridtable td{
        border-width: 1px;
        padding: 6px;
        border-style: solid;
        border-color: #666666;
        background-color: #ffffff;
    }
    /* Define the default color for all the table rows */
    .gridtable tr{
        background: #b8d1f3;
    }
    /* Define the hover highlight color for the table row */
    .gridtable td:hover {
        background-color: #ffff99;
    }

    </style>
    </HEAD>
    <BODY>
    
    """ + '<H3>' + my_title + '</H3><BR>'
    
    return html_script

#FUNCTION RETURNS HTML CODE FOR A DATAFRAME THAT IS
#PASSED AS A PARAMETER AND ASSIGNS THE TABLE
#CLASS NAME TO MATCH THE STYLE TAG CLASS NAME
def html_from_df(df):

    html_script = df.to_html(index=False).replace(
        '<table border="1" class="dataframe">',
        '<table class="gridtable">'
    )
    
    return html_script

#FUNCTION RETURNS HTML CODE FOR THE FOOTER PORTION OF
#AN HTML FILE
def html_footer():

    html_script = """
    </BODY>
    </HTML>
    """
    
    return html_script

#FUNCTION RETURNS HEADER, STYLE TAG, DATAFRAMES, AND FOOTER
#HTML CODE IN ONE CONCATENATED STRING
def df_to_html(my_title, df):

    html_script = ''
    html_script = html_script + html_header(my_title)
    html_script = html_script + html_style_header(my_title)
    html_script = html_script + html_from_df(df)
    html_script = html_script + html_footer()
    
    return html_script
