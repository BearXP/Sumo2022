import machine
from time import sleep, time
class Lidar:
    def __init__(self, portNo, angleOffset) -> None:
        """
        The function is called when the class is instantiated. It sets up the UART port to
        talk to the lidar senor

        :param portNo: The UART port number to use
        :param angleOffset: This is the offset of the sensor from the center of the robot
        """
        self.portNo = portNo
        self.angleOffset = angleOffset
        uartSpeed = 230400
        self.ser = machine.UART(self.portNo, uartSpeed)
        self.start()

    def start(self) -> None:
        """
        It sends a start command to the lidar sensor, and then records the time
        """
        self.ser.write(b"b")
        self.startTime = time()

    def stop(self) -> None:
        """
        It sends a start command to the lidar sensor, and then records the time
        """
        self.ser.write(b"e")
        self.startTime = None

    def _read_serial(self) -> bytes:
        """
        It reads the serial port and returns the data
        :return: The data is being returned as a byte string.
        """
        # If the start command has not been sent, then make sure it's started
        if self.startTime == None:
            self.start()
        # Note: The lidar needs ~2s after startup to spin up
        startupWaitTime = self.startTime + 2 - time()
        if startupWaitTime > 0:
            sleep(startupWaitTime)
        # Read back the data
        retryCount = 0
        data = b""
        while True:
            bit = self.ser.read(1)
            # print(f"Received bit: {bit}")
            # If it's the end of the data stream, return the data found so far
            if bit == None:
                break
            # If we receive the sync character, read and return the full packet
            elif bit == b'\xFA':
                packet = self.ser.read(41)
                # print(f"  Rest of the packet is: {packet}")
                if packet:
                    data = bit + packet
                break
            # If we get data but it's not the sync bit, ignore and retry
            else:
                data += bit
                if retryCount > 100:
                    break
                retryCount += 1
                sleep(0.01)
        return data

    def _read_range(self, data):
        """
        The function takes in a byte array, and returns a tuple of the RPM, distance, and intensity
        :param data: The data received from the sensor
        """
        bytes_data = list(data)
        degree = (bytes_data[1] - 0xA0) * 6
        rpm = (bytes_data[3] << 8) | bytes_data[2]
        distances = [0] * 360
        intensities = [0] * 360
        if bytes_data[41] != bytes_data[40] or bytes_data[40] == 0:
            return f"invalid data: {degree}"
        for i in range(6):
            distance = (bytes_data[2 + (i * 4) + 3] << 8) | (
                bytes_data[2 + (i * 4) + 2]
            )
            intensity = (bytes_data[2 + (i * 4) + 1] << 8) | (
                bytes_data[2 + (i * 4) + 0]
            )
            angle = degree + i
            angle_offsetted = (
                angle + self.angleOffset
                if angle + self.angleOffset < 360
                else angle + self.angleOffset - 360
            )
            # print(f"angle_offsetted: {angle_offsetted}\tdistance: {distance}")
            distances[angle_offsetted] = distance
            intensities[angle_offsetted] = intensity
        return distances

    def update(self):
        """
        It reads the serial port, checks the first byte of the data, and if it's not 250, it returns an
        error message. Otherwise, it returns the range
        :return: The data is being returned as a string.
        """
        data = self._read_serial()
        if len(list(data)) == 0:
            return f"Error, no data was returned from the sensor"
        if data[0] == 252:
            return f"Error, data[0] was 252. Make sure the PWM signal is wired up correctly"
        if data[0] != 250:
            return f"Error, data[0] was {data[0]} dec - {hex(data[0])} hex"
        return self._read_range(data)


if __name__ == "__main__":
    lidar = Lidar(portNo=1, angleOffset=0)
    vals = lidar.update()
    print(f"Update Completed, values: {vals}")
    lidar.stop()

