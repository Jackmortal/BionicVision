from picamera2 import Picamera2
import cv2 as cv

picam2 = Picamera2()
picam2.start()

while True:
    frame = picam2.capture_array()
    
    cv.imshow('Live', frame)

    if cv.waitKey(20) & 0xFF == ord('d'):
        break

picam2.stop()
cv.destroyAllWindows()