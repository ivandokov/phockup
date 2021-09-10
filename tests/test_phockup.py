#!/usr/bin/env python3
import logging
import os
import shutil
import sys
from datetime import datetime

import pytest

from src.dependency import check_dependencies
from src.exif import Exif
from src.phockup import Phockup

os.chdir(os.path.dirname(__file__))


def test_check_dependencies(mocker):
    mocker.patch('shutil.which', return_value='exiftool')
    mocker.patch('sys.exit')

    check_dependencies()
    assert not sys.exit.called


def test_check_dependencies_missing(mocker):
    mocker.patch('shutil.which', return_value=None)
    mocker.patch('sys.exit')

    with pytest.raises(Exception, match="Exiftool is not installed. \
Visit http://www.sno.phy.queensu.ca/~phil/exiftool/"):
        check_dependencies()


def test_exception_if_missing_input_directory(mocker):
    mocker.patch('os.makedirs')
    mocker.patch('sys.exit')

    with pytest.raises(RuntimeError, match="Input directory 'in' does not exist"):
        Phockup('in', 'out')


def test_exception_if_input_not_directory(mocker):
    mocker.patch('os.makedirs')
    mocker.patch('sys.exit')

    with pytest.raises(RuntimeError, match="Input directory 'input/exif.jpg' is not a directory"):
        Phockup('input/exif.jpg', 'out')


def test_removing_trailing_slash_for_input_output(mocker):
    mocker.patch('os.makedirs')
    mocker.patch('sys.exit')
    mocker.patch.object(Phockup, 'check_directories')
    if sys.platform == 'win32':
        phockup = Phockup('in\\', 'out\\')
    else:
        phockup = Phockup('in/', 'out/')
    assert phockup.input_dir == 'in'
    assert phockup.output_dir == 'out'


def test_exception_for_no_write_access_when_creating_output_dir(mocker):
    mocker.patch.object(Phockup, 'walk_directory')
    with pytest.raises(OSError, match="Cannot create output '/root/phockup' \
directory. No write access!"):
        Phockup('input', '/root/phockup')


def test_walking_directory():
    shutil.rmtree('output', ignore_errors=True)
    Phockup('input', 'output')
    dir1 = 'output/2017/01/01'
    dir2 = 'output/2017/10/06'
    dir3 = 'output/unknown'
    dir4 = 'output/2018/01/01/'
    assert os.path.isdir(dir1)
    assert os.path.isdir(dir2)
    assert os.path.isdir(dir3)
    assert os.path.isdir(dir4)
    assert len([name for name in os.listdir(dir1) if
                os.path.isfile(os.path.join(dir1, name))]) == 3
    assert len([name for name in os.listdir(dir2) if
                os.path.isfile(os.path.join(dir2, name))]) == 1
    assert len([name for name in os.listdir(dir3) if
                os.path.isfile(os.path.join(dir3, name))]) == 1
    assert len([name for name in os.listdir(dir4) if
                os.path.isfile(os.path.join(dir4, name))]) == 1
    shutil.rmtree('output', ignore_errors=True)


def test_dry_run():
    shutil.rmtree('output', ignore_errors=True)
    Phockup('input', 'output', dry_run=True)
    assert not os.path.isdir('output')
    dir1 = 'output/2017/01/01'
    dir2 = 'output/2017/10/06'
    dir3 = 'output/unknown'
    dir4 = 'output/2018/01/01/'
    assert not os.path.isdir(dir1)
    assert not os.path.isdir(dir2)
    assert not os.path.isdir(dir3)
    assert not os.path.isdir(dir4)


def test_progress():
    shutil.rmtree('output', ignore_errors=True)
    Phockup('input', 'output', progress=True)
    dir1 = 'output/2017/01/01'
    dir2 = 'output/2017/10/06'
    dir3 = 'output/unknown'
    dir4 = 'output/2018/01/01/'
    assert os.path.isdir(dir1)
    assert os.path.isdir(dir2)
    assert os.path.isdir(dir3)
    assert os.path.isdir(dir4)
    assert len([name for name in os.listdir(dir1) if
                os.path.isfile(os.path.join(dir1, name))]) == 3
    assert len([name for name in os.listdir(dir2) if
                os.path.isfile(os.path.join(dir2, name))]) == 1
    assert len([name for name in os.listdir(dir3) if
                os.path.isfile(os.path.join(dir3, name))]) == 1
    assert len([name for name in os.listdir(dir4) if
                os.path.isfile(os.path.join(dir4, name))]) == 1
    shutil.rmtree('output', ignore_errors=True)


