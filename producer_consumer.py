from queue import Queue
from interface import ServerInterface
from threading import Thread
from collections import deque


def spawn_thread(target) -> Thread:
    return Thread(target=target, daemon=True)


def split_fp(inst) -> deque:
    res = deque()
    for i in range(0, len(inst)):
        if inst[i] == 'F':
            res.append(inst[i: i + 2])
        elif inst[i] == 'L':
            res.append(inst[i])
        elif inst[i] == 'R':
            res.append(inst[i])
    return res


class ProducerConsumer(object):

    def __init__(self, server: ServerInterface):
        self.server = server
        self.q = Queue()
        self.observers = []
        self.name = self.server.get_name()
        self.cache = {}
        self.instructions = deque()
        self.tags = server.get_tags()

    def start(self):
        count = 0
        while True:
            count += 1
            if count > 5:
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
            if not self.server.is_connected():
                break
            try:
                data = self.get_data()
                if data is not None:
                    self.server.write(data)
            except ConnectionError:
                break
            except Exception:
                continue

    # notify relevant subscribers subscribed to this server that data has been read from the client
    def notify_observers(self, data):
        if 'MDP15' not in data:  # only parse json with this key value
            return

        inst = data.get('MDP15')

        # special case for fastest path string
        if inst == 'FP':
            val = data.get('FP')
            self.cache['FP'] = val  # store in cache
            self.instructions = split_fp(val)
            return

        # print(self.observers)
        # print(len(self.observers))
        # count = 1
        for s in self.observers:
            # print(s)
            # s.get_name()
            # print(s.tags)
            # continue
            # s.put_data(data)
            # print(f'tag is {s.get_tags()}')
            # print('boolean ', 'ROBOT' in s.tags)
            if 'ROBOT' in s.tags:  # send to Robot
                if inst == 'RI':
                    if 'ALGO' in self.tags:
                        self.cache['latest'] = data.get('RI')  # get latest movement from algo and store in local cache
                    s.put_data(data)
                elif inst == 'SF':  # start fastest path; get the cached string and send to Robot
                    s.put_data(self.cache.get('FP'))

            elif 'ANDROID' in s.tags:  # send to Android
                if inst.startswith('MDF') or inst == 'STATUS':
                    s.put_data(data)
                elif inst == 'MC':  # movement completed
                    if 'latest' in self.cache:  # for exploration; get the latest instruction from Algo
                        s.put_data({'MDP15': 'RI', 'RI': self.cache.get('latest')})
                    if len(self.instructions) != 0:  # for fastest path; dequeue instructions and send to Android
                        val = self.instructions.popleft()
                        s.put_data({'MDP15': 'RI', 'RI': val})

                continue

            if 'ALGO' in s.tags:  # send to Algo
                # print(data)
                if inst == 'SENSORS' or inst == 'RP' or inst == 'W' or inst == 'O' or inst == 'SE':
                    s.put_data(data)

            # count += 1
            # print('count', count)

    # put data into queue
    def put_data(self, data):
        self.q.put(data)

    def register(self, items: list):
        self.observers.extend(items)

    def get_data(self):
        if self.q.empty():
            return None
        data = self.q.get()
        # self.q.task_done()
        return data
