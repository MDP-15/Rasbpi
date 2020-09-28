# import threading
from tcp import PcConn
from bt import BluetoothConn
from usb import ArduinoConn
# from queue import Queue
from producer_consumer import ProducerConsumer
from config import ProjectConfig
from camera import PiHttpStream
from multiprocessing import Queue, Process


procs = []


def run_all(servers):
    create_process(servers)


def create_process(servers):
    for s in servers:
        t = Process(target=s.start, daemon=True)
        procs.append(t)
        t.start()

    for p in procs:
        p.join()


if __name__ == '__main__':
    server_list = []
    config = ProjectConfig(default=False)

    bt_server = ProducerConsumer(BluetoothConn(config))
    usb_server = ProducerConsumer(ArduinoConn(config))
    pc_server = ProducerConsumer(PcConn(config))
    cam_server = ProducerConsumer(PiHttpStream(config))

    # register observers to each server
    pc_server.register([bt_server, usb_server])
    bt_server.register([pc_server, usb_server])
    usb_server.register([bt_server, pc_server])
    cam_server.register([bt_server, pc_server, usb_server])

    server_list.append(bt_server)
    server_list.append(usb_server)
    server_list.append(pc_server)
    server_list.append(cam_server)

    run_all(server_list)
