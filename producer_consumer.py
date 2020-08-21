from queue import Queue
from interface import ServerInterface
from threading import Thread


class ProducerConsumer(object):

    def __init__(self, server: ServerInterface):
        self.server = server
        self.q = Queue()
        self.observers = []
        self.name = self.server.get_name()

    def spawn_thread(self, target) -> Thread:
        return Thread(target=target, daemon=True)

    def start(self):
        self.server.connect()
        read = self.spawn_thread(self.read_listen)
        write = self.spawn_thread(self.write_listen)
        read.start()
        write.start()

    def read_listen(self):
        while True:
            data = self.server.read()
            if data is not None:
                self.notify_observers(data)
            else:
                continue

    def write_listen(self):
        while True:
            data = self.get_data()
            self.server.write(data)

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
