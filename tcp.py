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
            print(f'Error with connection attempt for {self.get_name()}: {e}')
            self.disconnect()
            raise ConnectionError

    def read(self):
        try:
            data = self.client.recv(4096)  # reads data from the socket in batches of 1024 bytes
            print("Data", data)
            data_string = data.decode('utf-8')
            # "{MDP15:RI, RI: xxx}{MDP:MDF, MDF:002}" => "{MDP15:RI, RI: xxx", "{MDP:MDF, MDF:002" , ""
            # data_list = data_string.split('}')

            count = 0
            for i in data_string:
                if i == '}':
                    count = count + 1

            if count == 1:
                data_dict = json.loads(data_string)
            #                 j = json.loads(data_string)
            #                 key = j.get('MDP15')
            #                 data_dict[key] = j.get(key)

            elif count > 1:
                data_list = data_string.split('}')
                if data_list[len(data_list) - 1] is not '':
                    print('buffer overflow?')
                    return

                data_dict = {'MDP15': 'MDFRI'}
                for i in data_list:
                    if i is not "":
                        s = i + "}"
                        s_json = json.loads(s)
                        key = s_json.get('MDP15')
                        data_dict[key] = s_json.get(key)

            if not data:
                raise ConnectionError('No transmission')
            # data_dict = json.loads(data)
            print(f'Received from PC: {data_dict}')
            return self.format_data(data_dict)

        #             if data_list[len(data_list)-1] is not '':
        #                 print('buffer overflow?')
        #                 return
        #             data_dict = {'MDP15': 'MDFRI'}
        #             for i in data_list:
        #                 if i is not "":
        #                     s = i + "}"
        #                     s_json = json.loads(s)
        #                     key = s_json.get('MDP15')
        #                     data_dict[key] = s_json.get(key)

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
            # message = str(message)
            # byte_msg: bytes = str.encode(message + '\n')
            json_str = json.dumps(message)
            byte_msg = bytes(json_str, encoding='utf-8')
            self.client.sendto(byte_msg, self.addr)
            print(f'Sent to PC: {message}')

        except socket.error as e:
            print(f'IO Error with {self.get_name()}: {e}')
            print('Reconnecting...')
            self.disconnect()
            raise ConnectionError
        except Exception as e:
            print(f'Error with writing to {self.get_name()}: {e}')
            raise e


if __name__ == '__main__':
    server = PcConn(ProjectConfig(default=False))
    server.connect()
    Robot_Position = '{"MDP15":"SENSORS","SENSORS":"0;0;0;0;0;0"}'  # to algo
    RP = json.loads(Robot_Position)
    while True:
        server.write(RP)
        server.read()
        time.sleep(2)
