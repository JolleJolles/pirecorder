
# coding: utf-8

# In[ ]:

#!/usr/bin/python

import picamera
import time
import os
import socket
import cPickle
from decimal import Decimal
import subprocess
from ast import literal_eval

# define recording function
def record(imgwait = 5.0):
    # set-up the camera with the right parameters
    camera = picamera.PiCamera()
    sleep(0.1)
    camera.exposure_mode = 'off'
    camera.awb_mode = 'off'
    for i, img in enumerate(camera.capture_continuous("{timestamp:%Y%m%d}", format="jpeg")):
        if i == imgnr:
            break
        print i
        sleep(2)

