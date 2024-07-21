from flasher import Flasher

import argparse

__version__ = '0.1.1'


def setool():
    parser = argparse.ArgumentParser(description='Ericsson and Sony Ericsson Tool')
    # Add the arguments
    parser.add_argument('-p', '--port', help='Set serial port')
    parser.add_argument('-b', '--baudrate', type=int, help='Set baudrate')
    parser.add_argument('-e', '--execute', type=str, help='Execute action')

    # Parse the command-line arguments
    args = parser.parse_args()

    # Check if no arguments provided
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    # Process the arguments
    flasher = Flasher(args.port, args.baudrate, args.execute)
    flasher.wait_for_answer()
    flasher.do_job()

if __name__ == '__main__':
    setool()
