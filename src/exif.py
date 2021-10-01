import json
import shlex
import sys
import threading
from subprocess import CalledProcessError, check_output


class Exif(object):
    def __init__(self, filename):
        self.filename = filename

    def data(self):
        try:
            exif_command = self.get_exif_command(self.filename)
            data = check_output(exif_command, shell=True,).decode('UTF-8')
            exif = json.loads(data)[0]
        except (CalledProcessError, UnicodeDecodeError):
            return None

        return exif

    @staticmethod
    def get_exif_command(filename):
        # Handle all platform and concurrency variations
        if sys.platform == 'win32':
            if threading.current_thread() is threading.main_thread():
                # Single threaded, so don't swallow error messages
                exif_command = f'exiftool -time:all -mimetype -j "{filename}"'
            else:
                # Executing on a thread other than the main thread, so swallow stderr
                exif_command = f'exiftool -time:all -mimetype -j "{filename}" 2>nul'
        else:
            if threading.current_thread() is threading.main_thread():
                exif_command = f'exiftool -time:all -mimetype -j {shlex.quote(filename)}'
            else:
                exif_command = f'exiftool -time:all -mimetype -j {shlex.quote(filename)} 2>/dev/null'
        return exif_command
