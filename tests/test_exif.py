#!/usr/bin/env python3
import os
from subprocess import CalledProcessError

from src.exif import Exif

os.chdir(os.path.dirname(__file__))


def test_exif_reads_valid_file():
    exif = Exif("input/exif.jpg")
    assert exif.data()['CreateDate'] == '2017:01:01 01:01:01'


def test_exif_reads_files_with_illegal_characters():
    exif = Exif("input/!#$%'+-.^_`~.jpg")
    assert exif.data()['CreateDate'] == '2017:01:01 01:01:01'


def test_exif_reads_file_with_spaces_punctuation():
    exif = Exif("input/phockup's exif test.jpg")
    assert exif.data()['CreateDate'] == '2017:01:01 01:01:01'


def test_exif_handles_exception(mocker):
    mocker.patch('subprocess.check_output',
                 side_effect=CalledProcessError(2, 'cmd'))
    exif = Exif("not-existing.jpg")
    assert exif.data() is None
