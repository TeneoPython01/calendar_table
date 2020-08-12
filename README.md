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

INSTALLATION/SETUP:
Clone, checkout, or download the .py and run it in Python 3.7+.
No special imports will be needed outside of standard
libraries.

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


AUTHOR:
This file was authored by TeneoPython01 with select
code excerpts leveraged from other authors where
noted.  In some cases the noted authors' code has
been materially modified.  In other cases it has
been used verbatim.  All other code is original.

ABOUT AUTHOR:
Contact me at https://github.com/TeneoPython01

COLLABORATION?
Collaboration is sought and encouraged on this project!

LICENSE:
See license information in git repo.  The software
is released in the public domain as-is without any
warranty.  More details can be found in the
license file.
