import threading
from tcp import PcConn
from bt import BluetoothConn
from usb import ArduinoConn
from queue import Queue
from producer_consumer import ProducerConsumer
from config import ProjectConfig

thread_queue = Queue()


def run_all(servers):
    create_workers(len(servers))
    create_jobs(servers)


# Create worker threads
def create_workers(num):
    for _ in range(num):
        t = threading.Thread(target=work, daemon=True)
        t.start()


# Put job list into queue
def create_jobs(servers):
    for s in servers:
        thread_queue.put(s)
    thread_queue.join()  # blocks until task_done is called


# Do next job that is in the queue
def work():
    s = thread_queue.get()
    s.start()


if __name__ == '__main__':
    server_list = []
    config = ProjectConfig()
    bt_server = ProducerConsumer(BluetoothConn(config))
    pc_server = ProducerConsumer(PcConn(ProjectConfig(IP_PORT=9999)))
    pc_server2 = ProducerConsumer(PcConn(ProjectConfig(IP_PORT=9998)))
    pc_server3 = ProducerConsumer(PcConn(ProjectConfig(IP_PORT=9997)))

    pc_server.register([pc_server2])
    pc_server2.register([pc_server3])

    server_list.append(bt_server)
    server_list.append(pc_server)
    server_list.append(pc_server2)
    server_list.append(pc_server3)

    run_all(server_list)
