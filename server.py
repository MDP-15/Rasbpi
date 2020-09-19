import threading
from tcp import PcConn
from bt import BluetoothConn
from usb import ArduinoConn
from queue import Queue
from producer_consumer import ProducerConsumer
from config import ProjectConfig
from pistream import PiVideoStream


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
    config = ProjectConfig(default=False)

    bt_server = ProducerConsumer(BluetoothConn(config))
    usb_server = ProducerConsumer(ArduinoConn(config))
    pc_server = ProducerConsumer(PcConn(config))
    camera_server = ProducerConsumer(PiVideoStream())

    pc_server.register([bt_server, usb_server])
    bt_server.register([pc_server, usb_server])
    usb_server.register([bt_server, pc_server])
    camera_server.register([pc_server])

    server_list.append(bt_server)
    server_list.append(usb_server)
    server_list.append(pc_server)
    server_list.append(camera_server)

    run_all(server_list)
