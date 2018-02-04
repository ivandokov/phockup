import sys

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
    with mocker.patch.object(Phockup, 'walk_directory'):
        mocker.patch('os.makedirs', side_effect=Exception("No write access"))
        mocker.patch('sys.exit')
        Phockup('test_files', '/root/phockup')
        sys.exit.assert_called_once_with(2)
        assert 'No write access' in capsys.readouterr()[0]


def test_is_image_or_video(mocker):
    with mocker.patch.object(Phockup, 'check_directories'):
        assert Phockup('in', '.').is_image_or_video("image/jpeg")
        assert Phockup('in', '.').is_image_or_video("video/mp4")
        assert not Phockup('in', '.').is_image_or_video("foo/bar")


# def test_get_file_name():
#     date = {
#         "date": datetime(2017, 1, 1, 1, 1, 1),
#         "subseconds": "123"
#     }
#
#     assert get_file_name("Bar/Foo.jpg", date) == "20170101-010101123.jpg"
#
#
# def test_get_file_name_is_original_on_exception():
#     assert get_file_name("Bar/Foo.jpg", None) == "Foo.jpg"
#
#
# def test_handle_file_filename_date():
#     with tempfile.TemporaryDirectory("phockup") as dir_name:
#         handle_file("test_files/input/in_date_20170101_010101.jpg", dir_name, "%Y/%m/%d", False, False)
#         assert os.path.isfile(os.path.join(dir_name, "2017/01/01/20170101-010101.jpg"))
#
#
# def test_handle_image_exif_date():
#     with tempfile.TemporaryDirectory("phockup") as dir_name:
#         handle_file("test_files/input/in_exif.jpg", dir_name, "%Y/%m/%d", False, False)
#         assert os.path.isfile(os.path.join(dir_name, "2017/01/01/20170101-010101.jpg"))
#
#
# def test_handle_image_xmp():
#     with tempfile.TemporaryDirectory("phockup") as dir_name:
#         handle_file("test_files/input/in_xmp.jpg", dir_name, "%Y/%m/%d", False, False)
#         assert os.path.isfile(os.path.join(dir_name, "2017/01/01/20170101-010101.jpg"))
#         assert os.path.isfile(os.path.join(dir_name, "2017/01/01/20170101-010101.jpg.xmp"))
#
#
# def test_handle_image_xmp_noext():
#     with tempfile.TemporaryDirectory("phockup") as dir_name:
#         handle_file("test_files/input/in_xmp_noext.jpg", dir_name, "%Y/%m/%d", False, False)
#         assert os.path.isfile(os.path.join(dir_name, "2017/01/01/20170101-010101.jpg"))
#         assert os.path.isfile(os.path.join(dir_name, "2017/01/01/20170101-010101.xmp"))
#
#
# def test_handle_image_unknown():
#     with tempfile.TemporaryDirectory("phockup") as dir_name:
#         handle_file("test_files/input/in_unknown.jpg", dir_name, "%Y/%m/%d", False, False)
#         assert os.path.isfile(os.path.join(dir_name, "unknown/in_unknown.jpg"))
#
#
# def test_handle_other():
#     with tempfile.TemporaryDirectory("phockup") as dir_name:
#         handle_file("test_files/input/in_other.log", dir_name, "%Y/%m/%d", False, False)
#         assert os.path.isfile(os.path.join(dir_name, "unknown/in_other.log"))
#
#
# def test_handle_move():
#     with tempfile.TemporaryDirectory("phockup") as dir_name:
#         open(os.path.join(dir_name, "in_move.txt"), "w").close()
#         open(os.path.join(dir_name, "in_move.txt.xmp"), "w").close()
#
#         handle_file(os.path.join(dir_name, "in_move.txt"), dir_name, "%Y/%m/%d", True, False)
#
#         assert not os.path.isfile(os.path.join(dir_name, "in_move.txt"))
#         assert not os.path.isfile(os.path.join(dir_name, "in_move.txt.xmp"))
#
#         assert os.path.isfile(os.path.join(dir_name, "unknown/in_move.txt"))
#         assert os.path.isfile(os.path.join(dir_name, "unknown/in_move.txt.xmp"))
#
#
# def test_handle_exists_same(capsys):
#     with tempfile.TemporaryDirectory("phockup") as dir_name:
#         output_dir = os.path.join(dir_name, "unknown")
#
#         os.makedirs(output_dir)
#         shutil.copy2("test_files/input/in_other.log", output_dir)
#
#         handle_file("test_files/input/in_other.log", dir_name, "%Y/%m/%d", False, False)
#         assert 'skipped, duplicated file' in capsys.readouterr()[0]
#
#
# def test_handle_exists_rename():
#     with tempfile.TemporaryDirectory("phockup") as dir_name:
#         output_dir = os.path.join(dir_name, "unknown")
#
#         os.makedirs(output_dir)
#         shutil.copy2("test_files/input/in_exif.jpg", os.path.join(output_dir, "in_other.log"))
#
#         handle_file("test_files/input/in_other.log", dir_name, "%Y/%m/%d", False, False)
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
