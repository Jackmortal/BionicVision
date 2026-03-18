import cv2 as cv

video = cv.VideoCapture(0, cv.CAP_V4L2)
print("Opened:", video.isOpened())

isTrue, frame = video.read()
print("Frame read:", isTrue)
if isTrue:
    print("Frame shape:", frame.shape)
    cv.imwrite("test.jpg", frame)
    print("Saved test.jpg")

video.release()