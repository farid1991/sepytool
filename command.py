from common import *

class Command:
    def __init__(self):
        pass

    def create_binary_command(self, cmd, data, datasize):
        buf = bytearray(datasize + 7 + 64)
        num = 0
        i = 0
        checksum = 0

        buf[num] = 0x89
        num += 1
        buf[num] = cmd
        num += 1

        buf[num] = datasize & 0xFF
        num += 1
        buf[num] = (datasize >> 8) & 0xFF
        num += 1

        buf[num : num + datasize] = data
        num += datasize

        for i in range(num):
            checksum ^= buf[i]

        buf[num] = (checksum + 7) & 0xFF  # Ensure the value is within 0 to 255
        num += 1

        return buf[:num]

    def command_read_gdfs_var(self, block, lsb, msb):
        data = bytearray([block, lsb, msb])
        return self.create_binary_command(0x21, data, 3)

    def command_create_csloader(self, cmd, subcmd, csdata, datasize):
        data = bytearray(0x2000)
        data[0] = subcmd
        data[1 : datasize + 1] = data
        return self.create_binary_command(cmd, csdata, datasize+1)
