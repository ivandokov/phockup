from subprocess import check_output, CalledProcessError
import json
import shlex
import sys


class Exif(object):
    def __init__(self, filename):
        self.filename = filename

    def data(self):
        try:
            if sys.platform == 'win32':
                exif_command = 'exiftool -time:all -mimetype -j "%s"' % self.filename
            else:
                exif_command = 'exiftool -time:all -mimetype -j %s' % shlex.quote(self.filename)
            data = check_output(exif_command, shell=True).decode('UTF-8')
            exif = json.loads(data)[0]
        except (CalledProcessError, UnicodeDecodeError):
            return None

        return exif
