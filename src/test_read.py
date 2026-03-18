import cv2 as cv

img = cv.imread('Bill.jpg')

cv.imwrite('Bill_copy.jpg', img)

cv.waitKey(0)

