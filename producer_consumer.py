from queue import Queue
from interface import ServerInterface
from threading import Thread


def spawn_thread(target) -> Thread:
    return Thread(target=target, daemon=True)


class ProducerConsumer(object):

    def __init__(self, server: ServerInterface):
        self.server = server
        self.q = Queue()
        self.observers = []
        self.name = self.server.get_name()

    def start(self):
        count = 0
        while True:
            count += 1
            if count > 2:
                print(f'{self.name}: max number of reconnections exceeded.')
                break
            try:
                self.server.connect()
                read = spawn_thread(self.read_listen)
                write = spawn_thread(self.write_listen)
                read.start()
                write.start()
                read.join()
                write.join()
            except ConnectionError:
                print(f'{self.name}: connection ended')

    def read_listen(self):
        while True:
            try:
                data = self.server.read()
                self.notify_observers(data)
            except ConnectionError:
                break

    def write_listen(self):
        while True:
            try:
                if not self.server.is_connected():
                    break
                data = self.get_data()
                self.server.write(data)
            except ConnectionError:
                break

    # notify every job subscribed to this server that data has been read from the client
    def notify_observers(self, data):
        for s in self.observers:
            s.put_data(data)

    # put data into queue
    def put_data(self, data):
        self.q.put(data)

    def register(self, items: list):
        self.observers.extend(items)

    def get_data(self):
        data = self.q.get()
        self.q.task_done()
        return data
