import os
import sys
import shutil
import tempfile
import re

from datetime import datetime

from phockup import (
    check_dependencies,
    get_date,
    get_file_name,
    get_output_dir,
    handle_file,
    is_image_or_video,
    parse_date_format,
    main
)


def test_parse_date_format_valid():
    """Test that parse_date_format returns a valid format for strftime"""
    datetime.strftime(
        datetime.now(),
        parse_date_format("YYYY YY m MM M DDD DD \\ /")
    )


def test_get_date_exif():
    assert get_date("Foo.jpg", {
        "Create Date": "2017-01-01 01:01:01"
    }) == {
        "date": datetime(2017, 1, 1, 1, 1, 1),
        "subseconds": ""
    }


def test_get_date_exif_strip_timezone():
    assert get_date("Foo.jpg", {
        "Create Date": "2017-01-01 01:01:01-02:00"
    }) == {
        "date": datetime(2017, 1, 1, 1, 1, 1),
        "subseconds": ""
    }


def test_get_date_exif_colon():
    assert get_date("Foo.jpg", {
        "Create Date": "2017:01:01 01:01:01"
    }) == {
        "date": datetime(2017, 1, 1, 1, 1, 1),
        "subseconds": ""
    }


def test_get_date_exif_subseconds():
    assert get_date("Foo.jpg", {
        "Create Date": "2017-01-01 01:01:01.123"
    }) == {
        "date": datetime(2017, 1, 1, 1, 1, 1),
        "subseconds": "123"
    }


def test_get_date_exif_invalid():
    assert get_date("Foo.jpg", {
        "Create Date": "Invalid"
    }) == {
        "date": None,
        "subseconds": ""
    }


def test_get_date_filename():
    assert get_date("IMG_20170101_010101.jpg", {}) == {
        "date": datetime(2017, 1, 1, 1, 1, 1),
        "subseconds": ""
    }


def test_get_date_filename_invalid():
    assert get_date("IMG_20170101_999999.jpg", {}) is None


def test_get_date_none_on_no_info():
    assert get_date("Foo.jpg", {}) is None


def test_get_date_none_on_no_error():
    assert get_date("IMG_2017_01.jpg", {}) is None


def test_get_date_custom_regex():
    """
    A valid regex with a matching filename. Returns a datetime.
    """
    date_regex = re.compile("(?P<day>\d{2})\.(?P<month>\d{2})\.(?P<year>\d{4})[_-]?(?P<hour>\d{2})\.(?P<minute>\d{2})\.(?P<second>\d{2})")
    filename = "IMG_27.01.2015-19.20.00.jpg"
    assert get_date(filename, {}, date_regex) == {
        "date": datetime(2015, 1, 27, 19, 20, 00),
        "subseconds": ""
    }


def test_get_date_custom_regex_invalid():
    """
    A valid regex with a matching filename.
    Return none because there is not enougth information in the filename.
    """
    date_regex = re.compile("(?P<hour>\d{2})\.(?P<minute>\d{2})\.(?P<second>\d{2})")
    filename = "19.20.00.jpg"
    assert get_date(filename, {}, date_regex) is None


def test_get_date_custom_regex_no_match():
    """
    A valid regex with a non-matching filename.
    """
    date_regex = re.compile("(?P<day>\d{2})\.(?P<month>\d{2})\.(?P<year>\d{4})[_-]?(?P<hour>\d{2})\.(?P<minute>\d{2})\.(?P<second>\d{2})")
    filename = "Foo.jpg"
    assert get_date(filename, {}, date_regex) is None


def test_is_image_or_video():
    assert is_image_or_video({"MIME Type": "image/jpeg"})
    assert is_image_or_video({"MIME Type": "video/mp4"})

    assert not is_image_or_video({"MIME Type": "foo/bar"})


def test_get_file_name():
    date = {
        "date": datetime(2017, 1, 1, 1, 1, 1),
        "subseconds": "123"
    }

    assert get_file_name("Bar/Foo.jpg", date) == "20170101-010101123.jpg"


def test_get_file_name_is_original_on_exception():
    assert get_file_name("Bar/Foo.jpg", None) == "Foo.jpg"


def test_handle_file_filename_date():
    with tempfile.TemporaryDirectory("phockup") as dir_name:
        handle_file("test_files/input/in_date_20170101_010101.jpg", dir_name, "%Y/%m/%d", False, False)
        assert os.path.isfile(os.path.join(dir_name, "2017/01/01/20170101-010101.jpg"))


def test_handle_image_exif_date():
    with tempfile.TemporaryDirectory("phockup") as dir_name:
        handle_file("test_files/input/in_exif.jpg", dir_name, "%Y/%m/%d", False, False)
        assert os.path.isfile(os.path.join(dir_name, "2017/01/01/20170101-010101.jpg"))


