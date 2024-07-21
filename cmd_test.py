from command import *

cmd = Command()
res1 = cmd.command_read_gdfs_var(0x04, 0x8F, 0xC)
print(res1)

data = b"\x00\x04\x8F\x0C"
res2 = cmd.create_binary_command(4, data, 9)
print(res2)
