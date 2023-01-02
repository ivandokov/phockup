#!/usr/bin/env python3
import os
import re
from datetime import datetime

from src.date import Date

os.chdir(os.path.dirname(__file__))


def test_parse_date_format_valid():
    """Test that parse_date_format returns a valid format for strftime"""
    datetime.strftime(
        datetime.now(),
        Date().parse("YYYY YY m MM M DDD DD \\ /")
    )


def test_get_date_from_exif():
    assert Date().from_exif({
        "CreateDate": "2017-01-01 01:01:01"
    }) == {
               "date": datetime(2017, 1, 1, 1, 1, 1),
               "subseconds": ""
           }


def test_get_date_from_exif_with_timezone():
    assert Date().from_exif({
        "CreateDate": "2023-01-01 01:01:01",
        "TimeZone": "-07:00",
    }) == {
               "date": datetime(2022, 12, 31, 18, 1, 1),
               "subseconds": ""
           }


def test_get_date_from_custom_date_field():
    assert Date().from_exif({
        "CustomField": "2017:01:01 01:01:01"
    }, date_field="CustomField") == {
               "date": datetime(2017, 1, 1, 1, 1, 1),
               "subseconds": ""
           }


def test_get_date_from_exif_strip_timezone():
    assert Date().from_exif({
        "CreateDate": "2017-01-01 01:01:01-02:00"
    }) == {
               "date": datetime(2017, 1, 1, 1, 1, 1),
               "subseconds": ""
           }


def test_get_date_from_exif_strip_timezone_sub_sec():
    assert Date().from_exif({
        "SubSecCreateDate": "2019:10:06 11:02:50.575+01:00"
    }) == {
               "date": datetime(2019, 10, 6, 11, 2, 50),
               "subseconds": "575"
           }


def test_get_date_from_exif_colon():
    assert Date().from_exif({
        "CreateDate": "2017:01:01 01:01:01"
    }) == {
               "date": datetime(2017, 1, 1, 1, 1, 1),
               "subseconds": ""
           }


def test_get_date_from_exif_subseconds():
    assert Date().from_exif({
        "CreateDate": "2017-01-01 01:01:01.20"
    }) == {
               "date": datetime(2017, 1, 1, 1, 1, 1),
               "subseconds": "20"
           }


def test_get_date_from_exif_invalid():
    assert Date().from_exif({
        "CreateDate": "Invalid"
    }) == {
               "date": None,
               "subseconds": ""
           }


def test_get_date_from_filename():
    assert Date("IMG_20170101_010101.jpg").from_exif({}) == {
        "date": datetime(2017, 1, 1, 1, 1, 1),
        "subseconds": ""
    }


def test_get_date_filename_invalid():
    assert Date("IMG_20170101_999999.jpg").from_exif({}) is None


def test_get_date_none_on_no_info():
    assert Date("Foo.jpg").from_exif({}) is None


def test_get_date_none_on_no_error():
    assert Date("IMG_2017_01.jpg").from_exif({}) is None


def test_get_date_custom_regex():
    """
    A valid regex with a matching filename. Returns a datetime.
    """
    date_regex = re.compile(r"(?P<day>\d{2})\.(?P<month>\d{2})\.(?P<year>\d{4})[_-]?(?P<hour>\d{2})\.(?P<minute>\d{2})\.(?P<second>\d{2})")     # noqa: E501
    assert Date("IMG_27.01.2015-19.20.00.jpg").from_exif({}, False,
                                                         date_regex) == {
        "date": datetime(2015, 1, 27, 19, 20, 00),
        "subseconds": ""
    }


def test_get_date_custom_regex_invalid():
    """
    A valid regex with a matching filename.
    Return none because there is not enough information in the filename.
    """
    date_regex = re.compile(r"(?P<hour>\d{2})\.(?P<minute>\d{2})\.(?P<second>\d{2})")       # noqa: E501
    assert Date("19.20.00.jpg").from_exif({}, False, date_regex) is None


def test_get_date_custom_regex_no_match():
    """
    A valid regex with a non-matching filename.
    """
    date_regex = re.compile(r"(?P<day>\d{2})\.(?P<month>\d{2})\.(?P<year>\d{4})[_-]?(?P<hour>\d{2})\.(?P<minute>\d{2})\.(?P<second>\d{2})")     # noqa: E501
    assert Date("Foo.jpg").from_exif({}, False, date_regex) is None


def test_get_date_custom_regex_optional_time():
    """
    A valid regex with a matching filename that doesn't have hour information.
    However, the regex in question has hour information as optional.
    """
    date_regex = re.compile(r"(?P<day>\d{2})\.(?P<month>\d{2})\.(?P<year>\d{4})[_-]?((?P<hour>\d{2})\.(?P<minute>\d{2})\.(?P<second>\d{2}))?")  # noqa: E501
    assert Date("IMG_27.01.2015.jpg").from_exif({}, False, date_regex) == {
        "date": datetime(2015, 1, 27, 0, 0, 00),
        "subseconds": ""
    }