def test_get_file_type(mocker):
    mocker.patch.object(Phockup, 'check_directories')
    assert Phockup('in', '.').get_file_type("image/jpeg")
    assert Phockup('in', '.').get_file_type("video/mp4")
    assert not Phockup('in', '.').get_file_type("foo/bar")


def test_get_file_name(mocker):
    mocker.patch.object(Phockup, 'check_directories')
    mocker.patch.object(Phockup, 'walk_directory')
    date = {
        "date": datetime(2017, 1, 1, 1, 1, 1),
        "subseconds": "20"
    }

    assert Phockup('in', 'out').get_file_name("Bar/Foo.jpg", date) == \
        "20170101-01010120.jpg"


def test_get_file_name_is_original_on_exception(mocker):
    mocker.patch.object(Phockup, 'check_directories')
    mocker.patch.object(Phockup, 'walk_directory')
    assert Phockup('in', 'out').get_file_name("Bar/Foo.jpg", None) == "Foo.jpg"


def test_process_file_with_filename_date(mocker):
    shutil.rmtree('output', ignore_errors=True)
    mocker.patch.object(Phockup, 'check_directories')
    mocker.patch.object(Phockup, 'walk_directory')
    mocker.patch.object(Exif, 'data')
    Exif.data.return_value = {
        "MIMEType": "image/jpeg"
    }
    Phockup('input', 'output').process_file("input/date_20170101_010101.jpg")
    assert os.path.isfile("output/2017/01/01/20170101-010101.jpg")
    shutil.rmtree('output', ignore_errors=True)


def test_process_link_to_file_with_filename_date(mocker):
    shutil.rmtree('output', ignore_errors=True)
    mocker.patch.object(Phockup, 'check_directories')
    mocker.patch.object(Phockup, 'walk_directory')
    Phockup('input', 'output').process_file(
        "input/link_to_date_20170101_010101.jpg")
    assert os.path.isfile("output/2017/01/01/20170101-010101.jpg")
    shutil.rmtree('output', ignore_errors=True)


def test_process_broken_link(mocker, caplog):
    shutil.rmtree('output', ignore_errors=True)
    mocker.patch.object(Phockup, 'check_directories')
    mocker.patch.object(Phockup, 'walk_directory')
    with caplog.at_level(logging.WARNING):
        Phockup('input', 'output').process_file("input/not_a_file.jpg")
    assert 'skipped, no such file or directory' in caplog.text
    shutil.rmtree('output', ignore_errors=True)


def test_process_broken_link_move(mocker, caplog):
    shutil.rmtree('output', ignore_errors=True)
    mocker.patch.object(Phockup, 'check_directories')
    mocker.patch.object(Phockup, 'walk_directory')
    phockup = Phockup('input', 'output', move=True)
    phockup.process_file("input/not_a_file.jpg")
    with caplog.at_level(logging.WARNING):
        Phockup('input', 'output').process_file("input/not_a_file.jpg")
    assert 'skipped, no such file or directory' in caplog.text
    shutil.rmtree('output', ignore_errors=True)


def test_process_image_exif_date(mocker):
    shutil.rmtree('output', ignore_errors=True)
    mocker.patch.object(Phockup, 'check_directories')
    mocker.patch.object(Phockup, 'walk_directory')
    Phockup('input', 'output').process_file("input/exif.jpg")
    assert os.path.isfile("output/2017/01/01/20170101-010101.jpg")
    shutil.rmtree('output', ignore_errors=True)


def test_process_image_xmp(mocker):
    shutil.rmtree('output', ignore_errors=True)
    mocker.patch.object(Phockup, 'check_directories')
    mocker.patch.object(Phockup, 'walk_directory')
    Phockup('input', 'output').process_file("input/xmp.jpg")
    assert os.path.isfile("output/2017/01/01/20170101-010101.jpg")
    assert os.path.isfile("output/2017/01/01/20170101-010101.jpg.xmp")
    shutil.rmtree('output', ignore_errors=True)


def test_process_image_xmp_noext(mocker):
    shutil.rmtree('output', ignore_errors=True)
    mocker.patch.object(Phockup, 'check_directories')
    mocker.patch.object(Phockup, 'walk_directory')
    Phockup('input', 'output').process_file("input/xmp_noext.jpg")
    assert os.path.isfile("output/2017/01/01/20170101-010101.jpg")
    assert os.path.isfile("output/2017/01/01/20170101-010101.xmp")
    shutil.rmtree('output', ignore_errors=True)


