
# coding: utf-8

# In[ ]:

#!/usr/bin/python

#######################################
# Script for automatically recording  #
# slow framerate videos with the rpi  #
# Author: J. Jolles                   #
# Last updated: 28 Nov 2017           #
#######################################

# import packages
from picamera import PiCamera
from time import sleep, strftime
from datetime import datetime as dt
from socket import gethostname
import os

# define recording function
def record(imgwait = 5.0,
           imgnr = 100,
           imgtime = 600,
           resolution = (1000, 1000),
           compensation = 0,
           shutterspeed = 10000,
           iso = 200,
           brightness = 40,
           sharpness = 50,
           contrast = 20,
           saturation = -100,
           quality = 20):
    
    """
        Run automated image recording with the rpi camera
        
        Storage location
        ----------
        The folder where the images will be stored is automatically
        set to the folder on the server that reflects the rpi name,
        for example /home/pi/SERVER/pi41.
        
        Parameters
        ----------
        imgwait : float, default = 5.0
            The delay between subsequent images in seconds. When a 
            delay is provided that is less than shutterspeed + 
            processingtime "delay" will be automatically set at 0 
            and images thus taken one after the other.
        imgnr : integer, default = 100
            The number of images that should be taken. When this 
            number is reached the script will automatically terminate.
            The minimum of imgnr and nr of images based on imgwait and
            imgtime will be selected.
        imgtime : integer, default = 10
            The time in minutes during which images should be taken.
            The minimum of imgnr and nr of images based on imgwait and
            imgtime will be selected.
        resolution : tuple, default = (1000, 1000)
            The width and height of the images that will be recorded.
        compensation : int, default = 0
            Camera lighting compensation. Ranges between 0 and 20.
            Compensation artificially adds extra light to the image.
        shutterspeed : int, detault = 10000
            Shutter speed of the camera in microseconds, i.e. the
            default of 10000 is equivalent to 1/100th of a second. A
            longer shutterspeed will result in a brighter image but
            more likely motion blur.
        iso : int, default = 200
            The camera iso value. Higher values are more light
            sensitive but have higher gain. Valid values are
            between 200 and 1600.
        brightness : int, default = 55
            The brightness level of the camera. Valid values are
            between 0 and 100.
        sharpness : int, default = 50
            The sharpness of the image, an integer value between -100
            and 100.
        contrast : int, default = 20
            The image contrast, an integer value between 0 and 100.
        saturation : int, default -100
            The color saturation level of the image, an integer
            value between -100 and 100.
        quality : int, default = 20
            Defines the quality of the JPEG encoder as an integer
            ranging from 1 to 100. Defaults to 20.
        
        Output
        -------
        A series of JPEG images, automatically named based on 
        the rpi number, date, and time, following a standard 
        naming convention, e.g. pi11_172511_im00010_153012.jpg
        
        """
    
    print "=================================================="
    print strftime("imgrec started: Date: %y/%m/%d; Time: %H:%M:%S")
    print "=================================================="
    
    # Change type for use with runp
    imgwait = float(imgwait)
    #imgnr = int(imgnr)
    #imgtime = int(imgtime)
            
    # get number of images to record
    totimg = int(imgtime * (60 / imgwait))
    imgnr = min(imgnr, totimg)
    
    # acquire rpi name
    rpi = gethostname()
    
    # set the directory
    server = "/home/pi/SERVER/"
    location = server + rpi
    if os.path.exists(location):
        os.chdir(location)
    
    # set-up automatic filenaming
    daystamp = "_{timestamp:%Y%m%d}"
    counter = "_im{counter:05d}"
    timestamp = "_{timestamp:%H%M%S}"
    ftype = ".jpg"
    filename = rpi+daystamp+counter+timestamp+ftype

    # set-up the camera with the right parameters
    camera = PiCamera()
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
    
    # start taking images
    bef = dt.now()
    for i, img in enumerate(camera.capture_continuous(filename, format="jpeg", quality=quality)):
        if i == imgnr:
            break
        delay = imgwait-(dt.now()-bef).total_seconds()
        delay = 0 if delay < 0 else delay
        print strftime("[%H:%M:%S][") + rpi + "] - captured " + img +               ", sleeping " + str(round(delay,2)) + "s.."
        sleep(delay)
        bef = dt.now()
    
    print "=================================================="
    print strftime("imgrec stopped: Date: %y/%m/%d; Time: %H:%M:%S")

