
# coding: utf-8

# In[ ]:


#!/usr/bin/python

#######################################
# Script for automatically recording  #
# slow framerate videos with the rpi  #
# Author: J. W. Jolles                #
# Last updated: 4 Dec 2017            #
# Version: 1.0.0                      #
#######################################

#1.0.0: imgrec final and published

# import packages
import picamera
from time import sleep, strftime
import datetime
from socket import gethostname
import argparse
import os
import csv
from ast import literal_eval
from fractions import Fraction

# define recording function
def record(location = "pi",
           imgwait = 5.0,
           imgnr = 100,
           imgtime = 600,
           resolution = (1000, 1000),
           compensation = 0,
           shutterspeed = 8000,
           iso = 200,
           brightness = 30,
           sharpness = 0,
           contrast = 10,
           saturation = -100,
           quality = 17,
           roifile = "/home/pi/roifile.txt"):
    
    """
        A fully automated image recording script for the rpi
                
        Parameters
        ----------
        location : str, default = "pi"
            The location where the images are stored. By default, 
            when location is "pi", this is automatically set to 
            the folder on the server corresponding to the rpi name, 
            for example /home/pi/SERVER/pi41. If different, a folder 
            with name corresponding to location will be created
            inside the home directory. Images are stored in separate 
            automatically created folders each day.
        imgwait : float, default = 5.0
            The delay between subsequent images in seconds. When a 
            delay is provided that is less than shutterspeed + 
            processingtime, it will be automatically set to 0 
            and images thus taken immideately one after the other.
        imgnr : int, default = 100
            The number of images that should be taken. When this 
            number is reached, the script will automatically terminate.
            The minimum of a) imgnr and b) nr of images based on 
            imgwait and imgtime will be selected.
        imgtime : integer, default = 600
            The time in seconds during which images should be taken.
            The minimum of a) imgnr and b) nr of images based on 
            imgwait and imgtime will be selected.
        resolution : tuple, default = (1000, 1000)
            The width and height of the to-be recorded images in 
            pixels.
        compensation : int, default = 0
            Camera lighting compensation. Ranges between 0 and 20.
            Compensation artificially adds extra light to the image.
        shutterspeed : int, detault = 10000
            Shutter speed of the camera in microseconds, i.e. the
            default of 10000 is equivalent to 1/100th of a second. A
            longer shutterspeed will result in a brighter image but
            more motion blur.
        iso : int, default = 200
            The camera ISO value, an integer value in sequence 
            [200,400,800,1600]. Higher values are more light
            sensitive but have higher gain.
        brightness : int, default = 55
            The brightness level of the camera, an integer value 
            between 0 and 100.
        sharpness : int, default = 50
            The sharpness of the camera, an integer value between 
            -100 and 100.
        contrast : int, default = 20
            The image contrast, an integer value between 0 and 100.
        saturation : int, default -100
            The color saturation level of the image, an integer
            value between -100 and 100.
        quality : int, default = 20
            The quality of the JPEG encoder, as an integer
            ranging from 1 to 100. Defaults to 20.
        roifile : str, default = /home/pi/roifile.txt
            The filename for the txt file that contains the region 
            of interest. This should be provided on one line as 
            (x, y, w, h) with parentheses, i.e. a tuple of floating 
            point values ranging from 0.0 to 1.0. The default value 
            is (0.0, 0.0, 1.0, 1.0).
        
        Output
        -------
        A series of JPEG images, automatically named based on 
        the rpi number, date, and time, following the standard 
        naming convention: piXX_YYMMDD_im%04d_HHMMSS.jpg
        
        """
    
    # acquire rpi name
    rpi = gethostname()
    
    # print starting statement
    print strftime("[%H:%M:%S][") + rpi + "] - imgrec started. The date is "+strftime("%y/%m/%d")           
    
    # convert input to right type (for using runp)
    imgwait = float(imgwait)
    imgnr = int(imgnr)
    imgtime = int(imgtime)
    resolution = tuple(resolution)
    compensation = int(compensation)
    shutterspeed = int(shutterspeed)
    iso = int(iso)
    brightness = int(brightness)
    sharpness = int(sharpness)
    contrast = int(contrast)
    saturation = int(saturation)
    quality = int(quality)
    
    # when imgwait is close to zero, change to mininum
    # value that roughly equals time to take image
    mintime = 0.45
    imgwait = mintime if imgwait < mintime else imgwait

    # get number of images to record
    totimg = int(imgtime / imgwait)
    imgnr = min(imgnr, totimg)
    
    # set fps based on shutterspeed
#    shuttsec = shutterspeed / float(1000000)
#    if shuttsec <= 1:
#        fps = int(1/shuttsec)-1
#    else:
#        fps = Fraction(1,int(shuttsec)+1)
    fps = 4
    
#    # bound fps to min (40fps) and max (1/6th fps)
#    fps = 40 if fps>40 else fps
#    fps = Fraction(1,6) if 1/fps>6 else fps
    
    # set the directory 
    if location == "pi":
        server = "/home/pi/SERVER/"
        location = server + rpi
        
        # add date folder
        location = location + strftime("/%y%m%d")
    else:
        location = "/home/pi/"+location
    if not os.path.exists(location):
        os.makedirs(location)
    os.chdir(location)
    
    # set-up automatic filenaming
    daystamp = "_{timestamp:%Y%m%d}"
    counter = "_im{counter:05d}"
    timestamp = "_{timestamp:%H%M%S}"
    ftype = ".jpg"
    filename = rpi + daystamp + counter + timestamp + ftype
    
    # set the roi
    if os.path.exists(roifile):
        reader = csv.reader(open(roifile, "r"))
        zoom = next(reader)[0]
        zoom = literal_eval(zoom)
    else:
        zoom = (0.0,0.0,1.0,1.0)
    
    # set-up the camera with the right parameters
    camera = picamera.PiCamera()
    camera.framerate = fps
    camera.resolution = resolution
    camera.zoom = zoom
    camera.exposure_compensation = compensation
    sleep(1)
    camera.exposure_mode = 'off'
    camera.awb_mode = 'off'
    camera.awb_gains = (Fraction(405, 256), Fraction(57, 32))
    camera.shutter_speed = shutterspeed
    camera.sharpness = sharpness
    camera.iso = iso
    camera.contrast = contrast
    camera.saturation = saturation
    camera.brightness = brightness
    
    # start taking images
    bef = datetime.datetime.now()
    for i, img in enumerate(camera.capture_continuous(filename, 
                            format="jpeg", quality=quality)):
        
        # stop when image number is reached
        if i == (imgnr-1):
            print strftime("[%H:%M:%S][") + rpi + "] - captured " + img + "\n"
            break
        
        # calculate delay and wait before taking next image
        delay = imgwait-(datetime.datetime.now()-bef).total_seconds()
        delay = 0 if delay < 0 else delay
        print strftime("[%H:%M:%S][") + rpi + "] - captured " + img +              ", sleeping " + str(round(delay,2)) + "s.."
        sleep(delay)
        bef = datetime.datetime.now()

    # release camera when finished
    camera.close()

# only execute record function when file is run
if __name__ == '__main__':
    record()

