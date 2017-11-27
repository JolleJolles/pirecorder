from time import sleep
from picamera import PiCamera

camera = PiCamera(resolution=(1280, 720), framerate=30)
# Set ISO to the desired value
camera.iso = 100
# Wait for the automatic gain control to settle
sleep(2)
# Now fix the values
camera.shutter_speed = camera.exposure_speed
camera.exposure_mode = 'off'
g = camera.awb_gains
camera.awb_mode = 'off'
camera.awb_gains = g
# Finally, take several photos with the fixed settings
camera.capture_sequence(['image%02d.jpg' % i for i in range(10)])


from time import sleep
from picamera import PiCamera

camera = PiCamera()
camera.start_preview()
sleep(2)
for filename in camera.capture_continuous('img{counter:03d}.jpg'):
    print('Captured %s' % filename)
    sleep(300) # wait 5 minutes



#!/usr/bin/python

#######################################
# Script for automatically recording  #
# images with the rpi                 #
# Author: J. Jolles                   #
# Last updated: 27 Nov 2017           #
#######################################

# Set up the workspace
import picamera
import time
import os
import socket
import cPickle
from decimal import Decimal
import subprocess
from ast import literal_eval

# Define functions
def record(duration = 600,
           delay = 30, width = 1640, height = 1232, shutterspeed = 10000, compensation = 0, fps = 12,
           sharpness = 50, iso = 200, contrast = 15, brightness = 55,
           saturation = -100, quality = 18):

    """
        Run automated recording sessions with the rpi camera
        
        Parameters
        ----------
        location : str, default = "NAS"
            Location where images will be stored. This is automatically
            set to the server folder reflecting the rpi name.
        duration : int, default = 60
            Total duration during which images will be recorded
        delay : int, default = 5
            Time delay between images
        width : int, default = 1640
            The width of the images to be recorded.
        height : int, default 1232
            The height of the images to be recorded.
        shutterspeed : int, detault = 10000
            Shutter speed of the camera in microseconds. Thus the
            default of 10000 is equivalent to 1/100th of a second
        compensation : int, default = 0
            Camera lighting compensation. Ranges between 0 and 20.
            Compensation artificially adds extra light to the image.
        sharpness : int, default = 50
            The sharpness of the image. Valid values are between
            -100 and 100.
        iso : int, default = 200
            The camera iso value. Higher values are more light
            sensitive but have higher gain. Valid values are
            between 0 (auto) and 1600.
        contrast : int, default = 15
            The camera contrast. Valid values are between -100
            and 100.
        brightness : int, default = 55
            The brightness level of the camera. Valid values are
            between 0 and 100.
        saturation : int, default -100
            The color saturation level of the camera. Valid values
            are between -100 and 100.
        quality : int, default 18
            Specifies the quality that the encoder should attempt
            to maintain. Valid values are between 10 and 40, where
            10 is extremely high quality, and 40 is extremely low.
            
        Output
        -------
        a series of jpg images
        
    """
    # Set the parameters
    duration = int(duration)
    delay = int(delay)
    resolution = (int(width),int(height))
    shutterspeed = int(shutterspeed)
    compensation = int(compensation)
    fps = int(fps)
    sharpness = int(sharpness)
    iso = int(iso)
    contrast = int(contrast)
    brightness = int(brightness)
    saturation = int(saturation)
    quality = int(quality)
      
    # Load automatic settings
    rpi = socket.gethostname()
    rpi = "C"+rpi[5:7]
    date = time.strftime("%y%m%d")
    if os.path.exists("setup.gains.pk"):
        awb = cPickle.load(open('setup.gains.pk', 'rb'))[0]
    else:
        awb = (1.5, 2.4)

    # Change location where videos are stored
    location = "/home/pi/"+location
    if not os.path.exists(location):
        os.makedirs(location)
    os.chdir(location)

    # Print recording settings
    print time.strftime("%H:%M:%S")+" - Recording with following settings: location: "+location+"; duration "+str(duration+delay)+"sec; resolution: "+str(resolution)+"; shutterspeed: "+str(shutterspeed/1000)+"ms; compensation: "+str(compensation)+"; fps: "+str(fps)+"; sharpness: "+str(sharpness)+"; iso: "+str(iso)+"; contrast: "+str(contrast)+"; brightness: "+str(brightness)+"; saturation: "+str(saturation)+"; and quality: "+str(quality)+"\n"

    while True:
        print(time.strftime("%H:%M:%S")+" - New session started")

        # Ask for session and id information when not single
        if single == "yes":
            filename = date+"_"+task+"_"+rpi+"_"+time.strftime("%H%M%S")+"_U.h264"
            
        else:
            # Ask for session nr and check if input is correct
            while True:
                session = raw_input("Session nr (e.g. S01): ")
                if len(session) != 3:
                    print "Session nr should be 3 characters long, try again"
                    continue
                else:
                    break

            # Ask for ID nr and check if input is correct
            while True:
                idnr = raw_input("Fish/Group ID (e.g. F101 or GR20): ")
                if len(idnr) != 4:
                    print "ID should be 4 characters long, try again"
                    continue
                else:
                    break

            # Create filename
            filename = date+"_"+task+"_"+rpi+"_"+session+"_"+idnr+".h264"
        
        # Start recording
        print(time.strftime("%H:%M:%S")+" - Starting up...")
        with picamera.PiCamera() as camera:
            camera.resolution = resolution
            camera.exposure_compensation = compensation
            camera.framerate = fps
            time.sleep(1)
            camera.exposure_mode = 'off'
            camera.awb_mode = 'off'
            camera.awb_gains = awb
            camera.sharpness = sharpness
            camera.shutter_speed = shutterspeed
            camera.iso = iso
            camera.contrast = contrast
            camera.saturation = saturation
            camera.brightness = brightness
            print(time.strftime("%H:%M:%S")+" - Recording video "+filename)
            camera.start_recording(filename, quality = quality)
            camera.wait_recording(duration + delay)
            camera.stop_recording()

        if single == "yes":
            break
        else:
            answer = raw_input("\nPress ENTER to start new session or 'e' to exit: ")
            if answer == 'e':
                break
            else:
                continue


