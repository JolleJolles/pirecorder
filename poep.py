
# coding: utf-8

# In[ ]:

#!/usr/bin/python

import picamera
from time import sleep, strftime
import os
import socket
import cPickle
from decimal import Decimal
import subprocess
from ast import literal_eval

# define recording function
def record(imgwait = 5.0,
           imgnr = 3,
           imgtime = 1,
           resolution = (1000, 1000),
           compensation = 0,
           shutterspeed = 10000,
           iso = 200,
           brightness = 40,
           sharpness = 50,
           contrast = 20,
           saturation = -100,
           quality = 20):
    
    print "=================================================="
    print strftime("imgrec started: Date: %y/%m/%d; Time: %H:%M:%S")
    print "=================================================="
    
    imgwait = float(imgwait)
    imgtime = int(imgtime)
    imgnr = int(imgnr)
    
    # get number of images to record
    print type(imgtime), type(imgwait)
    print imgtime, imgwait
    totimg = int(imgtime * (60 / imgwait))
    imgnr = min(imgnr, totimg)
    
    
    
    # set-up automatic filenaming
    daystamp = "_{timestamp:%Y%m%d}"
    counter = "_im{counter:05d}"
    timestamp = "_{timestamp:%H%M%S}"
    ftype = ".jpg"
    rpi = "jolpi10"
    filename = rpi+daystamp+counter+timestamp+ftype

    # set-up the camera with the right parameters
    camera = picamera.PiCamera()
    camera.resolution = resolution
    camera.exposure_compensation = compensation
    sleep(0.1)
    camera.exposure_mode = 'off'
    camera.awb_mode = 'off'
    camera.shutter_speed = shutterspeed
    camera.sharpness = sharpness
    camera.iso = iso
    camera.contrast = contrast
    camera.saturation = saturation
    camera.brightness = brightness

    for i, img in enumerate(camera.capture_continuous("{timestamp:%Y%m%d}", format="jpeg")):
        if i == imgnr:
            break
        print i
        sleep(imgwait)
        
    print "=================================================="
    print strftime("imgrec stopped: Date: %y/%m/%d; Time: %H:%M:%S")

