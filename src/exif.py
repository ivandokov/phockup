from subprocess import check_output, CalledProcessError
import json
import shlex


class Exif(object):
    def __init__(self, file):
        self.file = file

    def data(self):
        try:
            data = check_output('exiftool -time:all -mimetype -j %s' % shlex.quote(self.file), shell=True).decode('UTF-8')
            exif = json.loads(data)[0]
        except (CalledProcessError, UnicodeDecodeError):
            return None

        return exif
