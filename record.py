from pistream import PiVideoStream
import cv2
import time

vs = PiVideoStream(save=True).start()
time.sleep(2)

out = cv2.VideoWriter('recording.avi', cv2.VideoWriter_fourcc(*'DIVX'), 15, (640, 480))

while True:
    frame = vs.read()
    out.write(frame)
    cv2.imshow("Recording", frame)

    k = cv2.waitKey(0)
    if k == ord('q'):
        break


out.release()

