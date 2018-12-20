import shutil

from src.printer import Printer


def check_dependencies():
    if shutil.which('exiftool') is None:
        Printer().error('Exiftool is not installed. Visit http://www.sno.phy.queensu.ca/~phil/exiftool/')