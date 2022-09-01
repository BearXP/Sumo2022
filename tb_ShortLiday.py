from typing import Generator
import matplotlib.pyplot as plt
import numpy as np
import belay

device = belay.Device("COM7")


@device.task
def getDistances():
    def devicePacketsToint(input: list) -> int:
        noPackets = len(input)
        runningSum = 0
        for packetIndex in range(noPackets, 0, -1):
            runningSum = (runningSum) * 256 + input[packetIndex - 1]
        return runningSum

    def intTo2Packets(inputVal: int) -> list:
        lsb = inputVal % 256
        msb = int(inputVal / 256)
        return [lsb, msb]

    def calChecksum(body: list) -> int:
        checksum = 0
        for chunk in body:
            checksum += chunk
        return checksum % 256

    import machine
    from time import sleep
    import _thread

    class ShortLidar:
        GET_DISTANCE = 0x02
        STOP_GET_DISTANCE = 0x0F
        GET_CORRECTION_PARAMS = 0x12
        CONFIG_ADDRESS = 0x16
        ACK = 0x10

        def __init__(self, portNo) -> None:
            self.portNo = portNo
            self.data = None
            self._openPort()
            self._stop()
            sleep(0.1)
            self._start()

        def _openPort(self) -> None:
            uartSpeed = 921600
            self.ser = machine.UART(self.portNo, uartSpeed)
            self.running = False

        def _serWrite(self, commandCode: int, data: list = []) -> None:
            startChars = [0xAA, 0xAA, 0xAA, 0xAA]
            deviceId = 0x01
            packetOffset = [0x00, 0x00]
            dataLenth = intTo2Packets(len(data))
            body = [deviceId, commandCode] + packetOffset + dataLenth + data
            checksum = calChecksum(body)
            msg = startChars + body + [checksum]
            self.ser.write(bytearray(msg))

        def _stop(self) -> None:
            commandCode = self.STOP_GET_DISTANCE
            self._serWrite(commandCode)
            _ = self.ser.read()  # ToDo: Don't just ignore the response

        def _start(self) -> None:
            commandCode = self.GET_DISTANCE
            self._serWrite(commandCode)
            _ = self.ser.read()  # ToDo: Don't just ignore the response

        def _read_serial(self, retryUntilAA=True) -> bytearray:
            _ = self.ser.read()
            preData = b""
            if retryUntilAA:
                aCount = 0
                retryCount = 0
                while aCount < 4:
                    charRead = self.ser.read(1)
                    sleep(0.01)
                    if charRead == b"\xaa":
                        aCount += 1
                    else:
                        retryCount += 1
                        aCount = 0
                    assert (
                        retryCount < 500
                    ), f"Count not find start of the string aa 4 times, retried {retryCount} times"
                preData += b"\xaa\xaa\xaa\xaa"
            preData += self.ser.read(6)
            dataLen = devicePacketsToint(preData[-2:])
            data = b""
            while len(data) < dataLen:
                lenToRead = dataLen + 1 - len(data)
                newData = self.ser.read(lenToRead)
                if newData:
                    data += newData
                else:
                    sleep(0.05)
            assert dataLen + 1 == len(
                data
            ), f"Incorrect amount of data received.\r\nExpected {dataLen+1}\r\nReceived {len(data)}"
            return preData + data

        def update(self):
            """
            It reads the serial port, checks the first byte of the data, and if it's not 250, it returns an
            error message. Otherwise, it returns the range
            :return: The data is being returned as a string.
            """
            data = self._read_serial()
            self.data = data
            return self.data

        def _loop(self):
            while self.running:
                self.update()

        def start_loop(self):
            self.running = True
            _thread.start_new_thread(self._loop, ())

    lidar = ShortLidar(portNo=0)
    lidar.start_loop()
    while True:
        yield lidar.data


def distConf(data: bytearray):
    retVal = []
    for i in range(160):
        tmpMeasurement = int.from_bytes(data[2 * i : 2 * i + 2], byteorder="little")
        tmpConfidence = (tmpMeasurement >> 9) << 1
        tmpDistance = tmpMeasurement & 0x1FF
        retVal.append({"d": tmpDistance, "c": tmpConfidence})
    return retVal


def plotLine():
    from time import sleep

    x = range(160)
    y = [0, 500] * 80
    plt.ion()
    fig = plt.figure()
    # https://www.statology.org/fig-add-subplot/
    ax = fig.add_subplot(
        111
    )  # In layout that has 1 row(s) and 1 column(s), add the first subplot
    # line1 = ax.scatter(x, y)
    (line1,) = ax.plot(x, y, linewidth=0, marker="o")
    for data in getDistances():
        if data:
            distances = distConf(data[4:])
            ys = [point["d"] for point in distances]
            line1.set_ydata(ys)
            fig.canvas.draw()
            fig.canvas.flush_events()


if __name__ == "__main__":
    plotLine()
