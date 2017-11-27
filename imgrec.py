#!/usr/bin/python

#######################################
# Script for automatically recording  #
# slow framerate videos with the rpi  #
# Author: J. Jolles                   #
# Last updated: 27 Nov 2017           #
#######################################

# Load modules
import picamera
import time
import socket
import os
import subprocess
from fractions import Fraction

# Define recording function
def record(duration = 10, resolution = (1000,1000),
           shutterspeed = 10000, compensation = 0,
           framerate = 0.2, sharpness = 50, iso = 200,
           contrast = 20, brightness = 40, saturation = -100,
           quality = 15):

    """
        Run automated video recording with the rpi camera
        
        Parameters
        ----------
        location : str, default = "NAS"
            Location where images will be stored. This is automatically
            set to the server folder reflecting the rpi name.
        duration : int, default = 60
            Total duration during which images will be recorded
        resolution : tuple, default = (1000,1000)
            The width and height of the images to be recorded.
        framerate : int or fraction, default = Fraction(1,6)
            The framerate at which images should be taken. The minimum
            framerate is 6s, which is provided as the default.
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
        a h264 video
        
    """

    # Set directory to right location
    server = "/home/pi/SERVER/"
    rpi = socket.gethostname()
    foldername = server+rpi
    if os.path.exists(foldername):
        os.chdir(foldername)

    # Get the current date and time
    date = time.strftime("%y%m%d_%H%M%S")

    # Create the video filename
    filename = rpi+"_"+date+".h264"

    print(time.strftime("%H:%M:%S")+" - recording video "+filename)

    # Now record the video
    with picamera.PiCamera() as camera:
        camera.resolution = resolution
        camera.exposure_compensation = compensation
        camera.framerate = framerate
        time.sleep(1)
        camera.exposure_mode = 'off'
        camera.awb_mode = 'off'
        camera.sharpness = sharpness
        camera.shutter_speed = shutterspeed
        camera.iso = iso
        camera.contrast = contrast
        camera.saturation = saturation
        camera.brightness = brightness
        camera.start_recording(filename, quality = quality)
        camera.wait_recording(duration-1)
        camera.stop_recording()

    print(time.strftime("%H:%M:%S")+" - finished video "+filename)

# Run recording function
record()
