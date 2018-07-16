
# coding: utf-8

# In[ ]:


import picamera
import numpy as np
from time import sleep
import cv2
import yaml

def take_img(res = (416, 320)):
    
    res = (int(res[0]),int(res[1]))
    camera = picamera.PiCamera()
    camera.resolution = res
    sleep(1)
    image = np.empty((res[1] * res[0] * 3,), dtype=np.uint8)
    camera.capture(image, 'bgr')
    image = image.reshape((res[1], res[0], 3))

    return image


def drawmask(event, x, y, flags, param):
    global image, image_clone2, points
    
    image = image_clone2.copy()

    if event == cv2.EVENT_MOUSEMOVE and len(points)>0:
        cv2.line(image, points[-1], (x, y), (20,20,20))

    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x,y))
        cv2.polylines(image, np.array([points]), False, (20,20,20), 1)
        cv2.circle(image, (x,y), 4, (0,0,255), -1)
        image_clone2 = image.copy()


        
image = take_img()
image_clone = image.copy()
image_clone2 = image.copy()

points = []

cv2.namedWindow('Image', cv2.WINDOW_NORMAL)
cv2.setMouseCallback('Image', drawmask)


# drawing mode
while True:
    cv2.imshow('Image', image)
    k = cv2.waitKey(1) & 0xFF

    # clear the frame
    if k == ord('e'):
        points = []
        image_clone2 = image_clone

    # Store the data
    if k == ord('s') and len(points)>0:
        #filename = filename+"_mask.jpg"
        print "Edge info written to file.."
        break

    # simply close the window
    if k == 27:
        print "User escaped.."
        break
        
# close video and windows
cv2.destroyAllWindows()
cv2.waitKey(1)

# convert points
points = str([i*2 for i in points])

# write edge info to file
with open("setup/edgecoords.yml", 'w') as f:
    yaml.safe_dump(points, f, default_flow_style=False)

