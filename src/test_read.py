import cv2 as cv

img = cv.imread('Bill.jpg')

cv.imshow('Bill', img)

cv.waitKey(0)