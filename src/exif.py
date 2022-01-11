import json
import shlex
import subprocess
import sys
import threading
from subprocess import CalledProcessError, check_output


class Exif(object):
    def __init__(self, filename):
        self.filename = filename

    def data(self):
        try:
            exif_command = self.get_exif_command(self.filename)
            if threading.current_thread() is threading.main_thread():
                data = check_output(exif_command, shell=True).decode('UTF-8')
            else:
                # Swallow stderr in the case that multiple threads are executing
                data = check_output(exif_command, shell=True, stderr=subprocess.DEVNULL).decode('UTF-8')
            exif = json.loads(data)[0]
        except (CalledProcessError, UnicodeDecodeError):
            return None

        return exif

    @staticmethod
    def get_exif_command(filename):
        # Handle all platform variations
        if sys.platform == 'win32':
            return f'exiftool -time:all -mimetype -j "{filename}"'
        return f'exiftool -time:all -mimetype -j {shlex.quote(filename)}'
