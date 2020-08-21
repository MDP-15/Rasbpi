import socket
from interface import ServerInterface
from config import ProjectConfig


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
            print(f'Error with connection: {e}')
            self.disconnect()

    def read(self):
        try:
            data = self.client.recv(1024)  # reads data from the socket in batches of 1024 bytes
            data = data.decode('utf-8')
            if not data:
                self.disconnect()
                print('No transmission. Connection ended.')
                print('Reconnecting...')
                self.connect()
                return None
            print(f'Received from PC: {data.rstrip()}')
            return data

        except Exception as e:
            print(f'Error with reading: {e}')
            print('Reconnecting...')
            self.connect()
            return None

    def write(self, message):
        try:
            message = str(message)
            byte_msg: bytes = str.encode(message + '\n')
            self.client.sendto(byte_msg, self.addr)
            print(f'Sent to PC: {message}')
        except Exception as e:
            print(f'Error with writing {message}: {e}')
            print('Reconnecting...')
            self.connect()


if __name__ == '__main__':
    server = PcConn(ProjectConfig())
    server.connect()