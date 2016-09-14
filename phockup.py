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

    files = (
        inputdir + '/**/*.nef',
        inputdir + '/**/*.NEF',
        inputdir + '/**/*.jp*g',
        inputdir + '/**/*.JP*G'
    )

    for file_regex in files:
        for file in glob.iglob(file_regex, recursive=True):
            try:
                handle_file(file, outputdir)
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
        subseconds = datestr[1] if 1 in datestr else ''

        return {
            'date': datetime.strptime(datestr[0], "%Y:%m:%d %H:%M:%S"),
            'subseconds': subseconds
        }
    else:
        # If missing datetime from exif data check if filename is in datetime format
        # E.g.: IMG_20160915_123456.jpg
        regex = re.compile('.*[_-](\d{8})[_-]?(\d{6})')
        matches = regex.findall(os.path.basename(file))

        if matches:
            datetimestr = ' '.join(list(matches[0]))

            return {
                'date': datetime.strptime(datetimestr, "%Y%m%d %H%M%S"),
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


def get_file_name(file, date):
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


def handle_file(file, outputdir):
    print(file, end="", flush=True)

    date = get_date(file)
    exif_output_dir = set_output_dir(date, outputdir)
    image_name = get_file_name(file, date)
    image_path = '/'.join([exif_output_dir, image_name])

    print(' => %s' % image_path)
    shutil.copy2(file, image_path)

    image_xmp = file + '.xmp'
    image_xmp_name = os.path.basename(file) + '.xmp'

    if os.path.isfile(image_xmp):
        image_xmp_path = '/'.join([exif_output_dir, image_xmp_name])
        print('%s => %s' % (image_xmp, image_xmp_path))
        shutil.copy2(image_xmp, image_xmp_path)


def error(message):
    print(message)
    sys.exit(2)


def help_info():
    error('phockup -i <inputdir> -o <outputdir>')


if __name__ == '__main__':
    main(sys.argv[1:])
