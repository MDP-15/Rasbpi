from pistream import PiVideoStream
import cv2

vs = PiVideoStream(save=True).start()

while True:
    frame = vs.read()
    cv2.imshow("Recording", frame)