def test_handle_image_xmp():
    with tempfile.TemporaryDirectory("phockup") as dir_name:
        handle_file("test_files/input/in_xmp.jpg", dir_name, "%Y/%m/%d", False, False)
        assert os.path.isfile(os.path.join(dir_name, "2017/01/01/20170101-010101.jpg"))
        assert os.path.isfile(os.path.join(dir_name, "2017/01/01/20170101-010101.jpg.xmp"))


def test_handle_image_xmp_noext():
    with tempfile.TemporaryDirectory("phockup") as dir_name:
        handle_file("test_files/input/in_xmp_noext.jpg", dir_name, "%Y/%m/%d", False, False)
        assert os.path.isfile(os.path.join(dir_name, "2017/01/01/20170101-010101.jpg"))
        assert os.path.isfile(os.path.join(dir_name, "2017/01/01/20170101-010101.xmp"))


def test_handle_image_unknown():
    with tempfile.TemporaryDirectory("phockup") as dir_name:
        handle_file("test_files/input/in_unknown.jpg", dir_name, "%Y/%m/%d", False, False)
        assert os.path.isfile(os.path.join(dir_name, "unknown/in_unknown.jpg"))


def test_handle_other():
    with tempfile.TemporaryDirectory("phockup") as dir_name:
        handle_file("test_files/input/in_other.log", dir_name, "%Y/%m/%d", False, False)
        assert os.path.isfile(os.path.join(dir_name, "unknown/in_other.log"))


def test_handle_move():
    with tempfile.TemporaryDirectory("phockup") as dir_name:
        open(os.path.join(dir_name, "in_move.txt"), "w").close()
        open(os.path.join(dir_name, "in_move.txt.xmp"), "w").close()

        handle_file(os.path.join(dir_name, "in_move.txt"), dir_name, "%Y/%m/%d", True, False)

        assert not os.path.isfile(os.path.join(dir_name, "in_move.txt"))
        assert not os.path.isfile(os.path.join(dir_name, "in_move.txt.xmp"))

        assert os.path.isfile(os.path.join(dir_name, "unknown/in_move.txt"))
        assert os.path.isfile(os.path.join(dir_name, "unknown/in_move.txt.xmp"))


def test_handle_exists_same(capsys):
    with tempfile.TemporaryDirectory("phockup") as dir_name:
        output_dir = os.path.join(dir_name, "unknown")

        os.makedirs(output_dir)
        shutil.copy2("test_files/input/in_other.log", output_dir)

        handle_file("test_files/input/in_other.log", dir_name, "%Y/%m/%d", False, False)
        assert 'skipped, duplicated file' in capsys.readouterr()[0]


def test_handle_exists_rename():
    with tempfile.TemporaryDirectory("phockup") as dir_name:
        output_dir = os.path.join(dir_name, "unknown")

        os.makedirs(output_dir)
        shutil.copy2("test_files/input/in_exif.jpg", os.path.join(output_dir, "in_other.log"))

        handle_file("test_files/input/in_other.log", dir_name, "%Y/%m/%d", False, False)
        assert os.path.isfile(os.path.join(dir_name, "unknown/in_other-2.log"))


def test_handle_skip_xmp():
    # Assume no errors == skip XMP file
    handle_file("skip.xmp", "", "", False, False)


def test_get_output_dir_no_write_access(mocker, capsys):
    mocker.patch('os.makedirs', side_effect=Exception("No write access"))
    mocker.patch('sys.exit')

    get_output_dir(datetime(2017, 1, 1, 1, 1, 1), "foo", "%Y/%m/%d")

    assert 'No write access' in capsys.readouterr()[0]
    sys.exit.assert_called_once_with(0)


def test_get_output_dir_strip_trailing_slash(mocker):
    mocker.patch('os.makedirs')
    mocker.patch('sys.exit')

    assert "foo/unknown" == get_output_dir(datetime(2017, 1, 1, 1, 1, 1), "foo/", "%Y/%m/%d")


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


def test_handle_move_removes_empty_dirs():
     tempdir = tempfile.mkdtemp(suffix='first')
     firstnesteddir = os.path.join(tempdir, 'one')
     nesteddir = os.path.join(firstnesteddir, 'two', 'three')
     os.makedirs(nesteddir, exist_ok=True)

     open(os.path.join(nesteddir, "move.txt"), "w").close()

     # we need to do removeal per dir, not in handle_file, (for now, before refactoring into classes)
     main([firstnesteddir, tempdir, '-m'])

     assert not os.path.isfile(os.path.join(nesteddir, "move.txt"))

     assert os.path.isfile(os.path.join(tempdir, "unknown/move.txt"))

     # shutil.rmtree(tempdir)
     assert not os.path.isdir(firstnesteddir)
