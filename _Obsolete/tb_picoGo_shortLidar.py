# https://github.com/andreas40239/LdRobot_LD07/blob/main/ld07_getCalibration.py
# https://github.com/andreas40239/LdRobot_LD07/blob/main/publisher_member_function.py
# https://github.com/andreas40239/LdRobot_LD07/blob/main/read_ld07.py

import machine
from time import sleep

#ld07_getCorrectionData = bytearray()
#packet.append(0x02)
#bytearray(msg, "ascii")
ld07_getCorrectionData = bytearray([0xAA,0xAA,0xAA,0xAA,0x01,0x12,0x00,0x00,0x00,0x00,0x13])

uartPort = 0
uartSpeed = 921600
uart = machine.UART(uartPort, uartSpeed)
uart.write(ld07_getCorrectionData)
sleep(0.1)
retVal = uart.readline()
print("Ret Val: ")
print(retVal)