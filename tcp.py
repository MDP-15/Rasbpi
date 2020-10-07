import socket
from interface import ServerInterface
from config import ProjectConfig
import json
import time


class PcConn(ServerInterface):

    def __init__(self, config: ProjectConfig):
        self.ip_address = config.get('IP_ADDRESS')
        self.port = int(config.get('IP_PORT'))
        self._connected = False

        self.conn = None
        self.client = None
        self.addr = None

    def get_name(self) -> str:
        return format(f'TCP connection on {self.ip_address}:{self.port}')

    def get_tags(self) -> dict:
        return {'TCP': True, 'PC': True, 'ALGO': True}

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
            print(f'Error with {self.get_name()}: {e}')
            #self.disconnect()
            raise ConnectionError

    def read(self):
        try:
            data = self.client.recv(1024)  # reads data from the socket in batches of 1024 bytes
            #data = data.decode('utf-8')
            #print(f'Type of data is {type(data)}')
            #print(f'Type of data_dict is {type(data_dict)}')
            if not data:
                raise ConnectionError('No transmission')
            data_dict = json.loads(data)
            print(f'Received from PC: {data}')
            return self.format_data(data_dict)

        except Exception as e:
            print(f'Error with reading from {self.get_name()}: {e}')
            #print('Reconnecting...')
            #self.disconnect()
            #raise ConnectionError

    def write(self, message):
        try:
            #message = str(message)
            #byte_msg: bytes = str.encode(message + '\n')
            json_str = json.dumps(message)
            byte_msg = bytes(json_str, encoding='utf-8') 
            self.client.sendto(byte_msg, self.addr)
            print(f'Sent to PC: {message}')
        except Exception as e:
            print(f'Error with writing {message} to {self.get_name()}: {e}')
            #print('Reconnecting...')
            #self.disconnect()
            raise ConnectionError


if __name__ == '__main__':
    server = PcConn(ProjectConfig(default=False))
    server.connect()
    Robot_Position = '{"MDP15":"SENSORS","SENSORS":"0;0;0;0;0;0"}' #to algo
    RP = json.loads(Robot_Position)   
    while True:
        server.write(RP)
        server.read()
        time.sleep(2)