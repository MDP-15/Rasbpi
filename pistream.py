from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
import pickle
import struct
import time
from interface import ServerInterface


class PiVideoStream(ServerInterface):
    def get_name(self) -> str:
        return format(f'picamera connection')

    def connect(self):
        self.start()
        self._connected = True

    def disconnect(self):
        self.stop()
        self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    def write(self, message):
        time.sleep(5.0)

    def __init__(self, resolution=(640, 480), framerate=32):
        # initialize the camera and stream
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.raw_capture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.raw_capture, format="bgr", use_video_port=True)

        self.frame = None
        self.stopped = False

        self._connected = True

    def start(self):
        # start the thread to read frames from the video stream
        Thread(target=self.update, daemon=True).start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        for f in self.stream:
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            self.frame = f.array
            self.raw_capture.truncate(0)
            # if the thread indicator variable is set, stop the thread
            # and resource camera resources
            if self.stopped:
                self.stream.close()
                self.raw_capture.close()
                self.camera.close()
                return

    def read(self):
        # return the frame most recently read
        # return self.frame
        return self.serve()

    def serve(self):
        data = pickle.dumps(self.frame, 0)
        size = len(data)
        data = struct.pack(">L", size)+data
        return data

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True

