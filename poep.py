
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

# Define functions
def run(single = "no"):
        
    camera = picamera.PiCamera()
    camera.framerate = 10
    time.sleep(1)
    camera.exposure_mode = 'off'
    camera.awb_mode = 'off'
    print(time.strftime("%H:%M:%S")+" - Recording video")
    camera.start_recording("sint.h264", quality = 10)
    camera.wait_recording(5)
    camera.stop_recording()

