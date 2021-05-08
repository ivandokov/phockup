import json
import shlex
import sys
from subprocess import CalledProcessError, check_output


class Exif(object):
    def __init__(self, filename):
        self.filename = filename

    def data(self):
        try:
            if sys.platform == 'win32':
                exif_command = f'exiftool -time:all -mimetype -j "{self.filename}"'
            else:
                exif_command = f'exiftool -time:all -mimetype -j {shlex.quote(self.filename)}'
            data = check_output(exif_command, shell=True).decode('UTF-8')
            exif = json.loads(data)[0]
        except (CalledProcessError, UnicodeDecodeError):
            return None

        return exif
