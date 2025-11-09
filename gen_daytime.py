'''
Generate a daytime table with various time attributes and metadata.
Write output to a CSV file.

The original code was contributed by C. Sonnet: c.sonnet@anthropic.com
'''


import os
import pandas as pd
from datetime import datetime, time, timedelta
from udfs import misc_udfs


# Constants
OUTPUT_DIR = './output'


# User-defined variables
skip_columns = os.environ.get('SKIP_TIME_COLUMNS', None)
include_columns = os.environ.get('INCLUDE_TIME_COLUMNS', None)
start_time_str = os.environ.get('START_TIME', '00:00:00')
end_time_str = os.environ.get('END_TIME', '23:59:59')
step_str = os.environ.get('TIME_STEP', '1m')

# Validate columns
if skip_columns is not None and include_columns is not None:
    raise ValueError("SKIP_TIME_COLUMNS and INCLUDE_TIME_COLUMNS environment variables are mutually exclusive")
if skip_columns:
    skip_columns = skip_columns.split(',')
    if 'time_int' in skip_columns:
        raise ValueError('time_int column cannot be excluded')
if include_columns:
    include_columns = include_columns.split(',')
    if 'time_int' not in include_columns:
        raise ValueError('time_int column must be included')

# Parse and normalize time strings (remove colons if present)
start_time_str = start_time_str.replace(':', '')
end_time_str = end_time_str.replace(':', '')

# Validate time format (must be 6 digits)
if len(start_time_str) != 6 or not start_time_str.isdigit():
    raise ValueError("START_TIME must be in HH:MM:SS format (colons are optional)")
if len(end_time_str) != 6 or not end_time_str.isdigit():
    raise ValueError("END_TIME must be in HH:MM:SS format (colons are optional)")

# Parse times
start_hour = int(start_time_str[0:2])
start_minute = int(start_time_str[2:4])
start_second = int(start_time_str[4:6])

end_hour = int(end_time_str[0:2])
end_minute = int(end_time_str[2:4])
end_second = int(end_time_str[4:6])

# Validate time ranges
if not (0 <= start_hour <= 23 and 0 <= start_minute <= 59 and 0 <= start_second <= 59):
    raise ValueError("START_TIME out of range")
# For END_TIME, allow leap second only at 23:59:60
if end_second == 60:
    if not (end_hour == 23 and end_minute == 59):
       raise ValueError("END_TIME: 60 seconds only allowed for leap second at 23:59:60")
elif not (0 <= end_hour <= 23 and 0 <= end_minute <= 59 and 0 <= end_second <= 59):
       raise ValueError("END_TIME out of range")

# Convert to total seconds for comparison
int_start_seconds = start_hour * 3600 + start_minute * 60 + start_second
int_end_seconds = end_hour * 3600 + end_minute * 60 + end_second

if int_start_seconds >= int_end_seconds:
    raise ValueError("START_TIME must be less than END_TIME")

# Parse step
step_str = step_str.lower().strip()
if not step_str[-1] in ['s', 'm', 'h']:
    raise ValueError("STEP must end with 's' (seconds), 'm' (minutes), or 'h' (hours)")

try:
    step_value = int(step_str[:-1])
except ValueError:
    raise ValueError("STEP must have a numeric value before the unit")

if step_value <= 0:
    raise ValueError("STEP value must be positive")

step_unit = step_str[-1]

# Convert step to seconds
if step_unit == 's':
    step_seconds = step_value
elif step_unit == 'm':
    step_seconds = step_value * 60
elif step_unit == 'h':
    step_seconds = step_value * 3600

# Start the process
misc_udfs.tprint(f'daytime table process started for {start_time_str[0:2]}:{start_time_str[2:4]}:{start_time_str[4:6]} through {end_time_str[0:2]}:{end_time_str[2:4]}:{end_time_str[4:6]} with step {step_str}')

# Generate time range
time_list = []
current_seconds = int_start_seconds

while current_seconds <= int_end_seconds:
    # Convert seconds back to hours, minutes, seconds
    hours = current_seconds // 3600
    minutes = (current_seconds % 3600) // 60
    seconds = current_seconds % 60
    
    # Create time object
    time_obj = time(hour=hours, minute=minutes, second=seconds)
    
    # time_int (HHMMSS format)
    time_int = hours * 10000 + minutes * 100 + seconds
    
    # time_string12 (12-hour format with AM/PM)
    hour_12 = hours % 12
    if hour_12 == 0:
        hour_12 = 12
    am_pm = 'AM' if hours < 12 else 'PM'
    time_string12 = f'{hour_12:02d}:{minutes:02d}:{seconds:02d} {am_pm}'
    
    # time_string24 (24-hour format)
    time_string24 = f'{hours:02d}:{minutes:02d}:{seconds:02d}'
    
    time_list.append({
        'time_int': time_int,
        'time_string12': time_string12,
        'time_string24': time_string24,
        'hour': hours,
        'minute': minutes,
        'second': seconds
    })
    
    current_seconds += step_seconds

# Create DataFrame
df = pd.DataFrame(time_list)

# Exclude columns listed in SKIP_TIME_COLUMNS or columns not mentioned in INCLUDE_TIME_COLUMNS
if skip_columns:
    df = df.drop(columns=[col for col in skip_columns if col in df.columns])
elif include_columns:
    # Always keep 'time_int' as the primary key
    cols_to_keep = [col for col in include_columns if col in df.columns]
    df = df[cols_to_keep]

# Save to CSV without index
df.to_csv(OUTPUT_DIR + '/daytime.csv', index=False)

misc_udfs.tprint(f'Daytime table process completed for {start_time_str[0:2]}:{start_time_str[2:4]}:{start_time_str[4:6]} through {end_time_str[0:2]}:{end_time_str[2:4]}:{end_time_str[4:6]} with step {step_str}')
