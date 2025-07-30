import os
import yaml
import socket
import threading
from datetime import datetime
from time import sleep
from pathlib import Path
from neopixel import NeoPixel
from neopixel import board
from sdl_utils import get_logger, send_file_name, receive_file_name
from sdl_utils import send_file_size, receive_file_size

"""
This is a module for the Raspberry Pi Camera Server
Please install the dependencies ONLY on Pi Zero 2 W/WH
Code will NOT work on Pi 5
"""

# Get the directory where this script is located
script_dir = Path(__file__).resolve().parent

# Open and read the JSON file
with open(script_dir / 'server_settings.yaml', 'r') as file:
    data = yaml.safe_load(file)
    buffer_size = data["BufferSize"]
    chunk_size = data["ChunkSize"]
    server_port = data["ServerPort"]


class LEDServer:
    """
    This is a class of a server with ability to take photos on demand with user-defined
    LED backlight. The client can request photos and changing the LED backlight.
    """
    def __init__(self, host="0,0,0,0", port=server_port):
        self.host = host
        self.port = port
        self.logger = self._setup_logger()
        self.server_ip = self._get_server_ip()
        self.led = self._init_led()
        self.color = (200, 200, 200)    # Default LED configuration

    @staticmethod
    def _setup_logger():
        return get_logger("LEDLogger")


    def _get_server_ip(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s_test:
            s_test.connect(("8.8.8.8", 80))
            server_ip = s_test.getsockname()[0]
            self.logger.info(f"My IP address is : {server_ip}")
            return server_ip

    def _init_led(self):
        # NeoPixel LED RING with 12 pixels MUST use board.D10
        led = NeoPixel(board.D10, 60, auto_write=True)

        # Blink to show initialization
        for i in range(0, 3):
            led.fill((100, 100, 100))
            sleep(0.5)
            led.fill((0, 0, 0))
        self.logger.info("LED initialized!")
        return led

    def test_led(self, led):
        self.logger.info("Start testing LED")
        _ = input("Please watch for possible dead pixels. Press any key.")    # TODO: Possible
        for color in [(255, 0, 0), (0, 255, 0), (0, 0, 255)]:
            for i in range(0, 12):
                led.fill((0, 0, 0))
                led[i] = color
                sleep(0.1)
        led.fill((0, 0, 0))
        self.logger.info("LED test complete.")


    def handle_client(self, conn):
        """Handle client connection in a thread-safe manner"""
        try:
            while True:
                msg = conn.recv(buffer_size).decode('utf-8').strip()
                if not msg:
                    break
                self.logger.info(f"Received message: {msg}.")

                if msg == "CHANGE_COLOR":
                    # Request color coordinates from client
                    conn.sendall("PLEASE SEND RGB".encode('utf-8'))
                    self.logger.info("Sent color request to client.")

                    # Receive and process RGB values
                    rgb_data = conn.recv(buffer_size).decode('utf-8').strip()
                    try:
                        r, g, b = map(int, rgb_data.split(','))
                        if all(0 <= val <= 255 for val in (r, g, b)):
                            self.color = (r, g, b)
                            self.led.fill(self.color)
                            sleep(1)
                            self.led.fill((0, 0, 0))
                            conn.sendall("COLOR_CHANGED".encode('utf-8'))
                            self.logger.info(f"LED color changed to ({r},{g},{b}).")
                        else:
                            raise ValueError("Values out of range (0-255).")
                    except Exception as e:
                        conn.sendall(f"INVALID_RGB: {e}".encode('utf-8'))
                        self.logger.error(f"Invalid RGB values: {rgb_data}.")

        except Exception as e:
            self.logger.error(f"Handle client error: {e}.")
        finally:
            conn.close()
            self.logger.info("Client connection closed.")
            self.logger.info("Waiting for new connection.")

    def start_server(self):
        """Start the server with clean error handling"""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            server.bind((self.server_ip, self.port))
            server.listen(5)
            self.logger.info(f"Server started on {self.server_ip}:{self.port}.")
            self.logger.info("Waiting for connection...")

            while True:
                # Accept the connection from client
                conn, addr = server.accept()
                self.logger.info(f"Connected with address: {addr}.")
                threading.Thread(
                    target=self.handle_client,
                    args=(conn,),
                    daemon=True
                ).start()

        except KeyboardInterrupt:
            self.logger.info("Server shutdown requested.")
        finally:
            server.close()
            self.led.fill((0, 0, 0))
            self.logger.info("Server socket closed.")


if __name__ == "__main__":
    camera = LEDServer()
    camera.test_led(camera.led)
    camera.start_server()
