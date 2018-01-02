import sys


def help(version):
    print("""NAME
    phockup - v{version}

SYNOPSIS
    phockup INPUTDIR OUTPUTDIR [OPTIONS]

DESCRIPTION
    Media sorting tool to organize photos and videos from your camera in folders by year, month and day.
    The software will collect all files from the input directory and copy them to the output directory without
    changing the files content. It will only rename the files and place them in the proper directory for year, month and day.

ARGUMENTS
    INPUTDIR
        Specify the source directory where your photos are located

    OUTPUTDIR
        Specify the output directory where your photos should be exported

OPTIONS
    -d | --date
        Specify date format for OUTPUTDIR directories.
        You can choose different year format (e.g. 17 instead of 2017) or decide
        to skip the day directories and have all photos sorted in year/month.

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

    -h | --help
        Display this help.

    -m | --move
        Instead of copying the process will move all files from the INPUTDIR to the OUTPUTDIR.
        This is useful when working with a big collection of files and the
        remaining free space is not enough to make a copy of the INPUTDIR.

    -l | --link
        Instead of copying the process will make hard links to all files in INPUTDIR and place them in the OUTPUTDIR.
        This is useful when working with working structure and want to create YYYY/MM/DD structure to point to same files.


    -r | --regex
        Specify date format for date extraction from filenames
        if there is no EXIF date information.

        Example:
            {regex}
            can be used to extract the dafe from file names like
            the following IMG_27.01.2015-19.20.00.jpg.
""".format(version=version,
           regex="(?P<day>\d{2})\.(?P<month>\d{2})\.(?P<year>\d{4})[_-]?(?P<hour>\d{2})\.(?P<minute>\d{2})\.(?P<second>\d{2})"))
    sys.exit(2)
