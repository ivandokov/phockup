import sys
import os


class Printer(object):
    
    def __init__(self):
        self.quiet = False
        self.logfile = ""
    
    def line(self, message, skip_end=False):
        if not self.quiet:
            if skip_end:
                print(message, end="", flush=True)
            else:
                print(message)
        if self.logfile:
            if skip_end:
                print(message, end="", file=open(self.logfile, "a+"), flush=True)
            else:
                print(message, file=open(self.logfile, "a+"))

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
    
    def set_logfile(self, logfile):
        if logfile:
            self.logfile = os.path.expanduser(logfile)