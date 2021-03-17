#!/usr/bin/env python3
import argparse
import os
import re
import sys

from src.date import Date
from src.dependency import check_dependencies
from src.phockup import Phockup
from src.printer import Printer


__version__ = "1.5.26"

printer = Printer()

PROGRAM_DESCRIPTION = """Media sorting tool to organize photos and videos from your camera in folders by year, month and day.
The software will collect all files from the input directory and copy them to the output directory without
changing the files content. It will only rename the files and place them in the proper directory for year, month and day.
"""

DEFAULT_DIR_FORMAT = ['%Y', '%m', '%d']


def main():
    check_dependencies()


    parser = argparse.ArgumentParser(
        description=PROGRAM_DESCRIPTION,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.version = "v%s" % __version__

    parser.add_argument(
        "-v",
        "--version",
        action="version",
    )

    parser.add_argument(
        "-d",
        "--date",
        action="store",
        type=Date().parse,
        help="""Specify date format for OUTPUTDIR directories.
You can choose different year format (e.g. 17 instead of 2017) or decide to
skip the day directories and have all photos sorted in year/month.

Supported formats:
    YYYY - 2016, 2017 ...
    YY   - 16, 17 ...
    MM   - 07, 08, 09 ...
    M    - July, August, September ...
    m    - Jul, Aug, Sept ...
    DD   - 27, 28, 29 ... (day of month)
    DDD  - 123, 158, 365 ... (day of year)

Example:
    YYYY/MM/DD -> 2011/07/17
    YYYY/M/DD  -> 2011/July/17
    YYYY/m/DD  -> 2011/Jul/17
    YY/m-DD    -> 11/Jul-17
        """,
    )

    exclusive_group = parser.add_mutually_exclusive_group()

    exclusive_group.add_argument(
        "-m",
        "--move",
        action="store_true",
        help="""Instead of copying the process will move all files from the INPUTDIR to the OUTPUTDIR.
This is useful when working with a big collection of files and the
remaining free space is not enough to make a copy of the INPUTDIR.
        """,
    )

    exclusive_group.add_argument(
        "-l",
        "--link",
        action="store_true",
        help="""Instead of copying the process will make hard links to all files in INPUTDIR and place them in the OUTPUTDIR.
This is useful when working with working structure and want to create YYYY/MM/DD structure to point to same files.
        """,
    )

    parser.add_argument(
        "-o",
        "--original-names",
        action="store_true",
        help="Organize the files in selected format or using the default year/month/day format but keep original filenames.",
    )

    parser.add_argument(
        "-t",
        "--timestamp",
        action="store_true",
        help="""Use the timestamp of the file (last modified date) if there is no EXIF date information.
If the user supplies a regex, it will be used if it finds a match in the filename.
This option is intended as "last resort" since the file modified date may not be accurate,
nevertheless it can be useful if no other date information can be obtained.
        """,
    )

    parser.add_argument(
        "-y",
        "--dry-run",
        action="store_true",
        help="Don't move any files, just show which changes would be done.",
    )

    parser.add_argument(
        "-r",
        "--regex",
        action="store",
        type=re.compile,
        help="""Specify date format for date extraction from filenames if there is no EXIF date information.

Example:
    {regex}
    can be used to extract the date from file names like the following IMG_27.01.2015-19.20.00.jpg.
        """,
    )

    parser.add_argument(
        "-f",
        "--date-field",
        action="store",
        help="""Use a custom date extracted from the exif field specified.
To set multiple fields to try in order until finding a valid date,
use spaces to separate fields inside a string.

Example:
    DateTimeOriginal
    "DateTimeOriginal CreateDate FileModifyDate"

These fields are checked by default when this argument is not set:
    "SubSecCreateDate SubSecDateTimeOriginal CreateDate DateTimeOriginal"

To get all date fields available for a file, do:
    exiftool -time:all -mimetype -j <file>
        """,
    )

    parser.add_argument(
        "input_dir",
        metavar="INPUTDIR",
        help="Specify the source directory where your photos are located.",
    )
    parser.add_argument(
        "output_dir",
        metavar="OUTPUTDIR",
        help="Specify the output directory where your photos should be exported.",
    )

    args = parser.parse_args()

    return Phockup(
        args.input_dir,
        args.output_dir,
        dir_format=args.date,
        move=args.move,
        link=args.link,
        date_regex=args.regex,
        original_filenames=args.original_names,
        timestamp=args.timestamp,
        date_field=args.date_field,
        dry_run=args.dry_run,
    )


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        printer.empty().line('Exiting...')
        sys.exit(0)
