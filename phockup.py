#!/usr/bin/env python3
import getopt
import hashlib
import os
import shutil
import subprocess
import sys
import re
from datetime import datetime
from subprocess import check_output, CalledProcessError

version = '1.1.0'


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
        help_info()
    if outputdir == '':
        help_info()

    if not os.path.isdir(inputdir) or not os.path.exists(inputdir):
        error('Input directory does not exist')
    if not os.path.exists(outputdir):
        print('Output directory does not exist, creating now')
        os.makedirs(outputdir)

    ignored_files = ('.DS_Store', 'Thumbs.db')

    for root, _, files in os.walk(inputdir):
        for filename in files:
            try:
                if filename in ignored_files:
                    continue
                handle_file(os.path.join(root, filename), outputdir)
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
    try:
        data = check_output(['exiftool', file]).decode('UTF-8').strip().split("\\n")[0].split("\n")
        exif_data = {}
    except (CalledProcessError, UnicodeDecodeError):
        return None

    for row in data:
        opt = row.split(":")
        exif_data[opt[0].strip()] = ":".join(opt[1:]).strip()

    return exif_data


def get_date(file, exif_data):
    keys = ['Create Date', 'Date/Time Original']

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

        try:
            parsed_date_time = datetime.strptime(date, "%Y:%m:%d %H:%M:%S")
        except ValueError:
            try:
                parsed_date_time = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                parsed_date_time = None

        return {
            'date': parsed_date_time,
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


def get_output_dir(date, outputdir):
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


def is_image_or_video(exif_data):
    pattern = re.compile('^(image/.+|video/.+|application/vnd.adobe.photoshop)$')
    if pattern.match(exif_data['MIME Type']):
        return True
    return False


def handle_file(source_file, outputdir):
    if str.endswith(source_file, '.xmp'):
        return None

    print(source_file, end="", flush=True)

    exif_data = exif(source_file)

    if exif_data and is_image_or_video(exif_data):
        date = get_date(source_file, exif_data)
        output_dir = get_output_dir(date, outputdir)
        target_file_name = get_file_name(source_file, date).lower()
        target_file_path = '/'.join([output_dir, target_file_name])
    else:
        output_dir = get_output_dir(False, outputdir)
        target_file_name = os.path.basename(source_file)
        target_file_path = '/'.join([output_dir, target_file_name])

    suffix = 1
    target_file = target_file_path
    while True:
        if os.path.isfile(target_file):
            if sha256_checksum(source_file) == sha256_checksum(target_file):
                print(' => skipped, duplicated file')
                break
        else:
            shutil.copy2(source_file, target_file)
            print(' => %s' % target_file)
            handle_file_xmp(source_file, target_file_name, suffix, output_dir)
            break

        suffix += 1
        target_split = os.path.splitext(target_file_path)
        target_file = "%s-%d%s" % (target_split[0], suffix, target_split[1])


def handle_file_xmp(source_file, photo_name, suffix, exif_output_dir):
    xmp_original_with_ext = source_file + '.xmp'
    xmp_original_without_ext = os.path.splitext(source_file)[0] + '.xmp'

    suffix = '-%s' % suffix if suffix > 1 else ''

    if os.path.isfile(xmp_original_with_ext):
        xmp_original = xmp_original_with_ext
        xmp_target = '%s%s.xmp' % (photo_name, suffix)
    elif os.path.isfile(xmp_original_without_ext):
        xmp_original = xmp_original_without_ext
        xmp_target = '%s%s.xmp' % (os.path.splitext(photo_name)[0], suffix)
    else:
        xmp_original = None
        xmp_target = None

    if xmp_original:
        xmp_path = '/'.join([exif_output_dir, xmp_target])
        print('%s => %s' % (xmp_original, xmp_path))
        shutil.copy2(xmp_original, xmp_path)


def sha256_checksum(filename, block_size=65536):
    sha256 = hashlib.sha256()
    with open(filename, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            sha256.update(block)
    return sha256.hexdigest()


def error(message):
    print(message)
    sys.exit(2)


def help_info():
    error("""NAME
    phockup - v{version}

SYNOPSIS
    phockup -i inputdir -o outputdir

DESCRIPTION
    Phockup is a photos and videos sorting and backup tool written in Python 3.
    It organizes the media from your camera in a meaningful hierarchy and with proper file names.

ARGUMENTS
    -i|--input=
        Specify the source directory where your photos are located

    -o|--output=
        Specify the output directory where your photos should be exported
""".format(version=version))


if __name__ == '__main__':
    main(sys.argv[1:])
