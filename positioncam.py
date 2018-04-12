
# coding: utf-8

# In[ ]:

# Import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
from time import sleep
import cv2
 
# Initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (832, 624)
rawCapture = PiRGBArray(camera)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(832, 624))
#camera.zoom = (0.0,0.0,1.0,1.0)
#camera.exposure_compensation = 0
 
# Allow the camera to warmup
sleep(0.1)
 
# Capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    
    # Grab the raw NumPy array representing the image, then initialise the timestamp
    # and occupied/unoccupied text
    image = frame.array

    # Resize
    #image = cv2.resize(image,(832, 624))

    # Draw lines
    cv2.line(image, (1,1), (832, 624), color=(255,255,255), thickness=2)
    cv2.line(image, (832, 1), (1, 624), color=(255,255,255), thickness=2)

    # Display the image on screen
    cv2.imshow("Image", image)
    k = cv2.waitKey(1) & 0xFF

    # Clear the stream in preparation for the next frame
    rawCapture.truncate(0)
    
    # Stop when escape is pressed
    if k == 27:
        break

