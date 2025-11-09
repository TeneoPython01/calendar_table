# Calendar Table Generator

The purpose of this project is to generate rich date/time data that can easily be imported
into a database, for analytics goals.

The project contains tools to generate a calendar table and a daytime table, with various
attributes and metadata.

The output is currently written to CSV files.


## Usage with Docker or Podman

The best way to use these tools is via Docker or Podman.
While containerisation is not strictly necessary, it is how we normally test
and use this project.

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

Options:

- `SKIP_CALENDAR`: don't generate a calendar table.
- `SKIP_DAYTIME`: don't generate a daytime table.
- `START_DATE` and `END_DATE` are in the 'YYYY-MM-DD' format. Separators can be
  added for better readibility. Dashes (`-`) and slashes (`/`) are accepted,
  but optional.
- `INCLUDE_CALENDAR_COLUMNS` can be set to a comma-separated list of columns to include
  in the output. `dt` must be specified. By default, all columns are included.
- `SKIP_CALENDAR_COLUMNS` can be set to a comma-separated list of columns to exclude
  from the output. Cannot be set if `INCLUDE_CALENDAR_COLUMNS` is set.
  `dt` cannot be skipped. By default, no column is skipped.
- `START_TIME` and `END_TIME` are in the `HH:MM:SS` format (columns are optional).
  Default: `00:00:00` and `23:59:59`. An end time of `23:59:60` is admitted, because
  you might want to include the leap second.
- `TIME_STEP` is the increment for the daytime table. Default: `1m`.
  Supported units are `s`, `m`, and `h` (case-insensitive). Units cannot be combined.
- `INCLUDE_TIME_COLUMNS` can be set to a comma-separated list of columns to include
  in the output. `dt` must be specified. By default, all columns are included.
- `SKIP_TIME_COLUMNS` can be set to a comma-separated list of columns to exclude
  from the output. Cannot be set if `INCLUDE_TIME_COLUMNS` is set.
  `dt` cannot be skipped. By default, no column is skipped.
- The path (`./output`) will be created on the host system if it doesn't exist.
  It contain the following generated files:
  - `daytime.csv`
  - `calendar.csv`


## Which Columns are Created

TO-DO: Update this section.

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


## Limitations

32-bit OS and hardware may cause limitations in the ability
to generate table data for years far in the future (2040) and raise
an OverflowError exception.
No limitation was observed on 64-bit systems.  

Holidays data uses a home-made implementation from the original project.
We will replace it with a reliable Python module.

CSV files are generated and they can be imported into databases.
But we don't provide (yet) a simple way to generate optimal tables
with the correct types.
We will do this at least for PostgreSQL and MariaDB.


## Maintainers and Credits

This project is maintained by Vettabase.

This project was originally forked from [TeneoPython01/calendar_table](https://github.com/TeneoPython01/calendar_table).
The original project's author is [TeneoPython01](https://github.com/TeneoPython01).
External contributions, if still present, are noted in the code.


## License

This software is released in the public domain as-is without any warranty.
See the license file.

