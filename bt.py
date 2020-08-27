from bluetooth import BluetoothSocket
import bluetooth
from interface import ServerInterface
from config import ProjectConfig


class BluetoothConn(ServerInterface):

    def __init__(self, config: ProjectConfig):
        self.conn = None
        self.client = None
        self._connected = False

        self.address = ''
        self.port = 0

    def get_name(self) -> str:
        return format(f'Bluetooth connection on {self.address} port {self.port}')

    def is_connected(self) -> bool:
        return self._connected

    def connect(self):
        try:
            self.conn = BluetoothSocket(bluetooth.RFCOMM)  # use RFCOMM protocol
            self.conn.bind((self.address, self.port))  # empty address; use any available adapter
            self.address, self.port = self.conn.getsockname()

            self.conn.listen(1)

            uuid = '94f39d29-7d6d-437d-973b-fba39e49d4ee'
            bluetooth.advertise_service(sock=self.conn,
                                        name='MDP-Group-15-Bluetooth-Server',
                                        service_id=uuid,
                                        service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
                                        profiles=[bluetooth.SERIAL_PORT_PROFILE], )

            print(f'Listening for Bluetooth connection on {self.address} port {self.port}')
            self.client, client_info = self.conn.accept()
            print(f'Connected to {client_info}')
            self._connected = True

        except Exception as e:
            print(f'Error with connection: {e}')
            self.disconnect()

    def read(self):
        try:
            data = self.client.recv(1024)
            data = data.decode('utf-8')
            if not data:
                self.disconnect()
                print('No transmission. Connection ended.')
                print('Reconnecting...')
                self.connect()
                return None
            print(f'Received from Android device: {data}')
            return self.format_data(data)

        except Exception as e:
            print(f'Error with reading from {self.get_name()}: {e}')
            print('Reconnecting...')
            self.connect()
            return None

    def write(self, message):
        try:
            message = str(message)
            self.client.send(message)
            print(f'Sent to Android device: {message}')

        except Exception as e:
            print(f'Error with writing {message} to {self.get_name()}: {e}')
            print('Reconnecting...')
            self.connect()

    def disconnect(self):
        if self.conn:
            self.conn.close()
            print('Terminating server socket..')

        if self.client:
            self.client.close()
            print('Terminating client socket..')

        self._connected = False


if __name__ == '__main__':
    server = BluetoothConn(ProjectConfig())
    server.connect()
