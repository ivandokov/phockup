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
    dir3='output/unknown'
    assert os.path.isdir(dir1)
    assert os.path.isdir(dir2)
    assert os.path.isdir(dir3)
    assert len([name for name in os.listdir(dir1) if os.path.isfile(os.path.join(dir1, name))]) == 3
    assert len([name for name in os.listdir(dir2) if os.path.isfile(os.path.join(dir2, name))]) == 3
    assert len([name for name in os.listdir(dir3) if os.path.isfile(os.path.join(dir3, name))]) == 1
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
    Phockup('input', 'output').process_file("input/in_date_20170101_010101.jpg")
    assert os.path.isfile("output/2017/01/01/20170101-010101.jpg")
    shutil.rmtree('output', ignore_errors=True)


def test_handle_image_exif_date(mocker):
    shutil.rmtree('output', ignore_errors=True)
    mocker.patch.object(Phockup, 'check_directories')
    mocker.patch.object(Phockup, 'walk_directory')
    Phockup('input', 'output').process_file("input/in_exif.jpg")
    assert os.path.isfile("output/2017/01/01/20170101-010101.jpg")
    shutil.rmtree('output', ignore_errors=True)


def test_handle_image_xmp(mocker):
    shutil.rmtree('output', ignore_errors=True)
    mocker.patch.object(Phockup, 'check_directories')
    mocker.patch.object(Phockup, 'walk_directory')
    Phockup('input', 'output').process_file("input/in_xmp.jpg")
    assert os.path.isfile("output/2017/01/01/20170101-010101.jpg")
    assert os.path.isfile("output/2017/01/01/20170101-010101.jpg.xmp")
    shutil.rmtree('output', ignore_errors=True)


def test_handle_image_xmp_noext(mocker):
    shutil.rmtree('output', ignore_errors=True)
    mocker.patch.object(Phockup, 'check_directories')
    mocker.patch.object(Phockup, 'walk_directory')
    Phockup('input', 'output').process_file("input/in_xmp_noext.jpg")
    assert os.path.isfile("output/2017/01/01/20170101-010101.jpg")
    assert os.path.isfile("output/2017/01/01/20170101-010101.xmp")
    shutil.rmtree('output', ignore_errors=True)


def test_handle_image_unknown(mocker):
    shutil.rmtree('output', ignore_errors=True)
    mocker.patch.object(Phockup, 'check_directories')
    mocker.patch.object(Phockup, 'walk_directory')
    mocker.patch.object(Exif, 'data')
    Exif.data.return_value = {
        "MIMEType": "image/jpeg"
    }
    Phockup('input', 'output').process_file("input/in_unknown.jpg")
    assert os.path.isfile("output/unknown/in_unknown.jpg")
    shutil.rmtree('output', ignore_errors=True)


def test_handle_other(mocker):
    shutil.rmtree('output', ignore_errors=True)
    mocker.patch.object(Phockup, 'check_directories')
    mocker.patch.object(Phockup, 'walk_directory')
    Phockup('input', 'output').process_file("input/in_other.log")
    assert os.path.isfile("output/unknown/in_other.log")
    shutil.rmtree('output', ignore_errors=True)


def test_handle_move(mocker):
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
def test_handle_link():
    return


def test_handle_exists_same(mocker, capsys):
    shutil.rmtree('output', ignore_errors=True)
    mocker.patch.object(Phockup, 'check_directories')
    mocker.patch.object(Phockup, 'walk_directory')
    phockup = Phockup('input', 'output')
    phockup.process_file("input/in_exif.jpg")
    assert os.path.isfile("output/2017/01/01/20170101-010101.jpg")
    phockup.process_file("input/in_exif.jpg")
    assert 'skipped, duplicated file' in capsys.readouterr()[0]
    shutil.rmtree('output', ignore_errors=True)


    # with tempfile.TemporaryDirectory("phockup") as dir_name:
    #     output_dir = os.path.join(dir_name, "unknown")
    #
    #     os.makedirs(output_dir)
    #     shutil.copy2("input/in_other.log", output_dir)
    #
    #     handle_file("input/in_other.log", dir_name, "%Y/%m/%d", False, False)
    #     assert 'skipped, duplicated file' in capsys.readouterr()[0]


# def test_handle_exists_rename():
#     with tempfile.TemporaryDirectory("phockup") as dir_name:
#         output_dir = os.path.join(dir_name, "unknown")
#
#         os.makedirs(output_dir)
#         shutil.copy2("input/in_exif.jpg", os.path.join(output_dir, "in_other.log"))
#
#         handle_file("input/in_other.log", dir_name, "%Y/%m/%d", False, False)
#         assert os.path.isfile(os.path.join(dir_name, "unknown/in_other-2.log"))
#
#
# def test_handle_skip_xmp():
#     # Assume no errors == skip XMP file
#     handle_file("skip.xmp", "", "", False, False)
#
#
# def test_get_output_dir_no_write_access(mocker, capsys):
#     mocker.patch('os.makedirs', side_effect=Exception("No write access"))
#     mocker.patch('sys.exit')
#
#     get_output_dir(datetime(2017, 1, 1, 1, 1, 1), "foo", "%Y/%m/%d")
#
#     assert 'No write access' in capsys.readouterr()[0]
#     sys.exit.assert_called_once_with(0)
#
#
# def test_get_output_dir_strip_trailing_slash(mocker):
#     mocker.patch('os.makedirs')
#     mocker.patch('sys.exit')
#
#     assert "foo/unknown" == get_output_dir(datetime(2017, 1, 1, 1, 1, 1), "foo/", "%Y/%m/%d")
