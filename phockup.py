#!/usr/bin/env python3
import argparse
import logging
import logging.handlers
import os
import re
import sys

from src.date import Date
from src.dependency import check_dependencies
from src.phockup import Phockup

__version__ = '1.13.0'

PROGRAM_DESCRIPTION = """\
Media sorting tool to organize photos and videos from your camera in folders by year, \
month and day.
The software will collect all files from the input directory and copy them to the output
directory without changing the files content. It will only rename the files and  place
them in the proper directory for year, month and day.
"""

DEFAULT_DIR_FORMAT = ['%Y', '%m', '%d']

logger = logging.getLogger('phockup')


def parse_args(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description=PROGRAM_DESCRIPTION,
        formatter_class=argparse.RawTextHelpFormatter)

    parser.version = f"v{__version__}"

    parser.add_argument(
        '-v',
        '--version',
        action='version',
    )

    parser.add_argument(
        '-d',
        '--date',
        action='store',
        type=Date.parse,
        help="""\
Specify date format for OUTPUTDIR directories.

You can choose different year format (e.g. 17 instead of 2017) or decide to skip the
day directories and have all photos sorted in year/month.

Supported formats:
    YYYY - 2016, 2017 ...
    YY   - 16, 17 ...
    MM   - 07, 08, 09 ...
    M    - July, August, September ...
    m    - Jul, Aug, Sept ...
    DD   - 27, 28, 29 ... (day of month)
    DDD  - 123, 158, 365 ... (day of year)
    U    - 00, 01, 53 ... (week of the year, Sunday first day of week)
    W    - 00, 01, 53 ... (week of the year, Monday first day of week)

Example:
    YYYY/MM/DD -> 2011/07/17
    YYYY/M/DD  -> 2011/July/17
    YYYY/m/DD  -> 2011/Jul/17
    YY/m-DD    -> 11/Jul-17
    YYYY/U     -> 2011/30
    YYYY/W     -> 2011/28
""",
    )

    exclusive_group_link_move = parser.add_mutually_exclusive_group()

    exclusive_group_link_move.add_argument(
        '-m',
        '--move',
        action='store_true',
        help="""\
            Instead of copying the process will move all files from the INPUTDIR to the OUTPUTDIR.
            This is useful when working with a big collection of files and the remaining free space
            is not enough to make a copy of the INPUTDIR.
            """,
    )

    exclusive_group_link_move.add_argument(
        '-l',
        '--link',
        action='store_true',
        help="""\
            Instead of copying the process will make hard links to all files in INPUTDIR and place
            them in the OUTPUTDIR.
            This is useful when working with working structure and want to create YYYY/MM/DD
            structure to point to same files.
            """,
    )

    parser.add_argument(
        '-o',
        '--original-names',
        action='store_true',
        help="""\
            Organize the files in selected format or using the default year/month/day format but
            keep original filenames.
            """,
    )

    parser.add_argument(
        '-t',
        '--timestamp',
        action='store_true',
        help="""\
            Use the timestamp of the file (last modified date) if there is no EXIF date information.
            If the user supplies a regex, it will be used if it finds a match in the filename.
            This option is intended as "last resort" since the file modified date may not be
            accurate, nevertheless it can be useful if no other date information can be obtained.
            """,
    )

    parser.add_argument(
        '-y',
        '--dry-run',
        action='store_true',
        help="""\
            Does a trial run with no permanent changes to the filesystem.
            So it will not move any files, just shows which changes would be done.
            """,
    )

    parser.add_argument(
        '-c',
        '--max-concurrency',
        type=int,
        default=1,
        choices=range(1, 255),
        metavar='1-255',
        help="""\
            Sets the level of concurrency for processing files in a directory.
            Defaults to 1. Higher values can improve throughput of file operations
            """,
    )

    parser.add_argument(
        '--maxdepth',
        type=int,
        default=-1,
        choices=range(0, 255),
        metavar='1-255',
        help="""\
            Descend at most 'maxdepth' levels (a non-negative integer) of directories
            """,
    )

    parser.add_argument(
        '-r',
        '--regex',
        action='store',
        type=re.compile,
        help="""\
            Specify date format for date extraction from filenames if there is no EXIF date
            information.

            Example:
                {regex}
                can be used to extract the date from file names like the following
                IMG_27.01.2015-19.20.00.jpg.
            """,
    )

    parser.add_argument(
        '-f',
        '--date-field',
        action='store',
        help="""\
            Use a custom date extracted from the exif field specified.
            To set multiple fields to try in order until finding a valid date, use spaces to
            separate fields inside a string.

            Example:
                DateTimeOriginal
                "DateTimeOriginal CreateDate FileModifyDate"

            These fields are checked by default when this argument is not set:
                "SubSecCreateDate SubSecDateTimeOriginal CreateDate DateTimeOriginal"

            To get all date fields available for a file, do:
                exiftool -time:all -mimetype -j <file>
            """,
    )

    exclusive_group_debug_silent = parser.add_mutually_exclusive_group()

    exclusive_group_debug_silent.add_argument(
        '--debug',
        action='store_true',
        default=False,
        help="""\
            Enable debugging.  Alternately, set the LOGLEVEL environment variable to DEBUG
            """,
    )

    exclusive_group_debug_silent.add_argument(
        '--quiet',
        action='store_true',
        default=False,
        help="""\
            Run without output.
            """,
    )

    exclusive_group_debug_silent.add_argument(
        '--progress',
        action='store_true',
        default=False,
        help="""\
            Run with progressbar output.
            """,
    )

    parser.add_argument(
        '--log',
        action='store',
        help="""\
            Specify the output directory where your log file should be exported.
            This flag can be used in conjunction with the flag `--quiet` or `--progress`.
            """,
    )

    parser.add_argument(
        'input_dir',
        metavar='INPUTDIR',
        help="""\
            Specify the source directory where your photos are located.
            """,
    )

    parser.add_argument(
        'output_dir',
        metavar='OUTPUTDIR',
        help="""\
            Specify the output directory where your photos should be exported.
            """,
    )

    parser.add_argument(
        '--file-type',
        type=str,
        choices=['image', 'video'],
        metavar='image|video',
        help="""\
            By default, Phockup addresses both image and video files.
            If you want to restrict your command to either images or
            videos only, use `--file-type=[image|video]`.
            """,
    )

    parser.add_argument(
        '--no-date-dir',
        type=str,
        default=Phockup.DEFAULT_NO_DATE_DIRECTORY,
        help="""\
            Files without EXIF date information are placed in a directory
            named 'unknown' by default.  This option overrides that
            folder name. e.g. --no-date-dir=misc, --no-date-dir="no date"
            """,
    )

    parser.add_argument(
        '--skip-unknown',
        action='store_true',
        default=False,
        help="""\
            Ignore files that don't contain valid EXIF data for the criteria specified.
            This is useful if you intend to make multiple passes over an input directory
            with varying and specific EXIF fields that are note checked by default.
            """,
    )

    parser.add_argument(
        '--movedel',
        action='store_true',
        default=False,
        help="""\
            DELETE source files which are determined to be duplicates of files
            already transferred.  Only valid in conjunction with both `--move`
            and `--skip-unknown`.
            """,
    )

    parser.add_argument(
        '--rmdirs',
        action='store_true',
        default=False,
        help="""\
            DELETE empty directories after processing.  Only valid in
            conjunction with `--move`.
            """,
    )

    parser.add_argument(
        '--output_prefix',
        type=str,
        default='',
        help="""\
            String to prepend to the output directory to aid in sorting
            files by an additional level prior to sorting by date.  This
            string will immediately follow the output path and is intended
            to allow runtime setting of the output path (e.g. via $USER,
            $HOSTNAME, %%USERNAME%%, etc.)
            """,
    )

    parser.add_argument(
        '--output_suffix',
        type=str,
        default='',
        help="""\
            String to append to the destination directory to aid in sorting
            files by an additional level after sorting by date.
            """,
    )

    parser.add_argument(
        '--from-date',
        type=str,
        default=None,
        help="""\
            Limit the operations to the files that are newer than --from-date (inclusive).
            The date must be specified in format YYYY-MM-DD. Files with unknown date won't be skipped.
            """,
    )

    parser.add_argument(
        '--to-date',
        type=str,
        default=None,
        help="""\
            Limit the operations to the files that are older than --to-date (inclusive).
            The date must be specified in format YYYY-MM-DD. Files with unknown date won't be skipped.
            """,
    )

    return parser.parse_args(args)


