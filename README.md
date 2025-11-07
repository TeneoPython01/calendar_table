# Calendar Table Generator

Forked from: [TeneoPython01/calendar_table](https://github.com/TeneoPython01/calendar_table)


## Purpose

Quickly and easily generate a calendar
table with many columns of date dimensions
and metadata. Output to CSV.


## Usage with Docker

The first time you run this Generator, you'll need to build a Docker image
from the Dockerfile. You'll need to do it again every time you update
the code.

To build a Docker image:

```
docker build -t calendar-table .
```

Then, you can use the Generator by creating an ephemeral container. This container
will be destroyed when the Generator ends its execution.

To run the Generator:

```
docker run -e START_DATE='2020-01-01' -e END_DATE='2028-12-31' \
  -v ./output:/app/output calendar-table
```

Argumdnts:

- `START_DATE` and `END_DATE` are in the 'YYYY-MM-DD' format. Separators can be
  added for better readibility. Dashes (`-`) and slashes (`/`) are accepted,
  but optional.
- The path (`./output`) will be created on the host system if it doesn't exist.
  It will be a directory containing the generated file.


## Which Columns are Created

First of all, you'll find the usual dimensions:
- year number, month number, day number, yearmonth, yearquarter
- month name, day name, full date w ordinal suffix (e.g., "January 3rd, 2012")
- etc.
    
Additionally, some interesting and unique data elements include:
- holiday identification including Easter in any year (including pre-1583)
- moon phase identification
- sunrise/sunset for UTC as well as user-provided lat/lon coordinates
- length of daylight / darkness each day/evening

Documentation: [Full column list with datatypes and descriptions](./docs/col_descriptions.csv)


## Notes

- Example CSV output is provided in git repo
- When this code is run for a span of 5 years:
  - ~2,200 rows of data are created with ~110 columns (~240k cells)
  - the resulting CSV's filesize is ~1.5 MiB
  - the script takes ~28 seconds on my raspberry pi 4B (very low specs)
  - code will run much faster on a modern laptop or desktop
- No special import statements needed besides standard Python
  3.7+ packages
- 32-bit OS and hardware may cause limitations in the ability
  to generate table data for years far in the future (2040)
  and throw "OverflowError: timestamp out of range for
  platform time_t"; no limitation has been observed on
  64-bit systems.  


## Authors

This project is maintained by Vettabase.

This project is a calendar_table derivative. The author is
[TeneoPython01](https://github.com/TeneoPython01),
with external contributions where noted.


### License

See license information in git repo.  The software
is released in the public domain as-is without any
warranty.  More details can be found in the
license file.

