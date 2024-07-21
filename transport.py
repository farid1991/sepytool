from log import *
from tqdm import tqdm

import serial
import time


class Transport:
    def __init__(self, portname):
        self.port_name = portname

    def connect(self):
        self._sl = serial.Serial(
            port=self.port_name,
            baudrate=9600,
            bytesize=8,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.15,
        )

        self.set_port()

    def disconnect(self):
        self._sl.close()
        del self._sl

    def set_baudrate(self, baudrate):
        self._sl.baudrate = baudrate
        self.set_port()

    def set_port(self):
        self._sl.rts = False
        self._sl.dtr = False
        self._sl.dtr = True
        self._sl.rts = True

    def reset_io_buffer(self):
        self._sl.reset_output_buffer()
        self._sl.reset_input_buffer()

    def write_binary(self, data: bytes):
        time.sleep(0.01)
        self._sl.write(data)
        time.sleep(0.01)

    def read_binary(self, length: int = 0):
        if length == 0:
            return self._sl.readall()
        else:
            return self._sl.read(length)

    def read_binary_with_timeout(self, timeout: float = 0.1):
        start_time = time.time()
        data = b""
        while time.time() - start_time < timeout:
            if self._sl.in_waiting:
                data += self._sl.read(self._sl.in_waiting)
                return data
            time.sleep(0.1)
        return data

    def wait_for_byte(self, byte_code):
        while True:
            resp = self.read_binary(1)
            if resp == byte_code:
                return resp
            time.sleep(0.01)

    def wait_for_str(self, str_data):
        received_data = b""  # Variable to store the received data
        desired_string = str_data.encode()  # Desired string to wait for
        buffer_size = len(
            desired_string
        )  # Size of the buffer to compare with the desired string

        while True:
            # Read one byte from the serial port
            data = self.read_binary(1)

            # Append the received byte to the variable
            received_data += data

            # Check if the desired string is present in the received data
            if desired_string in received_data[-buffer_size:]:
                break
        # Logger.LOG(1, f"Received data: {received_data}")

    def send_command(self, command):
        self.write_binary(command.encode())

    def send_payload_to_serial(self, buffer, chunk_size, name):
        total_size = len(buffer)
        progress_bar = tqdm(
            total=total_size,
            unit="%",
            ncols=80,
            bar_format="{desc:<10} [{bar:50}] : {percentage:.0f}%",
        )
        progress_bar.set_description(f"{name}")

        # Iterate over the buffer in chunks of chunk_size bytes
        for i in range(0, total_size, chunk_size):
            chunk = buffer[i : i + chunk_size]  # Get the current chunk

            # Send the chunk to the serial port
            self._sl.write(chunk)
            time.sleep(0.1)
            progress_bar.update(
                len(chunk)
            )  # Update the progress bar with the chunk size

        progress_bar.close()  # Close the progress bar when done

    def send_buffer_to_serial(self, buffer, chunk_size):
        # Iterate over the buffer in chunks of chunk_size bytes
        for i in range(0, len(buffer), chunk_size):
            chunk = buffer[i : i + chunk_size]  # Get the current chunk

            # Send the chunk to the serial port
            self._sl.write(chunk)

    def transceive(self, exp: str):
        resp = self.read_binary(len(exp))
        if resp.decode() != exp:
            raise ValueError(f"Unexpected response: {resp.decode()}. Expected: {exp}")
        return resp
