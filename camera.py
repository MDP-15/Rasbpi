# Web streaming example
# Source code from the official PiCamera package
# http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming

import io
import logging
import socketserver
import threading
from threading import Condition
from http import server
import json
import cgi
import time
from interface import ServerInterface
from picamera import PiCamera
from config import ProjectConfig
from queue import Queue

PAGE = """\
<html>
<head>
<title>Raspberry Pi - Camera</title>
</head>
<body>
<center><h1>Raspberry Pi - Camera</h1></center>
<center><img src="stream.mjpg" width="640" height="480"></center>
</body>
</html>
"""


class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)


class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/labels':
            ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
            if ctype != 'application/json':
                self.send_response(400)
                self.end_headers()
                return
            length = int(self.headers["Content-Length"])
            raw_message = self.rfile.read(length)
            message = json.loads(raw_message)
            queue.put(message['label'])
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes(json.dumps({'status': 0}), 'utf-8'))
        else:
            self.send_error(404)
            self.end_headers()

    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', str(len(frame)))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


output = StreamingOutput()
queue = Queue()


class PiHttpStream(ServerInterface):
    def get_name(self) -> str:
        return format(f'picamera http connection')

    def connect(self):
        try:
            self.server = StreamingServer(self.address, StreamingHandler)
            threading.Thread(target=self.server.serve_forever, daemon=True).start()
            self._connected = True
            print(f'Server started on {self.server.server_address}')
        except Exception as e:
            print(f'Error with {self.get_name()}: {e}')
            self.disconnect()
            raise ConnectionError

    def disconnect(self):
        if self.server:
            self.server.server_close()

        self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    def write(self, message):
        pass

    def __init__(self, config: ProjectConfig):
        # initialize the camera and stream
        self.camera = PiCamera()
        self.camera.resolution = (int(config.get('RES_WIDTH')), int(config.get('RES_HEIGHT')))
        self.camera.framerate = int(config.get('FRAMERATE'))

        self.server = None
        self.address = (config.get('IP_ADDRESS'), int(config.get('PICAM_PORT')))

        time.sleep(2.0)

        self.camera.start_recording(output, format='mjpeg')
        self._connected = False

    def read(self):
        label = queue.get()
        print(f'Received from POST request: {label}')
        return str(label)
