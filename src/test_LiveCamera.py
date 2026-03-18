import cv2 as cv

video = cv.VideoCapture(0)

while True:
    isTrue, frame = video.read()

    if not isTrue: # Exits the loop if the video ends.
        break

    cv.imshow('Live', frame)

    if cv.waitKey(20) & 0xFF == ord('d'): # Waits for 20ms before moving to the next frame. If 'd' is pressed then it exits.
        break

video.release() # Releases the video resources.
cv.destroyAllWindows() # Closes all the windows.