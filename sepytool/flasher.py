import logging
import time

from .common import *
from .transport import Transport
from .sonyericsson import SonyEricsson

# local logger for this module
log = logging.getLogger(__name__)


class Flasher:
    def __init__(self, portname: str, baudrate: int = 115200, execute: str = "info"):
        self.port = portname
        self.baudrate = baudrate
        self.execute = execute

        self.detected_name = "n/a"
        self.detected_type = "n/a"

        self.transport = Transport(portname)
        self.transport.connect()

    def wait_for_answer(self):
        # Wait for power-up the phone
        log.info(f"Connecting {self.transport._sl.port} at {self.transport._sl.baudrate}")
        log.info("Powering phone")
        log.info("Please wait ...")

        response_mapping = {
            b"\x32": ("388", "Ericsson"),
            b"\x33": ("6xx/7xx", "Ericsson"),
            b"\x46": ("SH888/R250", "Ericsson"),
            b"\x48": ("S868/SH888/R190/R250/R290", "Ericsson"),
            b"\x54": ("T1x", "Ericsson"),
            b"\x55": ("A1018", "Ericsson"),
            b"\x56": ("T28/R320", "Ericsson"),
            b"\x4E": ("A2628/T20/T29", "Ericsson"),
            b"\x60": ("New A1018/T1x/T28/R310/R320", "Ericsson"),
            b"\x5A": ("", "SonyEricsson"),
        }

        while True:
            resp = self.transport.read_binary(1)  # Read 1 byte
            if resp == b">":
                next_resp = self.transport.read_binary(1)  # Read the next byte
                if next_resp == b">":
                    self.detected_name = '337'
                    self.detected_type = "Ericsson"
                    break
            elif resp in response_mapping:
                self.detected_name, self.detected_type = response_mapping[resp]
                break
            time.sleep(0.02)

        log.info(f"Detected {self.detected_type} {self.detected_name}")

    def do_job(self):
        if self.detected_type == "SonyEricsson":
            self.sonyericsson()
        else:
            print("Not Implemented(Yet =)")

    def sonyericsson(self,):
        se = SonyEricsson(self.baudrate, self.transport, self.execute)
        se.get_phone_info()
        se.print_phone_info()
        se.disconnect()

        print(self.execute)
