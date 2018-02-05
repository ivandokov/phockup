import shutil
import sys
import os
import tempfile
from datetime import datetime

import pytest

from src.exif import Exif
from src.phockup import Phockup
from src.dependency import check_dependencies


def test_check_dependencies(mocker):
    mocker.patch('shutil.which', return_value='exiftool')
    mocker.patch('sys.exit')

    check_dependencies()
    assert not sys.exit.called


def test_check_dependencies_missing(mocker):
    mocker.patch('shutil.which', return_value=None)
    mocker.patch('sys.exit')

    check_dependencies()
    sys.exit.assert_called_once_with(2)


def test_exit_if_missing_input_directory(mocker):
    mocker.patch('os.makedirs')
    mocker.patch('sys.exit')
    Phockup('in', 'out')
    sys.exit.assert_called_once_with(2)


def test_removing_trailing_slash_for_input_output(mocker):
    mocker.patch('os.makedirs')
    mocker.patch('sys.exit')
    phockup = Phockup('in/', 'out/')
    assert phockup.input == 'in'
    assert phockup.output == 'out'


def test_error_for_missing_input_dir(mocker, capsys):
    mocker.patch('sys.exit')
    Phockup('in', 'out')
    sys.exit.assert_called_once_with(2)
    assert 'Input directory "in" does not exist' in capsys.readouterr()[0]


def test_error_for_no_write_access_when_creating_output_dir(mocker, capsys):
    mocker.patch.object(Phockup, 'walk_directory')
    mocker.patch('os.makedirs', side_effect=Exception("No write access"))
    mocker.patch('sys.exit')
    Phockup('input', '/root/phockup')
    sys.exit.assert_called_once_with(2)
    assert 'No write access' in capsys.readouterr()[0]


def test_walking_directory():
    shutil.rmtree('input/output', ignore_errors=True)
    Phockup('input', 'output')
    dir1='output/2017/01/01'
    dir2='output/2017/10/06'
    dir3='output/2018/02/05'
    dir4='output/unknown'
    assert os.path.isdir(dir1)
    assert os.path.isdir(dir2)
    assert os.path.isdir(dir3)
    assert os.path.isdir(dir4)
    assert len([name for name in os.listdir(dir1) if os.path.isfile(os.path.join(dir1, name))]) == 2
    assert len([name for name in os.listdir(dir2) if os.path.isfile(os.path.join(dir2, name))]) == 1
    assert len([name for name in os.listdir(dir3) if os.path.isfile(os.path.join(dir3, name))]) == 1
    assert len([name for name in os.listdir(dir4) if os.path.isfile(os.path.join(dir4, name))]) == 1
    shutil.rmtree('output', ignore_errors=True)


def test_is_image_or_video(mocker):
    mocker.patch.object(Phockup, 'check_directories')
    assert Phockup('in', '.').is_image_or_video("image/jpeg")
    assert Phockup('in', '.').is_image_or_video("video/mp4")
    assert not Phockup('in', '.').is_image_or_video("foo/bar")


def test_get_file_name(mocker):
    mocker.patch.object(Phockup, 'check_directories')
    mocker.patch.object(Phockup, 'walk_directory')
    date = {
        "date": datetime(2017, 1, 1, 1, 1, 1),
        "subseconds": "20"
    }

    assert Phockup('in', 'out').get_file_name("Bar/Foo.jpg", date) == "20170101-01010120.jpg"


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


def test_process_image_unknown(mocker):
    shutil.rmtree('output', ignore_errors=True)
    mocker.patch.object(Phockup, 'check_directories')
    mocker.patch.object(Phockup, 'walk_directory')
    mocker.patch.object(Exif, 'data')
    Exif.data.return_value = {
        "MIMEType": "image/jpeg"
    }
    Phockup('input', 'output').process_file("input/unknown.jpg")
    assert os.path.isfile("output/unknown/unknown.jpg")
    shutil.rmtree('output', ignore_errors=True)


def test_process_other(mocker):
    shutil.rmtree('output', ignore_errors=True)
    mocker.patch.object(Phockup, 'check_directories')
    mocker.patch.object(Phockup, 'walk_directory')
    Phockup('input', 'output').process_file("input/other.log")
    assert os.path.isfile("output/unknown/other.log")
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


@pytest.mark.skip(reason="Must be implemented")
def test_process_link():
    return


def test_process_exists_same(mocker, capsys):
    shutil.rmtree('output', ignore_errors=True)
    mocker.patch.object(Phockup, 'check_directories')
    mocker.patch.object(Phockup, 'walk_directory')
    phockup = Phockup('input', 'output')
    phockup.process_file("input/exif.jpg")
    assert os.path.isfile("output/2017/01/01/20170101-010101.jpg")
    phockup.process_file("input/exif.jpg")
    assert 'skipped, duplicated file' in capsys.readouterr()[0]
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