import logging

from command import *
from common import *
from tqdm import tqdm
from transport import *

# local logger for this module
log = logging.getLogger(__name__)


class SonyEricsson:
    def __init__(self, baudrate: int, transport: Transport, execute: str):
        self.baudrate = baudrate

        self.chip_id = "N/A"
        self.protocol = 0
        self.platform = "N/A"
        self.new_security = False
        self.speed_char = Common.getspeed_s_char(baudrate)

        self.PHONE_binarymode = False
        self.PHONE_loadertype = LoaderType.LOADER_UNKNOWN
        self.PHONE_loaderunlocked = False
        self.PHONE_loaderGDFSstarted = False
        self.PHONE_loaderFSstarted = False
        self.PHONE_csloader = False
        self.PHONE_cert_already_sent = False
        self.user_code = None

        self.flash_chip = {"id": None, "vendor": None, "size": None}
        self.erom_data = {"cid": None, "color": None, "sign": None}
        self.otp_data = {"imei": None, "cid": None, "closed": None, "paf": None}

        self.phone_info = {
            "name": "N/A",
            "language": "N/A",
            "cda_article": "N/A",
            "cda_revision": "N/A",
            "default_article": "N/A",
            "default_version": "N/A",
        }

        self.transport = transport
        # self.transport = Transport(self.port_name)
        # self.transport.connect()

        self.cmd = Command()

    def disconnect(self):
        self.transport.disconnect()

    def wait_for_hdr(self):
        return self.transport.wait_for_byte(DATA_HEADER)

    def command_send_header(self):
        self.transport.write_binary(DATA_HEADER)

    def command_send_data(self, data):
        self.transport.write_binary(data)

    def command_send_header_and_data(self, data):
        self.transport.write_binary(DATA_HEADER + data)

    def send_binary_command_csloader(self, cmd, subcmd, data, datasize):
        csdata = bytearray(0x2000)
        csdata[0] = subcmd
        csdata[1 : datasize + 1] = data
        command = self.cmd.create_binary_command(cmd, csdata, datasize + 1)

        self.transport.write_binary(DATA_HEADER + command)

    def send_binary_command_and_data(self, cmd, data, datasize, total_bytes, description):
        buf = bytearray(0x1000)
        num = 0
        checksum = 0

        sent_bytes = 0
        do_once = True

        progress_bar = tqdm(
            total=total_bytes,
            unit="%",
            ncols=80,
            bar_format="{desc:<10} [{bar:50}] : {percentage:.0f}%",
        )
        progress_bar.set_description(f"{description}")

        while sent_bytes < total_bytes or do_once:
            max_bytes = 0x7FF
            do_once = False
            checksum = 0
            num = 0

            buf[num] = 0x89
            num += 1
            buf[num] = cmd
            num += 1

            bytes_to_send = total_bytes - sent_bytes

            if bytes_to_send > max_bytes:
                bytes_to_send = max_bytes

                buf[num] = (bytes_to_send + 1) & 0xFF
                num += 1
                buf[num] = ((bytes_to_send + 1) >> 8) & 0xFF
                num += 1

                buf[num] = 0x01  # continuebit = 01 = "more to come"
            else:
                buf[num] = (bytes_to_send + 1) & 0xFF
                num += 1
                buf[num] = ((bytes_to_send + 1) >> 8) & 0xFF
                num += 1

                buf[num] = 0x00  # continuebit = 00 = last block

            num += 1

            buf[num : num + bytes_to_send] = data[
                sent_bytes : sent_bytes + bytes_to_send
            ]
            num += bytes_to_send

            # calculate checksum
            for i in range(num):
                checksum ^= buf[i]

            checksum = (checksum + 7) & 0xFF

            buf[num] = checksum
            num += 1

            # send off chunk of data
            chunks = buf[:num]
            self.transport.send_buffer_to_serial(chunks, datasize)

            res = self.transport.read_binary(1)
            if res[0] != 0x06:
                log.debug("Command: Error {}", res)
                break

            sent_bytes += bytes_to_send
            progress_bar.update(bytes_to_send)

        progress_bar.close()

        return res[0]

    def wait_for_binaryanswer(self, loader_type):
        res = self.transport.read_binary()
        if loader_type == LoaderType.LOADER_CS:
            return res[4]
        return res[3]

    def loader_get_type(self, filename):
        if "_cs_" in filename:
            log.info("This is a CHIPSELECT loader")
            return LoaderType.LOADER_CS

        elif "_prodid_" in filename:
            log.info("This is a PRODUCTION_ID loader")
            return LoaderType.LOADER_PRODUCTION_ID

        elif "_cert_" in filename:
            log.info("This is a CERTIFICATE loader")
            return LoaderType.LOADER_CERT

        elif "_patch_" in filename:
            log.info("This is a PATCHED_CERT loader")
            return LoaderType.LOADER_CERT

        elif "_flash_" in filename:
            log.info("This is a FLASH loader")
            return LoaderType.LOADER_FLASH

        elif "_mem_patcher_" in filename:
            log.info("This is a MEM_PATCHER loader")
            return LoaderType.LOADER_FLASH

        log.info("This is a unknown loader")
        return LoaderType.LOADER_UNKNOWN

    def loader_sayhello(self, hello):
        log.info(f"hello: {hello}")

        if "CS_LOADER" in hello or "CSLOADER" in hello:
            # log.info("Applet code is a CHIPSELECT loader")
            self.PHONE_loadertype = LoaderType.LOADER_CS
        elif "PRODUCTION_ID" in hello or "PRODUCTIONID" in hello:
            # log.info("Applet code is a PRODUCTION_ID loader")
            self.PHONE_loadertype = LoaderType.LOADER_PRODUCTION_ID
        elif "CERTLOADER" in hello:
            # log.info("Applet code is a CERTIFICATE loader")
            self.PHONE_loadertype = LoaderType.LOADER_CERT
        elif "FLASHLOADER" in hello:
            # log.info("Applet code is a FLASH loader")
            self.PHONE_loadertype = LoaderType.LOADER_FLASH
        elif "MEM_PATCHER" in hello:
            # log.info("Applet code is a MEM_PATCHER loader")
            self.PHONE_loadertype = LoaderType.LOADER_FLASH
        else:
            # log.info("This is an unknown applet type")
            self.PHONE_loadertype = LoaderType.LOADER_UNKNOWN

    def loader_activate(self):
        if self.PHONE_loadertype == LoaderType.LOADER_CS:
            log.info("Activating CHIPSELECT loader...")
            self.send_binary_command_csloader(0x01, 0x09, DATA_EMPTY, 0)
            res = self.transport.read_binary()
            print(f"SIZE: {res[2:4]}")
            if res[0] != 0x06:
                raise ValueError(f"Failed Activating loader  {res}")

            log.info("Activating GDFS...")
            self.send_binary_command_csloader(0x04, 0x05, DATA_EMPTY, 0)
            res = self.transport.read_binary()
            print(f"SIZE: {res[2:4]}")
            if res[0] != 0x06:
                raise ValueError(f"Failed Activating GDFS  {res}")

            self.transport.wait_for_byte(DATA_TYPE)
            log.info("GDFS activated")

            self.transport.read_binary(5)
            self.PHONE_loaderGDFSstarted = True

            log.info("Checking if loader is unlocked...")

            gdfsvar = b"\x02\x8f\x0c"
            self.send_binary_command_csloader(0x04, 0x01, gdfsvar, 3)
            res = self.transport.read_binary()
            if res[0] == 0x1E:
                log.info("This loader is LOCKED")
            else:
                self.PHONE_loaderunlocked = True
                log.info("This loader is UNLOCKED")

        else:
            command = self.cmd.create_binary_command(0x0D, DATA_EMPTY, 0)
            self.command_send_header_and_data(command)
            res = self.transport.read_binary()

            if not self.flash_chip["id"]:
                flash_id = (res[5] << 8) | res[6]

                self.flash_chip["id"] = hex(flash_id)
                self.flash_chip["vendor"] = Common.get_flash_vendor(flash_id)

                if self.flash_chip["id"] in ["0x200d", "0x890d", "0x890d"]:
                    self.flash_chip["size"] = 0x20000

                elif self.flash_chip["id"] in ["0x2019", "0x897e"]:
                    self.flash_chip["size"] = 0x40000

                else:
                    self.flash_chip["size"] = 0

                log.info("Flash ID:{id} Size:{size} Manufacturer:{vendor}".format(**self.flash_chip))

    def loader_get_otpdata(self):
        command = self.cmd.create_binary_command(0x24, DATA_EMPTY, 0)
        self.command_send_header_and_data(command)
        res = self.transport.read_binary()

        self.otp_data = {
            "status": res[5],
            "closed": res[6],
            "cid": res[7] | (res[8] << 8),
            "paf": res[9],
            "imei": res[10:-1].decode(),
        }

        log.info("OTP IMEI:{imei} STATUS:{status} CID:{cid} CLOSED:{closed} PAF:{paf}".format(**self.otp_data))

    def loader_get_eromdata(self):
        command = self.cmd.create_binary_command(0x57, DATA_EMPTY, 0)
        self.command_send_header_and_data(command)
        res = self.transport.read_binary()

        if res[0] != 0x06:
            log.warning("Reading EROM values failed")

        self.erom_data["cid"] = int.from_bytes(res[0xE : 0xE + 4], byteorder="little")

        if res[6] & 1:
            self.erom_data["color"] = "Blue"
        elif res[6] & 2:
            self.erom_data["color"] = "Brown"
        elif res[6] & 4:
            self.erom_data["color"] = "Red"
        elif res[6] & 8:
            self.erom_data["color"] = "Black"
        else:
            self.erom_data["color"] = "Unknown"

        log.info("EROM Color:{color} CID:{cid}".format(**self.erom_data))

    def loader_activate_gdfs(self):
        log.info("Activating GDFS...")
        command = self.cmd.create_binary_command(0x22, DATA_EMPTY, 0)
        self.command_send_header_and_data(command)
        res = self.transport.read_binary_with_timeout(1)
        if res[0] != 0x06:
            raise ValueError(f"Failed Activating GDFS {res}")

        self.transport.wait_for_byte(DATA_TYPE)
        log.info("GDFS activated")
        self.PHONE_loaderGDFSstarted = True

        command = self.cmd.command_read_gdfs_var(0, 0x13, 0)
        self.command_send_header_and_data(command)
        self.transport.read_binary()

    def loader_read_gdfs_var(self, block, lsb, msb, encoding):
        if not self.PHONE_loaderGDFSstarted:
            self.loader_activate_gdfs()

        gdfs_var = ""

        command = self.cmd.command_read_gdfs_var(block, lsb, msb)
        self.command_send_header_and_data(command)
        res = self.transport.read_binary()
        if encoding == "utf-8":
            gdfs_var = res[6:-2].decode(encoding, errors="ignore")
        else:
            gdfs_var = res[6:19].decode(encoding, errors="ignore")

        return gdfs_var

    def start_loader(self):
        self.transport.write_binary(DATA_HEADER)

    def send_binaryloader_noactivate(self, fname):
        loader = "loader/" + fname
        log.info(f"Sending binary {loader}")

        loader_type = self.loader_get_type(loader)

        with open(loader, "rb") as file:
            buffer = file.read()

            QHsize = 0x380
            QAsize = (
                buffer[0x228]
                | (buffer[0x229] << 8)
                | (buffer[0x22A] << 16)
                | (buffer[0x22B] << 24)
            )
            QDsize = (
                buffer[0x2E8]
                | (buffer[0x2E9] << 8)
                | (buffer[0x2EA] << 16)
                | (buffer[0x2EB] << 24)
            )

            # Split the buffer into three parts: QH00, QA00, QD00
            qh00 = buffer[:QHsize]
            qa00 = buffer[QHsize : QHsize + QAsize]
            qd00 = buffer[QHsize + QAsize : QHsize + QAsize + QDsize]

            self.command_send_header()
            res1 = self.send_binary_command_and_data(
                0x3C, qh00, 0x380, QHsize, "header"
            )
            res2 = self.wait_for_binaryanswer(loader_type)
            if res1 != 0x06 and res2 != 0:
                raise ValueError(f"Header: Error {res}")

            self.command_send_header()
            res1 = self.send_binary_command_and_data(
                0x3C, qa00, 0x1000, QAsize, "prologue"
            )
            res2 = self.wait_for_binaryanswer(loader_type)
            if res1 != 0x06 and res2 != 0:
                raise ValueError(f"Prologue: Error  {res}")

            self.command_send_header()
            res1 = self.send_binary_command_and_data(0x3C, qd00, 0x1000, QDsize, "body")
            res2 = self.wait_for_binaryanswer(loader_type)
            if res1 != 0x06 and res2 != 0:
                raise ValueError(f"Payload: Error {res}")

        # Send 0x06 to start loader
        self.start_loader()
        self.transport.read_binary(1)

        if loader_type == LoaderType.LOADER_CS:
            if self.platform == "db2020":
                self.start_loader()

            res = self.transport.read_binary()
            hello = res[6:-1].decode()
        else:
            res = self.transport.read_binary()
            if self.erom_data["sign"] == "A1_DB2010_49_RED":
                hello = res[12:-1].decode()
            else:
                hello = res[6:-1].decode()

        self.loader_sayhello(hello)

    def send_qhloader_noactivate(self, fname):
        loader = "loader/" + fname
        log.info(f"Sending {loader}")

        self.loader_get_type(loader)

        with open(loader, "rb") as file:
            buffer = file.read()

            QHsize = 0x380
            QAsize = (
                buffer[0x228]
                | (buffer[0x229] << 8)
                | (buffer[0x22A] << 16)
                | (buffer[0x22B] << 24)
            )
            QDsize = (
                buffer[0x2E8]
                | (buffer[0x2E9] << 8)
                | (buffer[0x2EA] << 16)
                | (buffer[0x2EB] << 24)
            )

            # Split the buffer into three parts: QH00, QA00, QD00
            qh00 = buffer[:QHsize]
            qa00 = buffer[QHsize : QHsize + QAsize]
            qd00 = buffer[QHsize + QAsize : QHsize + QAsize + QDsize]

            self.transport.send_command("QH00")
            self.transport.transceive("EsB")
            self.transport.send_payload_to_serial(
                qh00, chunk_size=QHsize, name="header"
            )
            self.transport.transceive("EhM")

            self.transport.send_command("QA00")
            self.transport.send_payload_to_serial(
                qa00, chunk_size=0x800, name="prologue"
            )
            self.transport.transceive("EaTEbS")

            self.transport.send_command("QD00")
            self.transport.send_payload_to_serial(qd00, chunk_size=0x800, name="data")
            self.transport.transceive("EdQ")

        log.info("Device now in binary mode!")
        self.PHONE_binarymode = True

        res = self.transport.read_binary()
        hello = res[6:-1].decode()

        self.loader_sayhello(hello)

    def send_binaryloader(self, filename):
        self.send_binaryloader_noactivate(filename)
        self.loader_activate()

    def send_qhloader(self, filename):
        self.send_qhloader_noactivate(filename)
        self.loader_activate()
        self.loader_get_otpdata()

    def send_loader(self, filename):
        if self.PHONE_binarymode:
            self.send_binaryloader(filename)
        else:
            self.send_qhloader(filename)

    def update_baudrate(self):
        if self.platform == "pnx5230":
            return

        if self.platform == "db2000" and self.baudrate > 460800:
            log.info(f"Decrease baudrate")
            self.baudrate = 460800
            self.transport.send_command("S6")
            self.transport.set_baudrate(460800)
        else:
            self.transport.send_command("S" + self.speed_char)
            self.transport.set_baudrate(self.baudrate)

        self.transport.reset_io_buffer()
        log.info(f"Set baudrate to {self.baudrate}")

    def get_platform_type(self, chip_id):
        if self.new_security == True:
            return "db2012"

        platforms = {
            "5B07": "db1000",
            "5B08": "db1000",
            "5C06": "avr2001",
            "7100": "db2000",
            "8000": "db2010",
            "8040": "db2010",
            "8900": "arm2001",
            "9900": "db2020",
            "D000": "pnx5230",
            "C802": "db3150",
        }
        return platforms.get(chip_id, "Unknown")

    def send_question_mark(self):
        self.transport.send_command("?")
        bin = self.transport.read_binary()
        res = bytearray(bin)

        if res[3] == 0xFF:
            res[3] = 0x00

        if res[4] == 0x01:
            log.info("NEW SECURITY PHONE DETECTED! SWITCHING...")
            self.new_security = True

        self.chip_id = f"{res[0]:02X}{res[1]:02X}"
        self.protocol = float(f"{res[2]:02X}.{res[3]:02X}")
        self.platform = self.get_platform_type(self.chip_id)

        log.info(f"ChipID:{self.chip_id} Platform:{self.platform} Protocol:{self.protocol}")

    def erom_read_var(self, cmd):
        hdr = "ICG1".encode()
        command = hdr + cmd
        self.transport.write_binary(command)
        res = self.transport.read_binary_with_timeout()
        log.info("erom_read_var({}): {}", command, res)

    def prepare_pnx5230(self):
        cmd = b"\x00\x06\x00"
        self.erom_read_var(cmd)
        cmd = b"\x00\x0E\x00"
        self.erom_read_var(cmd)
        cmd = b"\x00\x1C\x00"
        self.erom_read_var(cmd)
        cmd = b"\x01\x51\x08"
        self.erom_read_var(cmd)
        cmd = b"\x00\x13\x00"
        self.erom_read_var(cmd)
        cmd = b"\x00\x18\x00"
        self.erom_read_var(cmd)
        cmd = b"\x00\xAA\x00"
        self.erom_read_var(cmd)
        cmd = b"\x02\x15\x0E"
        self.erom_read_var(cmd)
        cmd = b""
        self.erom_read_var(cmd)
        cmd = b"\x00\x13\x00"
        self.erom_read_var(cmd)
        cmd = b"\x02\xBB\x0D"
        self.erom_read_var(cmd)

    def prepare_erom(self):
        if self.platform == "db2020":
            return

        if self.platform != "pnx5230":
            self.transport.send_command("IC10")  # SIGN
            res = self.transport.read_binary()
            null_byte_index = res[2:].find(DATA_EMPTY)
            self.erom_data["sign"] = res[2 : 2 + null_byte_index].decode()

        self.transport.send_command("IC30")  # COLOR
        res = self.transport.read_binary()

        if res[2] & 1:
            self.erom_data["color"] = "Blue"
        elif res[2] & 2:
            self.erom_data["color"] = "Brown"
        elif res[2] & 4:
            self.erom_data["color"] = "Red"
        elif res[2] & 8:
            self.erom_data["color"] = "Black"
        else:
            self.erom_data["color"] = "Unknown"

        self.transport.send_command("IC40")  # CID
        res = self.transport.read_binary()
        self.erom_data["cid"] = int.from_bytes(res[2 : 2 + 4], byteorder="little")

        log.info("Signature: {sign}".format(**self.erom_data))
        log.info("EROM Color:{color} CID:{cid}".format(**self.erom_data))

        if self.platform == "pnx5230":
            self.prepare_pnx5230()

    def binary_mode_db2000(self):
        cid = self.erom_data["cid"]

        if cid < 36:
            self.send_loader(DB2000_PILOADER_RED_CID00_R1F)
        else:
            self.send_loader(DB2000_PILOADER_RED_CID03_P3B)

    def binary_mode_db2010(self):
        cid = self.erom_data["cid"]
        color = self.erom_data["color"]

        if color == "Red":
            if self.PHONE_csloader:
                self.send_loader(DB2010_PILOADER_RED_CID00_R2F)
            else:
                self.send_loader(DB2010_PILOADER_RED_CID00_P3L)
        elif color == "Brown":
            if cid <= 36:
                self.send_loader(DB2010_PILOADER_RED_CID00_P3L)
            else:
                self.send_loader(DB2010_PILOADER_BROWN_CID49_R1A002)

    def enter_binary_mode(self):
        if self.platform == "db2000":
            self.send_loader(DB2000_PILOADER_RED_CID03_P3B)

        elif self.platform == "db2010":
            self.binary_mode_db2010()

        elif self.platform == "db2012":
            self.send_loader(DB2010_PILOADER_RED_CID00_P4D)

        elif self.platform == "db2020":
            self.send_loader(DB2020_PILOADER_RED_CID01_P3J)

        else:
            raise ValueError("Platform is not supported...")

        if self.PHONE_binarymode:
            self.loader_get_eromdata()

    def get_phone_info(self):
        self.send_question_mark()
        if self.protocol == 3.01:
            self.prepare_erom()
            self.update_baudrate()
            self.identify()
            self.shutdown()

        else:
            log.info("Protocol is not supported...")
            exit

    def print_phone_info(self):
        log.info("Phone info")
        log.info(f"Name: {self.phone_info['name']}")
        log.info(f"Language: {self.phone_info['language']}")
        log.info(f"CDA Article: {self.phone_info['cda_article']}")
        log.info(f"CDA Revision: {self.phone_info['cda_revision']}")
        log.info(f"Default Article: {self.phone_info['default_article']}")
        log.info(f"Default Version: {self.phone_info['default_version']}")

        if self.platform != "db2020":
            log.info(f"Usercode: {self.user_code}")

    def identify(self):
        if self.platform == "pnx5230":
            log.info("Platform is not supported...")
            exit

        self.enter_binary_mode()

        if self.platform == "db2000":
            gdfs_values = {
                "name": (0x04, 0x8F, 0x0C, "utf-16le"),
                "language": (0x04, 0xBB, 0x0C, "utf-8"),
                "cda_article": (0x04, 0xBC, 0x0C, "utf-8"),
                "cda_revision": (0x04, 0xBD, 0x0C, "utf-8"),
                "default_article": (0x04, 0xBE, 0x0C, "utf-8"),
                "default_version": (0x04, 0xBF, 0x0C, "utf-8"),
            }

        elif self.platform in ["db2010", "db2012"]:
            gdfs_values = {
                "name": (0x02, 0x8F, 0x0C, "utf-16le"),
                "language": (0x02, 0xBB, 0x0C, "utf-8"),
                "cda_article": (0x02, 0xBC, 0x0C, "utf-8"),
                "cda_revision": (0x02, 0xBD, 0x0C, "utf-8"),
                "default_article": (0x02, 0xBE, 0x0C, "utf-8"),
                "default_version": (0x02, 0xBF, 0x0C, "utf-8"),
            }

        elif self.platform == "db2020":
            gdfs_values = {
                "name": (0x02, 0xBB, 0x0D, "utf-16le"),
                "language": (0x02, 0xE7, 0x0D, "utf-8"),
                "cda_article": (0x02, 0xE8, 0x0D, "utf-8"),
                "cda_revision": (0x02, 0xE9, 0x0D, "utf-8"),
                "default_article": (0x02, 0xEA, 0x0D, "utf-8"),
                "default_version": (0x02, 0xEB, 0x0D, "utf-8"),
            }

        log.info("Reading Phone info")

        for attribute, params in gdfs_values.items():
            value = self.loader_read_gdfs_var(*params)
            self.phone_info[attribute] = value

        if self.platform in ["db2000", "db2010", "db2012"]:
            self.detect_lockcode()
            # self.get_simlock_status()

        log.info("Done")

    def unlock_usercode_db2020(self):
        self.prepare_csloader()

        log.info("Resetting Lock Code...")
        self.send_binary_command_csloader(0x01, 0x0D, DATA_EMPTY, 0)
        res = self.transport.read_binary()
        if res[0] != 0x06:
            raise ValueError("Failed")

        res = self.transport.read_binary()
        log.info("Lock Code...Reset to '0000'!")

        # shutdown
        self.shutdown_csloader()

    def get_simlock_status(self):
        # if not self.PHONE_loaderGDFSstarted:
        #     self.loader_activate_gdfs()

        command = self.cmd.command_read_gdfs_var(0x0, 0x6, 0)
        self.command_send_header_and_data(command)
        res = self.transport.read_binary()

    def detect_lockcode(self):
        if not self.PHONE_loaderGDFSstarted:
            self.loader_activate_gdfs()

        command = self.cmd.command_read_gdfs_var(0x00, 0x0E, 0x00)
        self.command_send_header_and_data(command)
        res = self.transport.read_binary()

        usercode_len = res[0x67]
        usercode = ""

        for i in range(usercode_len):
            usercode += "{:X}{:X}".format(
                Common.getlsb(res[0x68 + i]), Common.getmsb(res[0x68 + i])
            )

        if usercode_len > 0:
            self.user_code = usercode[:usercode_len]

    def break_db2010_cid36(self):
        log.info("Bypassing RSA...")
        self.send_loader(DB2010_CERTLOADER_RED_CID01_R2E)

        loader = "loader/" + DB2010_PATCH_R2E
        log.info(f"Sending {loader}")

        self.loader_get_type(loader)

        with open(loader, "rb") as file:
            data = file.read()

            command = self.cmd.create_binary_command(0x3E, data, len(data))
            self.command_send_header_and_data(command)
            res = self.transport.read_binary(1)
            if res[0] != 0x06:
                log.debug("Cannot break-in the sec unit. {}", res)

        res = self.transport.read_binary()
        hello = res[6:-1].decode()
        self.loader_sayhello(hello)

        log.info("RSA security disabled!")

    def csloader_backup_gdfs(self):
        if not self.PHONE_loaderGDFSstarted or not self.PHONE_loaderunlocked:
            return

        log.debug("Backing up the GDFS...")
        self.send_binary_command_csloader(0x04, 0x02, DATA_EMPTY, 0)
        res = self.transport.read_binary()

        if res[0] != 0x06:
            log.debug("Backup: Error")
            return

        buffer = bytearray(0x10000)
        bytesread = 0

        buffer[bytesread:] = self.transport.wait_for_byte(DATA_TYPE)

        bytesread += 1
        buffer[bytesread:] = self.transport.read_binary(9)

        datasize = (buffer[bytesread + 2] | (buffer[bytesread + 3] << 8)) + 1
        log.debug("GDFS size: {}", datasize)

        offs = 6
        varcounts = int.from_bytes(buffer[offs : offs + 4], byteorder="little")
        log.debug("Stated variables: {}", varcounts)

        bytesread = 10
        chunkcount = 0
        with open("gdfs.bin", "wb") as file:
            for _ in range(varcounts):
                buffer[bytesread:] = self.transport.read_binary(1)

                if bytesread >= datasize:
                    log.debug("Variables found at {}", chunkcount)

                    file.write(buffer[6:bytesread])

                    self.command_send_header()
                    bytesread = 0
                    buffer[bytesread:] = self.transport.read_binary(6)
                    datasize = (
                        buffer[bytesread + 2] | (buffer[bytesread + 3] << 8)
                    ) + 1
                    log.debug("GDFS size: {}", datasize)

                    bytesread = 6
                    chunkcount = 0
                    buffer[bytesread:] = self.transport.read_binary(1)

                bytesread += 1
                buffer[bytesread:] = self.transport.read_binary(6)

                bytesread += 2
                varsize = int.from_bytes(
                    buffer[bytesread : bytesread + 4], byteorder="little"
                )

                bytesread += 4
                buffer[bytesread:] = self.transport.read_binary(varsize)
                bytesread += varsize

                chunkcount += 1

            log.debug("Variables found: {}", chunkcount)
            file.write(buffer[6:bytesread])

            log.debug("Wrote backup to gdfs.bin")
            log.debug("GDFS was backed up successfully!")

    def csloader_db2010(self):
        cid = self.erom_data["cid"]
        color = self.erom_data["color"]

        if color == "Red":
            if cid == 29:
                self.send_loader(DB2010_CSLOADER_RED_CID29_P2C)

            elif cid == 36:
                self.break_db2010_cid36()
                self.send_loader(DB2010_CSLOADER_HAK_CID00_V23)

            elif cid == 49:
                if self.flash_chip["id"] in ["0x897e", "0x2019"]:
                    self.send_loader(DB2010_CSLOADER_RED_CID49_R3A010)
                else:
                    self.send_loader(DB2010_CSLOADER_RED_CID49_P3T)

        elif color == "Brown":
            if cid == 29:
                self.send_loader(DB2010_CSLOADER_RED_CID29_P2C)

            elif cid == 36:
                self.break_db2010_cid36()
                self.send_loader(DB2010_CSLOADER_HAK_CID00_V23)

            elif cid == 49:
                if self.flash_chip["id"] in ["0x897e", "0x2019"]:
                    self.send_loader(DB2010_CSLOADER_BRN_CID49_V26)
                else:
                    self.send_loader(DB2010_CSLOADER_BRN_CID49_V23)

    def csloader_db2012(self):
        cid = self.erom_data["cid"]

        if cid == 50:
            self.send_loader(DB2012_FLLOADER_RED_CID50_R1A002)
            self.send_loader(DB2012_CSLOADER_RED_CID50_R3B009)

        elif cid == 51:
            self.send_loader(DB2012_FLLOADER_RED_CID51_R2B012)
            self.send_loader(DB2012_CSLOADER_RED_CID51_R3B009)

        elif cid == 52:
            self.send_loader(DB2012_FLLOADER_RED_CID52_R2B012)
            self.send_loader(DB2012_CSLOADER_RED_CID52_R3B009)

        elif cid == 53:
            self.send_loader(DB2012_FLLOADER_RED_CID53_R2B017)
            self.send_loader(DB2012_CSLOADER_RED_CID53_R3B014)

    def csloader_db2020(self):
        if self.PHONE_cert_already_sent:
            return

        cid = self.erom_data["cid"]

        if cid == 49:
            self.send_loader(DB2020_MEMPLOADER_RED_CID49_R2A006)
            self.send_loader(DB2020_CSLOADER_RED_CID49_R3A013)
            self.PHONE_cert_already_sent = True

        elif cid == 51:
            self.send_loader(DB2020_MEMPLOADER_RED_CID51_R2A006)
            self.send_loader(DB2020_CSLOADER_RED_CID51_R3A013)
            self.PHONE_cert_already_sent = True

        elif cid == 52:
            self.send_loader(DB2020_MEMPLOADER_RED_CID52_R2A006)
            self.send_loader(DB2020_CSLOADER_RED_CID52_R3A013)
            self.PHONE_cert_already_sent = True

        elif cid == 53:
            log.info(f"CID:{cid} not supported")

        else:
            log.info(f"Unknown CID:{cid}")

    def prepare_csloader(self):
        self.PHONE_csloader = True
        self.enter_binary_mode()

        if self.platform == "db2010":
            self.csloader_db2010()
        elif self.platform == "db2012":
            self.csloader_db2012()
        elif self.platform == "db2020":
            self.csloader_db2020()

    def shutdown_csloader(self):
        log.info("Terminating GDFS Access...")
        self.send_binary_command_csloader(0x01, 0x08, DATA_EMPTY, 0)
        res = self.transport.read_binary()
        if res[0] != 0x06:
            raise ValueError("Failed")

    def read_gdfs(self):
        self.prepare_csloader()
        self.csloader_backup_gdfs()
        self.shutdown_csloader()

    def shutdown(self):
        command = self.cmd.create_binary_command(0x14, DATA_EMPTY, 0)
        self.command_send_header_and_data(command)  # Shutdown
        self.transport.read_binary()
        log.info("Shutdown phone")
