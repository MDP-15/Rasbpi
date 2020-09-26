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

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

out.release()

