import serial
import time
from interface import ServerInterface
from config import ProjectConfig


class ArduinoConn(ServerInterface):
    def __init__(self, config: ProjectConfig):
        self.port = config.get('USB_PORT')
        self.baud_rate = int(config.get('USB_BAUD_RATE'))

        self.conn = None
        self._connected = False

    def get_name(self) -> str:
        return format(f'USB connection on {self.port}')

    def connect(self):
        # Create socket for the serial port
        print(f'Waiting for a {self.get_name()}...')
        #while not self._connected:
        try:
            self.conn = serial.Serial(self.port, self.baud_rate)
            self._connected = True
            print(f'Connected to {self.conn.name}')
            #continue
        except Exception as e:
            print(f'Error with {self.get_name()}: {e}')
            self.disconnect()
            raise ConnectionError
            #print("Retrying Arduino Connection...")

    def is_connected(self) -> bool:
        return self._connected

    def write(self, message):
        try:
            self.conn.write(str.encode(message))
            print(f'Sent to Arduino: {message}')
        except Exception as e:
            print(f'Error with writing {message} to {self.get_name()}: {e}')

    def read(self):
        try:
            data = self.conn.readline()
            if data != b'\x00':
                data = str(data.decode('utf-8')).strip()
                print(f'Received from Arduino: {data}')
                return data

        except Exception as e:
            print(f'Error with reading from {self.get_name()}: {e}')

    def disconnect(self):
        if self.conn:
            self.conn.close()
            print('Terminating serial socket..')

        self._connected = False


if __name__ == '__main__':
    ar = ArduinoConn(ProjectConfig(USB_PORT='COM3'))
    ar.connect()
