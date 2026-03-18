import cv2 as cv

for i in [0, 1, 2, 3, 4, 5, 6, 7]:
    video = cv.VideoCapture(i, cv.CAP_V4L2)
    isTrue, frame = video.read()
    print(f"video{i} - Opened: {video.isOpened()}, Frame read: {isTrue}")
    video.release()