#!/usr/bin/env python3

from sepytool.flasher import Flasher

import argparse
import logging

__version__ = '0.1.1'

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s %(levelname)s] '
                           '%(message)s (%(filename)s:%(lineno)d)')

ap = argparse.ArgumentParser(prog='sepytool',
                             description='Ericsson and Sony Ericsson Tool')
sp = ap.add_subparsers(dest='command', metavar='command', required=True,
                       help='sub-command help')

# global arguments
ap.add_argument('-p', '--port', type=str, required=True,
                help='Set serial port (e.g. /dev/ttyUSB0 or COM1)')
ap.add_argument('-b', '--baudrate', type=int, default=115200,
                choices=[115200, 230400, 460800, 921600],
                help='Set baudrate (default: %(default)s)')
ap.add_argument('-v', '--verbose', action='count', default=0,
                help='print debug logging')

# identification
ident = sp.add_parser('identify',
                      help='Identify connected phone')

if __name__ == '__main__':
    # Parse the command-line arguments
    args = ap.parse_args()
    if args.verbose > 0:
        logging.root.setLevel(logging.DEBUG)
    # Process the arguments
    flasher = Flasher(args.port, args.baudrate, args.command)
    flasher.wait_for_answer()
    flasher.do_job()
