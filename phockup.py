#!/usr/bin/env python3
import getopt
import glob
import os
import shutil
import subprocess
import sys
import re
from datetime import datetime
from subprocess import check_output


def main(argv):
    check_dependencies()

    try:
        opts, args = getopt.getopt(argv, 'hi:o:', ['help', 'input=', 'output='])
    except getopt.GetoptError:
        help_info()

    inputdir = ''
    outputdir = ''

    for opt, arg in opts:
        if opt == '-h':
            help_info()
        elif opt in ('-i', '--input'):
            inputdir = arg
        elif opt in ('-o', '--output'):
            outputdir = arg

    if inputdir == '':
        help()
    if outputdir == '':
        help()

    if not os.path.isdir(inputdir) or not os.path.exists(inputdir):
        error('Input directory does not exist')
    if not os.path.exists(outputdir):
        print('Output directory does not exist, creating now')
        os.makedirs(outputdir)

    extensions = ['nef', 'NEF', 'cr2', 'CR2', 'crw', 'CRW', 'jp*g', 'JP*G']

    for ext in extensions:
        for file in glob.iglob(inputdir + '/**/*.' + ext, recursive=True):
            try:
                handle_photo(file, outputdir)
            except KeyboardInterrupt:
                print(' Exiting...')
                sys.exit(0)


def check_dependencies():
    if shutil.which('exiftool') is None:
        print('Exiftool is not installed. Visit http://www.sno.phy.queensu.ca/~phil/exiftool/')
        print('On Ubuntu you can `sudo apt-get install libimage-exiftool-perl`')
        print('On Mac you can `brew install exiftool`')
        sys.exit(2)


def exif(file):
    data = check_output(['exiftool', file]).decode('UTF-8').strip().split("\\n")[0].split("\n")
    exif_data = {}

    for row in data:
        opt = row.split(":")
        exif_data[opt[0].strip()] = ":".join(opt[1:]).strip()

    return exif_data


def get_date(file):
    keys = ['Create Date', 'Date/Time Original']

    exif_data = exif(file)
    datestr = None

    for key in keys:
        if key in exif_data:
            datestr = exif_data[key]
            break

    if datestr:
        datestr = datestr.split('.')
        date = datestr[0]

        if len(datestr) > 1:
            subseconds = datestr[1]
        else:
            subseconds = ''

        search = r'(.*)([+-]\d{2}:\d{2})'
        if re.search(search, date) is not None:
            date = re.sub(search, r'\1', date)

        return {
            'date': datetime.strptime(date, "%Y:%m:%d %H:%M:%S"),
            'subseconds': subseconds
        }
    else:
        # If missing datetime from exif data check if filename is in datetime format
        # E.g.: IMG_20160915_123456.jpg
        regex = re.compile('.*[_-](\d{8})[_-]?(\d{6})')
        matches = regex.findall(os.path.basename(file))

        if matches:
            try:
                datetimestr = ' '.join(list(matches[0]))
                date = datetime.strptime(datetimestr, "%Y%m%d %H%M%S")
            except ValueError:
                date = None

            if date:
                return {
                    'date': date,
                    'subseconds': ''
                }


def set_output_dir(date, outputdir):
    if outputdir.endswith('/'):
        outputdir = outputdir[:-1]

    if date:
        path = [
            outputdir,
            '%04d' % date['date'].year,
            '%02d' % date['date'].month,
            '%02d' % date['date'].day,
        ]
    else:
        path = [
            outputdir,
            'unknown',
        ]

    fullpath = '/'.join(path)

    subprocess.call(['mkdir', '-p', fullpath])

    return fullpath


def get_photo_name(file, date):
    if date:
        filename = [
            '%04d' % date['date'].year,
            '%02d' % date['date'].month,
            '%02d' % date['date'].day,
            '-',
            '%02d' % date['date'].hour,
            '%02d' % date['date'].minute,
            '%02d' % date['date'].second,
        ]

        if date['subseconds']:
            filename.append(date['subseconds'])

        return ''.join(filename) + os.path.splitext(file)[1]

    else:
        return os.path.basename(file)


def handle_photo(file, outputdir):
    print(file, end="", flush=True)

    date = get_date(file)
    exif_output_dir = set_output_dir(date, outputdir)
    photo_name = get_photo_name(file, date).lower()
    photo_path = '/'.join([exif_output_dir, photo_name])

    print(' => %s' % photo_path)
    shutil.copy2(file, photo_path)

    handle_photo_xmp(file, photo_name, exif_output_dir)


def handle_photo_xmp(file, photo_name, exif_output_dir):
    xmp_original_with_ext = file + '.xmp'
    xmp_original_without_ext = os.path.splitext(file)[0] + '.xmp'

    if os.path.isfile(xmp_original_with_ext):
        xmp_original = xmp_original_with_ext
        xmp_target = photo_name + '.xmp'
    elif os.path.isfile(xmp_original_without_ext):
        xmp_original = xmp_original_without_ext
        xmp_target = os.path.splitext(photo_name)[0] + '.xmp'
    else:
        xmp_original = None
        xmp_target = None

    if xmp_original:
        xmp_path = '/'.join([exif_output_dir, xmp_target])
        print('%s => %s' % (xmp_original, xmp_path))
        shutil.copy2(xmp_original, xmp_path)


def error(message):
    print(message)
    sys.exit(2)


def help_info():
    error('phockup -i <inputdir> -o <outputdir>')


if __name__ == '__main__':
    main(sys.argv[1:])
