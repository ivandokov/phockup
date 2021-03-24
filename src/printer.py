import sys


class Printer(object):
    
    def __init__(self):
        self.quiet = False
    
    def line(self, message, skip_end=False):
        if not self.quiet:
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

    def should_print(self, quiet):
        self.quiet = quiet