def setup_logging(options):
    """Configure logging."""
    root = logging.getLogger('')
    root.setLevel(logging.WARNING)
    formatter = logging.Formatter(
        '[%(asctime)s] - [%(levelname)s] - %(message)s', '%Y-%m-%d %H:%M:%S')
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    root.addHandler(ch)
    if not options.quiet ^ options.progress:
        logger.setLevel(options.debug and logging.DEBUG or logging.INFO)
    else:
        logger.setLevel(logging.WARNING)
    if options.log:
        logfile = os.path.expanduser(options.log)
        fh = logging.FileHandler(logfile)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    logger.debug("Debug logging output enabled.")
    logger.debug("Running Phockup version %s", __version__)


def main(options):
    check_dependencies()

    return Phockup(
        options.input_dir,
        options.output_dir,
        dir_format=options.date,
        move=options.move,
        link=options.link,
        date_regex=options.regex,
        original_filenames=options.original_names,
        timestamp=options.timestamp,
        date_field=options.date_field,
        dry_run=options.dry_run,
        quiet=options.quiet,
        progress=options.progress,
        max_depth=options.maxdepth,
        file_type=options.file_type,
        max_concurrency=options.max_concurrency,
        no_date_dir=options.no_date_dir,
        skip_unknown=options.skip_unknown,
        movedel=options.movedel,
        rmdirs=options.rmdirs,
        output_prefix=options.output_prefix,
        output_suffix=options.output_suffix,
        from_date=options.from_date,
        to_date=options.to_date
    )


if __name__ == '__main__':
    try:
        options = parse_args()
        setup_logging(options)
        main(options)
    except Exception as e:
        logger.warning(e)
        sys.exit(1)
    except KeyboardInterrupt:
        logger.error("Exiting phockup...")
        sys.exit(1)
    sys.exit(0)
