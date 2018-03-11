import os
import re
from datetime import datetime


class Date():
    def __init__(self, file=None):
        self.file = file

    def parse(self, date):
        date = date.replace("YYYY", "%Y")  # 2017 (year)
        date = date.replace("YY", "%y")  # 17 (year)
        date = date.replace("m", "%b")  # Dec (month)
        date = date.replace("MM", "%m")  # 12 (month)
        date = date.replace("M", "%B")  # December (month)
        date = date.replace("DDD", "%j")  # 123 (day or year)
        date = date.replace("DD", "%d")  # 25 (day)
        date = date.replace("\\", os.path.sep)  # path separator
        date = date.replace("/", os.path.sep)  # path separator
        return date

    def strptime(self, date, format):
        return datetime.strptime(date, format)

    def build(self, date_object):
        return datetime(date_object["year"], date_object["month"], date_object["day"],
                        date_object["hour"], date_object["minute"], date_object["second"])

    def from_exif(self, exif, user_regex=None):
        keys = ['CreateDate', 'DateTimeOriginal']

        datestr = None

        for key in keys:
            if key in exif:
                datestr = exif[key]
                break

        if datestr:
            return self.from_datestring(datestr)
        else:
            return self.from_filename(user_regex)

    def from_datestring(self, datestr):
        datestr = datestr.split('.')
        date = datestr[0]
        if len(datestr) > 1:
            subseconds = datestr[1]
        else:
            subseconds = ''
        search = r'(.*)([+-]\d{2}:\d{2})'
        if re.search(search, date) is not None:
            date = re.sub(search, r'\1', date)
        try:
            parsed_date_time = self.strptime(date, "%Y:%m:%d %H:%M:%S")
        except ValueError:
            try:
                parsed_date_time = self.strptime(date, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                parsed_date_time = None
        return {
            'date': parsed_date_time,
            'subseconds': subseconds
        }

    def from_filename(self, user_regex):
        # If missing datetime from EXIF data check if filename is in datetime format.
        # For this use a user provided regex if possible.
        # Otherwise assume a filename such as IMG_20160915_123456.jpg as default.
        default_regex = re.compile(
            '.*[_-](?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})[_-]?(?P<hour>\d{2})(?P<minute>\d{2})(?P<second>\d{2})')
        regex = user_regex or default_regex
        matches = regex.search(os.path.basename(self.file))

        if matches:
            try:
                match_dir = matches.groupdict()
                match_dir = dict([a, int(x)] for a, x in match_dir.items())  # Convert str to int
                date = self.build(match_dir)
            except (KeyError, ValueError):
                date = None

            if date:
                return {
                    'date': date,
                    'subseconds': ''
                }
