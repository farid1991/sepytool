from enum import Enum

import csv

#CERT LOADERS
DB2000_CERTLOADER_RED_CID00_R3L = "db2000_cid00_cert_r3l.bin"
DB2010_CERTLOADER_RED_CID01_R2E = "db2010_cid00_cert_r2e.bin"
DB2020_CERTLOADER_RED_CID01_P3G = "db2020_cid01_cert_p3g.bin"

#MEM PATCHLOADERS
DB2020_MEMPLOADER_RED_CID49_R2A006 = "db2020_cid49_mem_patcher_r2a006.bin"
DB2020_MEMPLOADER_RED_CID51_R2A006 = "db2020_cid51_mem_patcher_r2a006.bin"
DB2020_MEMPLOADER_RED_CID52_R2A006 = "db2020_cid52_mem_patcher_r2a006.bin"
DB2020_MEMPLOADER_RED_CID53_R2A012 = "db2020_cid53_mem_patcher_r2a012.bin"
DB2020_RECOVERY_LOADER_BLUE01_P3N = "db2020_cid01blue_recovery_p3n.bin"

#CHIP SELECT LOADERS
DB2000_CSLOADER_RED_CID49_P4K = "db2000_cid49red_cs_p4k.bin"
DB2000_CSLOADER_RED_CID49_P4L = "db2000_cid49red_cs_p4l.bin"

DB2010_CSLOADER_RED_CID29_P2C = "db2010_cid29red_cs_p2c.bin"
DB2010_CSLOADER_HAK_CID00_V23 = "db2010_cid00_cs_hack_v23.bin"
DB2010_CSLOADER_RED_CID49_P3T = "db2010_cid49red_cs_p3t.bin"
DB2010_CSLOADER_RED_CID49_R3A010 = "db2010_cid49red_cs_r3a010.bin"

DB2012_CSLOADER_RED_CID50_R3B009 = "db2012_cid50red_cs_r3b009.bin"
DB2012_CSLOADER_RED_CID51_R3B009 = "db2012_cid51red_cs_r3b009.bin"
DB2012_CSLOADER_RED_CID52_R3B009 = "db2012_cid52red_cs_r3b009.bin"
DB2012_CSLOADER_RED_CID53_R3B014 = "db2012_cid53red_cs_r3b014.bin"

DB2010_CSLOADER_BRN_CID49_V26 = "db2010_cid49brown_cs_v26.bin"
DB2010_CSLOADER_BRN_CID49_V23 = "db2010_cid49brown_cs_v23.bin"

DB2020_CSLOADER_RED_CID49_R3A009 = "db2020_cid49red_cs_r3a009.bin"
DB2020_CSLOADER_RED_CID51_R3A009 = "db2020_cid51red_cs_r3a009.bin"
DB2020_CSLOADER_RED_CID52_R3A009 = "db2020_cid52red_cs_r3a009.bin"

DB2020_CSLOADER_RED_CID49_R3A013 = "db2020_cid49red_cs_r3a013.bin"
DB2020_CSLOADER_RED_CID51_R3A013 = "db2020_cid51red_cs_r3a013.bin"
DB2020_CSLOADER_RED_CID52_R3A013 = "db2020_cid52red_cs_r3a013.bin"
DB2020_CSLOADER_RED_CID53_R3A013 = "db2020_cid53red_cs_r3a013.bin"

PNX5230_CSLOADER_RED_CID51_R3A015 = "PNX5230_cid51red_cs_r3a015.bin"
PNX5230_CSLOADER_RED_CID52_R3A015 = "PNX5230_cid52red_cs_r3a015.bin"
PNX5230_CSLOADER_RED_CID53_R3A016 = "pnx5230_cid53red_cs_r3a016.bin"

#FLASH LOADERS
DB2000_FLLOADER_RED_CID36_R3U = "db2000_cid36red_flash_r3u.bin"
DB2000_FLLOADER_RED_CID49_R2B = "db2000_cid49red_flash_r2b.bin"
DB2000_FLLOADER_BRW_CID49_R2A = "db2000_cid49brown_flash_r2a.bin"

DB2010_FLLOADER_RED_CID36_R2AB = "db2010_cid36red_flash_r2ab.bin"
DB2010_FLLOADER_RED_CID49_R2A003 = "db2010_cid49red_flash_r2a003.bin"
DB2010_FLLOADER_RED_CID49_R2B = "db2010_cid49red_flash_r2b.bin"

