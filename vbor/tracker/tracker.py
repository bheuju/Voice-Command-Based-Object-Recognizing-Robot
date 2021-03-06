import cv2
import numpy as np
import RobustMatcher
import time

from VideoStream import VideoStream

import uart

left = '0'
right = '1'
up = '3'
down = '2'
far = '6'
near = '7'
optimum = '8'

resolution = (320, 240)
cap = VideoStream(usePiCamera=True, resolution=resolution).start()
time.sleep(0.2)

w = resolution[0]
h = resolution[1]
dw = int(resolution[0]/3)
dh = int(resolution[1]/3)
lx = 0 + dw
ly = 0 + dh
rx = w - dw
ry = h - dh

def checkBounds(res, area, x, y):

    if area < 0.2:
        uart.send(far)
        #print "Far"
        res = cv2.putText(res, "Far", (w-200, 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.75,
                              (155, 155, 0),
                              1,
                              cv2.LINE_AA)
    elif area > 1.5:
        uart.send(near)
        #print "Near"
        res = cv2.putText(res, "Near", (w-200, 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.75,
                              (155, 155, 0),
                              1,
                              cv2.LINE_AA)
    else:
        uart.send(optimum)
        #print "Optimal Distance"
        res = cv2.putText(res, "Optimal Distance", (w-200, 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.75,
                              (155, 155, 0),
                              1,
                              cv2.LINE_AA)
    
    
    if x > lx and x < rx and y > ly and y < ry:
        #uart.send(optimam)
        res = cv2.putText(res, "Inside", (20, 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.75,
                          (0, 255, 255),
                          1,
                          cv2.LINE_AA)
    else:
        if x < lx:
            dx = lx - x
            #print "move left"
            uart.send(left)
            res = cv2.putText(res, "Move left", (20, h - 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.75,
                              (255, 255, 0),
                              1,
                              cv2.LINE_AA)
        if x > rx:
            dx = x - rx
            uart.send(right)
            #print "move right"
            res = cv2.putText(res, "Move right", (20, h - 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.75,
                              (255, 255, 0),
                              1,
                              cv2.LINE_AA)
        if y < ly:
            dy = ly - x
            uart.send(up)
            #print "move up"
            res = cv2.putText(res, "Move up", (20, h - 40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.75,
                              (255, 255, 0),
                              1,
                              cv2.LINE_AA)
        if y > ry:
            dy = y - ry
            uart.send(down)
            #print "move down"
            res = cv2.putText(res, "Move down", (20, h - 40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.75,
                              (255, 255, 0),
                              1,
                              cv2.LINE_AA)
    return res


matcher = RobustMatcher.RobustMatcher()
trainImg = cv2.imread("defaultTrain.jpg")
x=0
y=0
while True:
    frame = cap.read()
    frame = cv2.flip(frame, 1)
    res = frame
    original = frame.copy()

    #Processing here
    res,area,x,y = matcher.bfWithRatioMatcher(trainImg, frame)

    res = checkBounds(res, area, x, y)
    
    res = cv2.rectangle(res, (0, 0), (w, h), (255, 0, 0), 3)        #outside boundary
    res = cv2.rectangle(res, (lx, ly), (rx, ry), (255, 0, 0), 3)    #inside boundary
    res = cv2.circle(res, (w/2, h/2), 2, (255, 0, 0), 3)            #center

    cv2.imshow("Display", frame)

    key = cv2.waitKey(1)
    if key == 27:
        break;
    if key == 32:
        cv2.imwrite("newTrain.jpg", original)
        trainImg = cv2.imread("newTrain.jpg");

cv2.destroyAllWindows()
cap.stop()
