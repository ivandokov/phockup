from subprocess import check_output, CalledProcessError


class Exif(object):
    def __init__(self, file):
        self.file = file

    def data(self):
        try:
            data = check_output(['exiftool', self.file]).decode('UTF-8').strip().split("\\n")[0].split("\n")
            exif = {}
        except (CalledProcessError, UnicodeDecodeError):
            return None

        for row in data:
            opt = row.split(":")
            exif[opt[0].strip()] = ":".join(opt[1:]).strip()

        return exif