DB2010_FLLOADER_BRW_CID49_R5A = "db2010_cid49brown_flash_r5a.bin"
DB2010_FLLOADER_RED_CID49_R2B_DEN_PO = "db2010_cid49r_flash_r2b_den_po.bin"

DB2012_FLLOADER_RED_CID50_R1A002 = "db2012_cid50red_flash_r1a002.bin"
DB2012_FLLOADER_RED_CID51_R2B012 = "db2012_cid51red_flash_r2b012.bin"
DB2012_FLLOADER_RED_CID52_R2B012 = "db2012_cid52red_flash_r2b012.bin"
DB2012_FLLOADER_RED_CID53_R2B017 = "db2012_cid53red_flash_r2b017.bin"

DB2020_FLLOADER_RED_CID49_R2A001 = "db2020_cid49red_flash_r2a001.bin"
DB2020_FLLOADER_RED_CID51_R2A005 = "db2020_cid51red_flash_r2a005.bin"
DB2020_FLLOADER_RED_CID52_R2A005 = "db2020_cid52red_flash_r2a005.bin"
DB2020_FLLOADER_RED_CID53_R2A015 = "db2020_cid53red_flash_r2a015.bin"

PNX5230_FLLOADER_RED_CID51_R2A016 = "PNX5230_cid51red_flash_r2a016.bin"
PNX5230_FLLOADER_RED_CID52_R2A019 = "PNX5230_cid52red_flash_r2a019.bin"
PNX5230_FLLOADER_RED_CID53_R2A022 = "pnx5230_cid53red_flash_r2a022.bin"

#PRODUCT_ID LOADERS
DB2000_PILOADER_RED_CID00_R1F = "db2000_cid00_prodid_r1f.bin"
DB2000_PILOADER_RED_CID00_R2B = "db2000_cid00_prodid_r2b.bin"
DB2000_PILOADER_RED_CID03_P3B = "db2000_cid03_prodid_p3b.bin"
DB2010_PILOADER_RED_CID00_P3L = "db2010_cid00_prodid_p3l.bin"
DB2010_PILOADER_RED_CID00_R2F = "db2010_cid00_prodid_r2f.bin"
DB2010_PILOADER_RED_CID00_P4D = "db2010_cid00_prodid_p4d.bin"
DB2010_PILOADER_BROWN_CID49_R1A002 = "db2010_cid49brown_prodid_r1a002.bin"
DB2020_PILOADER_RED_CID01_P3J = "db2020_cid01_prodid_p3j.bin"
DB2020_PILOADER_RED_CID01_P3M = "db2020_cid01_prodid_p3m.bin"

#MISC LOADERS
DB2010_PATCH_R2E = "db2010_patch_r2e.bin"

DATA_HEADER = b'\x06'
DATA_TYPE = b'\x89'

DATA_EMPTY = b'\x00'

class LoaderType(Enum):
    LOADER_UNKNOWN = 0
    LOADER_PRODUCTION_ID = 1
    LOADER_CS = 2
    LOADER_CERT = 3
    LOADER_FLASH = 4
    LOADER_HACK = 5
    LOADER_RECOV = 6
    LOADER_PRE = 7

class Common:
    def get_flash_vendor(flashid):
        vendor_map = {
            0x01: "AMD",
            0x04: "Fujitsu",
            0x20: "STMicro",
            0x89: "Intel",
            0x1F: "Atmel",
            0x98: "Toshiba",
            0xBF: "SST",
        }
        vendor = vendor_map.get(flashid >> 8, "unknown")
        return vendor

    def getspeed_s_char(speed):
        speed_mapping = {
            9600: "0",
            19200: "1",
            38400: "2",
            57600: "3",
            115200: "4",
            230400: "5",
            460800: "6",
            921600: "7",
        }
        return speed_mapping.get(speed, "")

    def getlsb(a):
        return a & 0x0F

    def getmsb(a):
        return (a >> 4) & 0x0F

    def getlong(data):
        return (
            data[0]
            | (data[1] << 8)
            | (data[2] << 16)
            | (data[3] << 24)
        ) & 0xFFFFFFFF
    
    def imei_get_model_and_type(tac_input):
        # Read the CSV file
        with open('imei_table.csv', 'r') as file:
            reader = csv.DictReader(file)
            # Search for the TAC value in the CSV
            for row in reader:
                if row['TAC'] == tac_input:
                    model = row['Model']
                    type = row['Type']
                    return f"{model} {type}"
            else:
                return ""
