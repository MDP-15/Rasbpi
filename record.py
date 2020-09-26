from pistream import PiVideoStream
import cv2
import time

vs = PiVideoStream(save=True).start()
time.sleep(2)

while True:
    frame = vs.read()
    cv2.imshow("Recording", frame)