def test_process_image_xmp_ext_and_noext(mocker):
    shutil.rmtree('output', ignore_errors=True)
    mocker.patch.object(Phockup, 'check_directories')
    mocker.patch.object(Phockup, 'walk_directory')
    Phockup('input', 'output').process_file("input/xmp_ext.jpg")
    assert os.path.isfile("output/2017/01/01/20170101-010101.jpg")
    assert os.path.isfile("output/2017/01/01/20170101-010101.xmp")
    assert os.path.isfile("output/2017/01/01/20170101-010101.jpg.xmp")
    shutil.rmtree('output', ignore_errors=True)


def test_process_image_unknown(mocker):
    shutil.rmtree('output', ignore_errors=True)
    mocker.patch.object(Phockup, 'check_directories')
    mocker.patch.object(Phockup, 'walk_directory')
    mocker.patch.object(Exif, 'data')
    Exif.data.return_value = {
        "MIMEType": "image/jpeg"
    }
    Phockup('input', 'output').process_file("input/UNKNOWN.jpg")
    assert os.path.isfile("output/unknown/unknown.jpg")
    shutil.rmtree('output', ignore_errors=True)


def test_process_other(mocker):
    shutil.rmtree('output', ignore_errors=True)
    mocker.patch.object(Phockup, 'check_directories')
    mocker.patch.object(Phockup, 'walk_directory')
    Phockup('input', 'output').process_file("input/other.txt")
    assert os.path.isfile("output/unknown/other.txt")
    shutil.rmtree('output', ignore_errors=True)


def test_process_move(mocker):
    shutil.rmtree('output', ignore_errors=True)
    mocker.patch.object(Phockup, 'check_directories')
    mocker.patch.object(Phockup, 'walk_directory')
    mocker.patch.object(Exif, 'data')
    Exif.data.return_value = {
        "MIMEType": "image/jpeg"
    }
    phockup = Phockup('input', 'output', move=True)
    open("input/tmp_20170101_010101.jpg", "w").close()
    open("input/tmp_20170101_010101.xmp", "w").close()
    phockup.process_file("input/tmp_20170101_010101.jpg")
    phockup.process_file("input/tmp_20170101_010101.xmp")
    assert not os.path.isfile("input/tmp_20170101_010101.jpg")
    assert not os.path.isfile("input/tmp_20170101_010101.xmp")
    assert os.path.isfile("output/2017/01/01/20170101-010101.jpg")
    assert os.path.isfile("output/2017/01/01/20170101-010101.xmp")
    shutil.rmtree('output', ignore_errors=True)


def test_process_link(mocker):
    shutil.rmtree('output', ignore_errors=True)
    mocker.patch.object(Phockup, 'check_directories')
    mocker.patch.object(Phockup, 'walk_directory')
    mocker.patch.object(Exif, 'data')
    Exif.data.return_value = {
        "MIMEType": "image/jpeg"
    }
    phockup = Phockup('input', 'output', link=True)
    open("input/tmp_20170101_010101.jpg", "w").close()
    open("input/tmp_20170101_010101.xmp", "w").close()
    phockup.process_file("input/tmp_20170101_010101.jpg")
    phockup.process_file("input/tmp_20170101_010101.xmp")
    assert os.path.isfile("input/tmp_20170101_010101.jpg")
    assert os.path.isfile("input/tmp_20170101_010101.xmp")
    assert os.path.isfile("output/2017/01/01/20170101-010101.jpg")
    assert os.path.isfile("output/2017/01/01/20170101-010101.xmp")
    shutil.rmtree('output', ignore_errors=True)
    os.remove("input/tmp_20170101_010101.jpg")
    os.remove("input/tmp_20170101_010101.xmp")


def test_process_exists_same(mocker, caplog):
    shutil.rmtree('output', ignore_errors=True)
    mocker.patch.object(Phockup, 'check_directories')
    mocker.patch.object(Phockup, 'walk_directory')
    phockup = Phockup('input', 'output')
    phockup.process_file("input/exif.jpg")
    assert os.path.isfile("output/2017/01/01/20170101-010101.jpg")
    with caplog.at_level(logging.INFO):
        phockup.process_file("input/exif.jpg")
    assert 'skipped, duplicated file' in caplog.text
    shutil.rmtree('output', ignore_errors=True)


