import os
import socket
from pathlib import Path
from time import sleep
from dotenv import load_dotenv
from sdl_utils import get_logger
from sdl_utils import connect_socket, send_file_name, receive_file_name
from sdl_utils import send_file_size, receive_file_size, receive_file

# Load environment variables from .env file
load_dotenv()

# Get settings from environment variables
server_ip = os.getenv("SERVER_IP", "172.31.34.163")
server_port = int(os.getenv("SERVER_PORT", 2222))
buffer_size = int(os.getenv("BUFFER_SIZE", 2048))
chunk_size = int(os.getenv("CHUNK_SIZE", 1024))
path_tesseract = os.getenv("PATH_TESSERACT")


class LEDClient:
    """
    This is a client that requests and receives images
    More to be added
    """
    def __init__(self, host="0.0.0.0", port=server_port, logger=None):
        self.host = host
        self.port = port
        self.server_ip = server_ip
        self.logger = self.setup_logger()


    def update_server_ip(self):
        """
        Run this only the first time you set up the server, or when its IP address changes.
        """
        ip_up_to_date = input(f"Is the server IP address: {self.server_ip}? [Y]: ")
        while True:
            if ip_up_to_date in ['', 'y', 'Y', 'yes', 'Yes']:
                break
            elif ip_up_to_date in ['n', 'N', 'No', 'no']:
                new_server_ip = input("What is the new ip address")
                self.logger.info(f"IP address updated to {new_server_ip}")
                self.server_ip = new_server_ip
                break

   
    def interactive_client_session(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s = connect_socket(s, server_ip, server_port, self.logger)
           
            if s == None:
                return
            while True:
                print("Options:\n1. WARNING: FLASHING RED\n2. STANDBY/CAUTION: STATIC ORANGE \n3. PROCEED: STATIC GREEN\n4. Exit")
                option = input("Enter your choice: ").strip()

                if option == "1":
                        
                        
                     # Send color change request
                        s.sendall("CHANGE_COLOR".encode('utf-8'))

                        # Wait for server's RGB request
                        response = s.recv(buffer_size).decode('utf-8').strip()

                        while True:

                            sleep(1)
                            r, g, b = (255, 0, 0) 
                            sleep(1)
                            r,g,b = (0,0,0)
                            # Send validated RGB values
                            s.sendall(f"{r},{g},{b}".encode('utf-8'))

                            # Get response from server
                            result = s.recv(buffer_size).decode('utf-8').strip()
                            if result == "COLOR_CHANGED":
                                print("Successfully changed LED color!")
                            else:
                                print(f"Error changing color: {result}")
                                print(f"Unexpected server response: {response}")

                elif option == '2':
                        # Send color change request
                        s.sendall("CHANGE_COLOR".encode('utf-8'))

                        # Wait for server's RGB request
                        response = s.recv(buffer_size).decode('utf-8').strip()

                        r, g, b = (255, 165, 0)  # Static orange color
                           
                        # Send validated RGB values
                        s.sendall(f"{r},{g},{b}".encode('utf-8'))
                       
                       # Get response from server
                        result = s.recv(buffer_size).decode('utf-8').strip()
                        if result == "COLOR_CHANGED":
                            print("Successfully changed LED color!")
                        else:
                            print(f"Error changing color: {result}")
                            print(f"Unexpected server response: {response}")
                            
                elif option == '3':
                   # Send color change request
                        s.sendall("CHANGE_COLOR".encode('utf-8'))

                        # Wait for server's RGB request
                        response = s.recv(buffer_size).decode('utf-8').strip()

                        r, g, b = (0, 255, 0)  # Static orange color
                           
                        # Send validated RGB values
                        s.sendall(f"{r},{g},{b}".encode('utf-8'))
                       
                       # Get response from server
                        result = s.recv(buffer_size).decode('utf-8').strip()
                        if result == "COLOR_CHANGED":
                            print("Successfully changed LED color!")
                        else:
                            print(f"Error changing color: {result}")
                            print(f"Unexpected server response: {response}")
                            
                elif option == '4':
                    self.logger.info('Exiting')
                    s.close()
                    break

                else:
                    print("Invalid option. Please try again.")

                    
if __name__ == "__main__":
    client = LEDClient()
    
    # Please confirm that you have the right server IP address
    client.update_server_ip()
    client.interactive_client_session()
