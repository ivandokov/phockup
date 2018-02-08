#!/usr/bin/env python3
import sys

from phockup import main
from src.printer import Printer

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        Printer().empty().line('Exiting...')
        sys.exit(0)
