'''
Orchestrate running calendar.py and daytime.py scripts with optional skipping.
Useful as a Docker entrypoint.
'''


import os
import subprocess
import sys


def run_script(script_name):
    """Run a Python script and return its exit code."""
    result = subprocess.run([sys.executable, script_name])
    return result.returncode


# Constants
SKIP_DAYTIME = (os.environ.get('SKIP_DAYTIME', None) is not None)
SKIP_CALENDAR = (os.environ.get('SKIP_CALENDAR', None) is not None)


# Run daytime.py unless SKIP_DAYTIME was specified
if SKIP_DAYTIME:
    print('Skipping daytime.py')
else:
    print('Running daytime.py')
    exit_code = run_script('daytime.py')
    if exit_code != 0:
        sys.exit(exit_code)
    print('OK')

# Run calendar.py unless SKIP_CALENDAR was specified
if SKIP_CALENDAR:
    print('Skipping calendar.py')
else:
    print('Running calendar.py')
    exit_code = run_script('calendar.py')
    if exit_code != 0:
        sys.exit(exit_code)
    print('OK')

if SKIP_DAYTIME and SKIP_CALENDAR:
    print('I did nothing, as you asked. It was an easy task!')

