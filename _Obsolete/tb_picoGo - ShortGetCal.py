import machine
from time import sleep

ld07_getCorrectionData = bytearray([0xAA,0xAA,0xAA,0xAA,0x01,0x12,0x00,0x00,0x00,0x00,0x13])

uartPort = 0
uartSpeed = 921600
uart = machine.UART(uartPort, uartSpeed)
uart.write(ld07_getCorrectionData)
sleep(0.1)
retVal = uart.readline()
print(retVal)