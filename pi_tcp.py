import socket
from interface import ServerInterface
from config import ProjectConfig
import json
import cv2
import struct
import pickle


encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]


class CamPcConn(ServerInterface):

    def __init__(self, config: ProjectConfig):
        self.ip_address = config.get('IP_ADDRESS')
        self.port = int(config.get('PICAM_PORT'))
        self._connected = False

        self.conn = None
        self.client = None
        self.addr = None

    def get_name(self) -> str:
        return format(f'Image Rec TCP connection on {self.ip_address}:{self.port}')

    def get_tags(self) -> dict:
        return {'IR': True, 'IMAGE_REC': True}

    def disconnect(self):
        if self.conn:
            self.conn.close()
            print('Terminating server socket..')

        if self.client:
            self.client.close()
            print('Terminating client socket..')

        self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    def connect(self):
        try:
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.conn.bind((self.ip_address, self.port))
            self.conn.listen(1)  # blocks until 1 client is connected

            print(f'Listening for a TCP connection on {self.ip_address}:{self.port}')

            self.client, self.addr = self.conn.accept()
            print(f'Connected to {self.addr}')
            self._connected = True

        except Exception as e:
            print(f'Error with connection attempt for {self.get_name()}: {e}')
            self.disconnect()
            raise ConnectionError

    def read(self):
        try:
            data = self.client.recv(1024)  # reads data from the socket in batches of 1024 bytes
            if not data:
                raise ConnectionError('No transmission')
            data_dict = json.loads(data)

            print(f'Received from IR PC: {data_dict}')
            return self.format_data(data_dict)

        except socket.error as e:
            print(f'IO Error with {self.get_name()}: {e}')
            print('Reconnecting...')
            self.disconnect()
            raise ConnectionError
        except Exception as e:
            print(f'Error with reading from {self.get_name()}: {e}')
            raise e

    def write(self, message):
        try:
            result, frame = cv2.imencode('.jpg', message, encode_param)
            data = pickle.dumps(frame, 0)
            size = len(data)

            # print("{}: {}".format(img_counter, size))
            # client_socket.sendall(struct.pack(">L", size) + data)

            self.client.sendto(struct.pack(">L", size) + data, self.addr)
            print(f'Sent to IR PC: {message}')

        except socket.error as e:
            print(f'IO Error with {self.get_name()}: {e}')
            print('Reconnecting...')
            self.disconnect()
            raise ConnectionError
        except Exception as e:
            print(f'Error with writing to {self.get_name()}: {e}')
            raise e


# if __name__ == '__main__':
#     server = CamPcConn(ProjectConfig(default=False))
#     server.connect()
#     Robot_Position = '{"MDP15":"SENSORS","SENSORS":"0;0;0;0;0;0"}'  # to algo
#     RP = json.loads(Robot_Position)
#     while True:
#         server.write(RP)
#         server.read()
#         time.sleep(2)