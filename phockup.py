#!/usr/bin/env python3
import getopt
import os
import re
import sys

from src.date import Date
from src.dependency import check_dependencies
from src.help import help
from src.phockup import Phockup
from src.printer import Printer

version = '1.5.7'
printer = Printer()


def main(argv):
    check_dependencies()

    move = False
    link = False
    date_regex = None
    dir_format = os.path.sep.join(['%Y', '%m', '%d'])
    original_filenames = False
    timestamp = False
    threads = 1

    try:
        opts, args = getopt.getopt(argv[2:], "d:r:mltoh", ["date=", "regex=", "move", "link", "original-names", "timestamp", "threads=", "help"])
    except getopt.GetoptError:
        help(version)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            help(version)
            sys.exit(2)

        if opt in ("-d", "--date"):
            if not arg:
                printer.error("Date format cannot be empty")
            dir_format = Date().parse(arg)

        if opt in ("-m", "--move"):
            move = True
            printer.line("Using move strategy")

        if opt in ("-l", "--link"):
            link = True
            printer.line("Using link strategy")

        if opt in ("-o", "--original-names"):
            original_filenames = True
            printer.line("Using original filenames")

        if opt in ("-r", "--regex"):
            try:
                date_regex = re.compile(arg)
            except:
                printer.error("Provided regex is invalid")
        
        if opt in ("-t", "--timestamp"):
            timestamp = True
            printer.line("Using file's timestamp")
        
        if opt in ("-x", "--threads"):
            if not arg:
                printer.error("Number of threads cannot be empty")
            threads = int(arg)
            printer.line("Using %s threads at most" % arg)

    if link and move:
        printer.error("Can't use move and link strategy together")

    if len(argv) < 2:
        help(version)
        sys.exit(2)

    return Phockup(
        argv[0], argv[1],
        dir_format=dir_format,
        move=move,
        link=link,
        date_regex=date_regex,
        original_filenames=original_filenames,
        timestamp=timestamp,
        threads=threads
    )


if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        printer.empty().line('Exiting...')
        sys.exit(0)
