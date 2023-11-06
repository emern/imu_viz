"""
Define object to parse data from IMU module via serial
"""

import serial
import json
import os
import time
import components.IMU

class Parser:

    def __init__(self, dev_name: str, imu: components.IMU) -> None:

        # open configuration file
        config_path = os.path.abspath("components/config/parser_conf.json")
        config_file = open(config_path)
        config_data = json.load(config_file)

        # get device configuration
        our_device = ""

        for device in config_data['device']:
            if device['name'] == dev_name:
                our_device = device

        if our_device == "":
            raise Exception("Missing device configuration!")

        self.port = our_device['port']
        self.baud = our_device['baudrate']

        print(f"Setting up connection on port {self.port} at baud {self.baud}")
        self.ser = serial.Serial(baudrate=self.baud, port=self.port)
        try:
            self.ser.open()
        except serial.serialutil.SerialException:
            self.ser.close()
            self.ser.open()

        # There is this known issue where reading data using pyserial from an Arduino requires a delay...
        # https://arduino.stackexchange.com/questions/23950/arduino-serial-monitor-works-but-not-on-pyserial-and-putty
        time.sleep(10)
        self.ser.read_all()

        self.imu = imu

    def run(self):

        # read all the incoming data directly, this clears the buffer at the same time as reading
        data = self.ser.read_all()

        # make sure that the current line is finished off, read all incoming bytes until we hit the newline char
        while len(data) == 0 or data[-1] != 10:
            data += self.ser.read(1)

        # split into lines, we analyze the "newest" line first for valid data
        data_decoded = data.decode()

        d_list = data_decoded.split('\r\n')
        d_list = d_list[::-1]
        for string in d_list:
            parsed_data = self.imu.parse_data(string)
            if parsed_data != None:
                return parsed_data

        return None

    def cleanup(self) -> None:
        self.ser.close()


if __name__ == '__main__':
    pass