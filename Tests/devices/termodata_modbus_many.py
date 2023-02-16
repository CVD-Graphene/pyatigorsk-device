"""
Termodats
"""

import minimalmodbus as mm
import time

reg = 377
REG_ON_OFF = 384

par = 0.00  # 0 -- off, 0.01 -- on
ON = 1  # 0.01
OFF = 0
TARGET_POINT = 0.0  # TARGET DEGREE

# rrg.write_register(REG_ON_OFF, 0.0, 2)  # ON/OFF
# print("on/off: " + str(rrg.read_register(REG_ON_OFF, 2)))
# rrg.write_register(371, 1.0, 1)  # 50.5 degree  # /= 10 from real (want 100C - need 10.0)

READ_TARGET_1 = 369  # 171h *= 10 (10.0 is 100C)
READ_TARGET_2 = 48  # 30h *= 10
SPEED_REG = 377


instruments = {i: mm.Instrument('/dev/ttyUSB1', i, debug=False) for i in [1, 2, 3]}
for i, inst in instruments.items():
    inst.serial.baudrate = 9600
    inst.serial.timeout = 0.2
    inst.mode = mm.MODE_ASCII
    print(f"on/off [{i}]: " + str(inst.read_register(REG_ON_OFF, 1)))
    inst.write_register(REG_ON_OFF, ON, 1)  # ON/OFF
    print(f"on/off 2 [{i}]: " + str(inst.read_register(REG_ON_OFF, 1)))


for i in range(20):
    s = ""
    for i, inst in instruments.items():
        print(f"T{i} = " + str(inst.read_register(368, 1)) + " | " +
              str(inst.read_register(READ_TARGET_1, 1)))
    # print("Tmax = " + str(int(str(rrg.read_register(549, 2)).replace('.',''))/10))
    time.sleep(0.5)


for i, inst in instruments.items():
    inst.write_register(REG_ON_OFF, OFF, 1)  # ON/OFF
    print(f"on/off [{i}]: " + str(inst.read_register(REG_ON_OFF, 1)))

