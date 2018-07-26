
# coding: utf-8

# In[ ]:


#!/usr/bin/python

#######################################
# Script for automatically recording  #
# slow framerate videos with the rpi  #
# Author: J. W. Jolles                #
# Last updated: 4 Dec 2017            #
# Version: 1.1.2                      #
#######################################

#1.2.0
#1.1.2: change default parameters to get images with even smaller filesize
#1.1.1: fixed resolution issue
#1.1.0: it is now possible to record images at low shutterspeeds of up to 1s
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
           single = "no",
           imgwait = 5.0,
           imgnr = 100,
           imgtime = 600,
           width = 3280,
           height = 2464,
           compensation = 0,
           shutterspeed = 8000,
           iso = 200,
           brightness = 45,
           sharpness = 0,
           contrast = 10,
           saturation = -100,
           quality = 11):
    
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
        single : str, default = "no"
            If a single image should be record, yes or no. 
        imgwait : float, default = 5.0
            The delay between subsequent images in seconds. When a 
            delay is provided that is less than ~0.5s (shutterspeed + 
            processingtime) it will be automatically set to 0 
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
        width : int, default = 3280
            The width of the image in pixels.
        height : int, default = 2464
            The height of the image in pixels.
        compensation : int, default = 0
            Camera lighting compensation. Ranges between 0 and 20.
            Compensation artificially adds extra light to the image.
        shutterspeed : int, detault = 10000
            Shutter speed of the camera in microseconds, i.e. the
            default of 10000 is equivalent to 1/100th of a second. A
            longer shutterspeed will result in a brighter image but
            more motion blur. Important: the framerate of the camera
            will be adjusted based on the shutterspeed. At shutter-
            speeds above ~ 0.2s this results in increasingly longer
            waiting times between images so a standard imgwait time
            should be chosen that is 6+ times more than the
            shutterspeed. For example, for a shutterspeed of 300000
            imgwait should be > 1.8s.
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
        roifile : str, default = /home/pi/setup/roifile.txt
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
    print strftime("[%H:%M:%S][") + rpi + "] - imgrec started. The date is "+strftime("%y/%m/%d")+". Warming up..."           
    
    # convert input to right type (for using runp)
    imgwait = float(imgwait)
    imgnr = int(imgnr)
    imgtime = int(imgtime)
    resolution = (int(width),int(height))
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
    shuttsec = shutterspeed / float(1000000)
    if shuttsec < 0.025:
        fps = 40
    elif shuttsec <= 1:
        fps = int(1/shuttsec)
    else:
        print "shutterspeed too low.. reverting back to framerate of 1fps"
        fps = 1

    # set the directory 
    if location == "pi":
        server = "/home/pi/NAS/"
        location = server
        
        # add date folder
        if single == "no":
            location = location + strftime("/%y%m%d")
    else:
        location = "/home/pi/"+location
    if not os.path.exists(location):
        os.makedirs(location)
    os.chdir(location)
    
    # set-up automatic filenaming
    if single == "yes":
        filename = rpi + "_" + strftime("%H%M%S") + ".jpg"
    else:
        daystamp = "_{timestamp:%Y%m%d}"
        counter = "_im{counter:05d}"
        timestamp = "_{timestamp:%H%M%S}"
        ftype = ".jpg"
        filename = rpi + daystamp + counter + timestamp + ftype
    
    
    # set the roi
    roifile = "/home/pi/setup/roifile.yml"
    if os.path.exists(roifile):
        with open(roifile) as f:
            zoom += yaml.load(f)
        zoom = literal_eval(zoom)
        print "Custom roi loaded..",
    else:
        zoom = (0.0,0.0,1.0,1.0)
    
    # set custom brightness
    brightfile = "/home/pi/setup/cusbright.yml"
    if os.path.exists(brightfile):
        with open(brightfile) as f:
            brightness += yaml.load(f)
        print "Custom brightness loaded:",brightness,
    else:
        print "standard brightness..",
    
    # set custom gains
    gainsfile = "/home/pi/setup/cusgains.yml"
    if os.path.exists(gainsfile):
        with open(gainsfile) as f:
            awb = literal_eval(awb)
        print "Custom gains loaded:",awb,
    else:
        awb = (1.5, 2.4)
        print "standard gains..",
    
    # set-up the camera with the right parameters
    camera = picamera.PiCamera()
    camera.framerate = fps
    camera.resolution = resolution
    camera.zoom = zoom
    camera.exposure_compensation = compensation
    sleep(5)
    camera.exposure_mode = 'off'
    camera.awb_mode = 'off'
    camera.awb_gains = awb
    camera.shutter_speed = shutterspeed
    camera.sharpness = sharpness
    camera.iso = iso
    camera.contrast = contrast
    camera.saturation = saturation
    camera.brightness = brightness
    
    # start taking images
    bef = datetime.datetime.now()
    if single == "yes":
        camera.capture(filename, format="jpeg", quality=quality)
    else:
        for i, img in enumerate(camera.capture_continuous(filename, 
                                format="jpeg", quality=quality)):

            # stop when image number is reached
            if i == (imgnr-1):
                print strftime("[%H:%M:%S][") + rpi + "] - captured " + img + "\n"
                break

            # calculate delay and wait before taking next image
            delay = imgwait-(datetime.datetime.now()-bef).total_seconds()
            delay = 0 if delay < 0 else delay
            print strftime("[%H:%M:%S][") + rpi + "] - captured " + img +                  ", sleeping " + str(round(delay,2)) + "s.."
            sleep(delay)
            bef = datetime.datetime.now()
            print bef

    # release camera when finished
    camera.close()

# only execute record function when file is run
if __name__ == '__main__':
    record()

