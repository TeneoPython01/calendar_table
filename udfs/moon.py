#class to determine moon phases (approximate)
#class code used in Aug, 2020 from https://gist.github.com/mrrrk/

import math, datetime

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
        base_new_moon = datetime.datetime(2017, 8, 21, 18, 30, 0)
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