def test_process_same_date_different_files_rename(mocker):
    shutil.rmtree('output', ignore_errors=True)
    mocker.patch.object(Phockup, 'check_directories')
    mocker.patch.object(Phockup, 'walk_directory')
    phockup = Phockup('input', 'output')
    phockup.process_file("input/exif.jpg")
    mocker.patch.object(Exif, 'data')
    Exif.data.return_value = {
        "MIMEType": "image/jpeg",
        "CreateDate": "2017:01:01 01:01:01"
    }
    phockup.process_file("input/date_20170101_010101.jpg")
    assert os.path.isfile("output/2017/01/01/20170101-010101-2.jpg")
    shutil.rmtree('output', ignore_errors=True)


def test_process_skip_xmp(mocker):
    # Assume no errors == skip XMP file
    mocker.patch.object(Phockup, 'check_directories')
    mocker.patch.object(Phockup, 'walk_directory')
    phockup = Phockup('input', 'output')
    phockup.process_file("skip.xmp")


def test_process_skip_ignored_file():
    shutil.rmtree('output', ignore_errors=True)
    shutil.rmtree('input_ignored', ignore_errors=True)
    os.mkdir('input_ignored')
    open("input_ignored/.DS_Store", "w").close()
    Phockup('input_ignored', 'output')
    assert not os.path.isfile("output/unknown/.DS_Store")
    shutil.rmtree('output', ignore_errors=True)
    shutil.rmtree('input_ignored', ignore_errors=True)


def test_keep_original_filenames(mocker):
    shutil.rmtree('output', ignore_errors=True)
    mocker.patch.object(Phockup, 'check_directories')
    mocker.patch.object(Phockup, 'walk_directory')
    Phockup('input', 'output', original_filenames=True).process_file(
        "input/exif.jpg")
    assert os.path.isfile("output/2017/01/01/exif.jpg")
    assert not os.path.isfile("output/2017/01/01/20170101-010101.jpg")
    shutil.rmtree('output', ignore_errors=True)


def test_keep_original_filenames_and_filenames_case(mocker):
    shutil.rmtree('output', ignore_errors=True)
    mocker.patch.object(Phockup, 'check_directories')
    mocker.patch.object(Phockup, 'walk_directory')
    Phockup('input', 'output', original_filenames=True).process_file(
        "input/UNKNOWN.jpg")
    assert os.path.isfile("output/2017/10/06/UNKNOWN.jpg")
    assert 'unknown.jpg' not in os.listdir("output/2017/10/06")
    shutil.rmtree('output', ignore_errors=True)


def test_maxdepth_zero():
    shutil.rmtree('output', ignore_errors=True)
    Phockup('input', 'output', maxdepth=0)
    dir1 = 'output/2017/01/01'
    dir2 = 'output/2017/10/06'
    dir3 = 'output/unknown'
    assert os.path.isdir(dir1)
    assert os.path.isdir(dir2)
    assert os.path.isdir(dir3)
    assert len([name for name in os.listdir(dir1) if
                os.path.isfile(os.path.join(dir1, name))]) == 3
    assert len([name for name in os.listdir(dir2) if
                os.path.isfile(os.path.join(dir2, name))]) == 1
    assert len([name for name in os.listdir(dir3) if
                os.path.isfile(os.path.join(dir3, name))]) == 1
    shutil.rmtree('output', ignore_errors=True)


def test_maxdepth_one():
    shutil.rmtree('output', ignore_errors=True)
    Phockup('input', 'output', maxdepth=1)
    dir1 = 'output/2017/01/01'
    dir2 = 'output/2017/10/06'
    dir3 = 'output/unknown'
    dir4 = 'output/2018/01/01/'
    assert os.path.isdir(dir1)
    assert os.path.isdir(dir2)
    assert os.path.isdir(dir3)
    assert os.path.isdir(dir4)
    assert len([name for name in os.listdir(dir1) if
                os.path.isfile(os.path.join(dir1, name))]) == 3
    assert len([name for name in os.listdir(dir2) if
                os.path.isfile(os.path.join(dir2, name))]) == 1
    assert len([name for name in os.listdir(dir3) if
                os.path.isfile(os.path.join(dir3, name))]) == 1
    assert len([name for name in os.listdir(dir4) if
                os.path.isfile(os.path.join(dir4, name))]) == 1
    shutil.rmtree('output', ignore_errors=True)
