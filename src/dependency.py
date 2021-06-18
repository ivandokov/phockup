import logging
import shutil

logger = logging.getLogger('phockup')


def check_dependencies():
    if shutil.which('exiftool') is None:
        raise Exception("Exiftool is not installed.\
 Visit http://www.sno.phy.queensu.ca/~phil/exiftool/")
