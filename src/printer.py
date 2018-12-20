import sys


class Printer(object):
    def line(self, message, skip_end=False):
        if skip_end:
            print(message, end="", flush=True)
        else:
            print(message)

    def error(self, message):
        self.line('')
        self.line(message)
        self.line('')
        sys.exit(1)

    def empty(self, times=1):
        for i in range(times):
            print('')
        return self
