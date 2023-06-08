<b>This is the best calendar_table with the most columns of interesting date dimensions you'll ever find!</b><br>

<h4> <i>Most recent successful run was on June 7, 2023 using Python 3.7.3, pandas 0.25.1 ; numpy 1.16.2 </i> </h4>

<h3>
PURPOSE:
</h3>
Quickly and easily generate a calendar
table with many columns of date dimensions
and metadata. Output to dataframe or CSV
to ingest into a database or for use in
an application like Excel or PowerBI.

<h3>
WHAT KIND OF COLUMNS?
</h3>
First of all, you'll find the usual dimensions:
<ul>
  <li> year number, month number, day number, yearmonth, yearquarter
  <li> month name, day name, full date w ordinal suffix (e.g., "January 3rd, 2012")
  <li> etc.
</ul>
    
Additionally, some interesting and unique data elements include:
<ul>
<li> holiday identification including Easter in any year (including pre-1583)
<li> moon phase identification
<li> sunrise/sunset for UTC as well as user-provided lat/lon coordinates
<li> length of daylight / darkness each day/evening
</ul>

For more information about the date dimensions and fields available, see these supporting documents:
<ul>
<li> Documentation: <a href="./docs/col_descriptions.csv">Full column list with datatypes and descriptions</a>
<li> Documentation: <a href="./calendar_table_output.csv">Sample output</a> (download and view in a CSV viewer like Excel)
</ul>


<h3>
WHY CREATE A CALENDAR TABLE / DATE DIMENSION TABLE?
</h3>
Calendar tables have myriad uses.  Examples:
<ul>
<li> PROCESS FLOW CONTROLS<br>
  Check today's date.  If it is a Sunday or the
  last day of the month, then run a code block.
<li> SLICING DATA FOR ANALYSIS<br>
  From the revenue dataset, show me all sales that
  fall between Thanksgiving and Christmas, and
  determine which days be best for best door-
  buster promotions
<li> FEATURES FOR MACHINE LEARNING MODELS<br>
  Using a polynomial linear regression, predict
  the end-of-month sales using the month-to-date
  sales along with the knowledge of what percent
  through the month the data is, comparing
  to similar data from prior months.
<li> DATA VISUALIZATION<br>
  In Microsoft PowerBI, or in Excel, or in Tableau,
  or in any tool... Use the workday of the month as
  the x-axis in a bar chart that shows the change
  in time clocked by employees on a given project
  in a given month
<li> AND MORE?<br>
  Send me more examples to add!
</ul>

<h3>
INSTALLATION/SETUP:
</h3>
Clone, checkout, or download the .py and run it in Python 3.7+.
No special imports will be needed outside of standard
libraries.

<h3>
NOTES:
</h3>
<ul>
<li> Example CSV output is provided in git repo
<li> When this code is run for a span of 5 years:
<ul>
<li> ~2,200 rows of data are created with ~110 columns (~240k cells)
<li> the resulting CSV's filesize is ~1.5 MiB
<li> the script takes ~28 seconds on my raspberry pi 4B (very low specs)
<li> code will run much faster on a modern laptop or desktop
</ul>
<li> No special import statements needed besides standard Python
  3.7+ packages
<li> 32-bit OS and hardware may cause limitations in the ability
  to generate table data for years far in the future (2040)
  and throw "OverflowError: timestamp out of range for
  platform time_t"; no limitation has been observed on
  64-bit systems.  
</ul>

<h3>
TO DO:
</h3>
<ul>
<li> modularize codes with classes/functions
<li> use config file to set main params (start,
  end, holiday rules, lat/lon for localized
  data like moon phase, sunrise, etc.)
<li> add columns
<ul>
<li> percent through w / ym / y / etc
<li> add season based on official start/end of seasons? (equinox, etc)
</ul>
<li> fix bugs in the following:
<ul>
<li> night duration utc / night duration local
</ul>
</ul>


<h3>
AUTHOR:
</h3>
This file was authored by TeneoPython01 with select
code excerpts leveraged from other authors where
noted.  In some cases the noted authors' code has
been materially modified.  In other cases it has
been used verbatim.  All other code is original.

<h3>
ABOUT AUTHOR:
</h3>
Contact me at https://github.com/TeneoPython01

<h3>
COLLABORATION?
</h3>
Collaboration is sought and encouraged on this project!

<h3>
LICENSE:
</h3>
See license information in git repo.  The software
is released in the public domain as-is without any
warranty.  More details can be found in the
license file.
