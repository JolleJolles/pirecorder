
# coding: utf-8

# In[ ]:

#!/usr/bin/python

#######################################
# Script for recording video with RPi #
# Author: J. Jolles ; Version: 3.10.5 #
# Last updated: 12 Apr 2018           #
#######################################

#3.10.6: Changed loading of gains file
#3.10.5: Check if NAS folder is mountpoint, otherwise write files to home folder
#3.10.4: Added automatic rotation based on the rpi number
#3.10.3: Added some more description
#3.10.2: Fixed folder naming and filenaming when running single
#3.10.1: Improved storage location naming to record to different folders
#3.10.0: Integrated shutterspeed
#3.9.3: Rpi name now changes jolpi names to RPiXX nr
#3.9.2: Decided to make tasks 5 characters and standard task "pilot"
#3.9.1: Changed file naming convention
#3.8.3: Made some small corrections
#3.8.2: Removed cnverting as rpi was too slow
#3.8.1: Included converting to right types for runp external function calling
#3.7: Made some fixes so file works flawlessly
#3.6: Added way to provide location where videos are stored
#3.5: Made many updates and changes to create more final script
#3.2: Created record function where user can enter parameters directly
#3.1: Added converting to mp4 container (takes few seconds)
#3.0: Rewrote script for Laurens experiment
#2.7: Video now takes a screenshot in foraging mode after 15s
#2.6: Included a foraging video mode
#2.5: script now takes a picture beforehand to show film region
#2.4: implemented user setting duration
#2.3: fixed roi not cropping
#2.2: incorporated crop.p file and fixed errors
#2.1: Made file work on rpi

# set up the workspace
import picamera
import time
import os
import socket
import cPickle
from decimal import Decimal
import subprocess
from ast import literal_eval

# define recording function
def record(location = "NAS",
           task = "pilot", 
           single = "no", 
           duration = 10, 
           delay = 0, 
           width = 1640, 
           height = 1232, 
           compensation = 0, 
           shutterspeed = 10000, 
           iso = 200, 
           brightness = 55, 
           sharpness = 50, 
           contrast = 15,
           saturation = -100, 
           quality = 18,
           fps = 12,
           autorotate = "yes"):
    
    """
        Run automated recording sessions with the rpi camera
        
        Parameters
        ----------
        location : str, default = "NAS"
            Location where videos will be stored. Default is "NAS",
            which is the automatically mounted NAS drive. New folder
            will be created based on alternative location name. Providing
            no name stores in home directory.
        task : str, default = "pilot"
            Name of task used. Always use five characters.
        single : str, default = "no"
            If a single video should be record, yes or no. 
            Alternatively, user is asked for session 
            information and id information continuously until 
            the user quits the script.
        duration : int, default = 10
            Total duration of the trials in seconds.
        delay : int, default = 0
            Extra recording time in seconds. Main use is for
            wanting to film acclimatisation time. 
        width : int, default = 1640
            The width dimension of the camera resolution.
        height : int, default 1232
            The height dimension of the camera resolution. Max 
            possible resolution is pixel size of default. Beyond
            that size, camera will throw an error.
        shutterspeed : int, detault = 10000
            Shutter speed of the camera in microseconds. Thus the
            default of 10000 is equivalent to 1/100th of a second
        compensation : int, default = 0
            Camera lighting compensation. Ranges between 0 and 20.
        fps : int, default = 12
            The recording framerate. After 30 fps, camera will 
            start to automatically lower resolution to accomodate
            the requested fps.
        sharpness : int, default = 50
            The sharpness of the camera. Valid values are 
            between -100 and 100.
        iso : int, default = 200
            The camera iso value. Higher values are more light
            sensitive but have higher gain. Valid
            values are between 0 (auto) and 1600.
        contrast : int, default = 15
            The camera contrast. Valid values are 
            between -100 and 100.
        brightness : int, default = 55
            The brightness level of the camera. Valid values
            are between 0 and 100.
        saturation : int, default -100
            The color saturation level of the camera. Valid 
            values are between -100 and 100.
        quality : int, default 18
            Specifies the quality that the encoder should attempt
            to maintain. Valid values are between 10 and 40, where
            10 is extremely high quality, and 40 is extremely low.
        autorotate : bool, default True
            If the camera image should be automatically rotated based 
            on the raspberrpi location (1,3,5,7 are rotated 180)
            
        Output
        -------
        h264 video of trial

        Note: Filenaming convention is:
        date(yymmdd)_task_RPI(RP+2nr)_session(S+2nr)_ID(F+3nr/GR+2nr).h264
            
    """
    
    # Convert input parameters (all string), needed when using runp 
    # external function calling
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
    rpi = "RPi"+rpi[6:8]
    date = time.strftime("%y%m%d")
    if os.path.exists("setup/gains.pk"):
        awb = cPickle.load(open('setup/gains.pk', 'rb'))[0]
    else:
        awb = (1.5, 2.4)
        
    # Camera rotation
    if autorotate == "yes":
        rotation = 180 if rpi in ["RPi01","RPi03","RPi05","RPi07"] else 0
    
    # Check if NAS is mounted, if not store in home folder instead
    if not os.path.ismount("NAS"):
        location = ""

    # Change location where videos are stored
    location = "/home/pi/"+location
    
    # Check if folder exisrts
    if not os.path.exists(location):
        os.makedirs(location)
    os.chdir(location)

    # Print recording settings
    print time.strftime("%H:%M:%S")+" - Recording with following settings: location: "+location+           "; duration "+str(duration+delay)+"sec; resolution: "+str(resolution)+"; shutterspeed: "+           str(shutterspeed/1000)+"ms; compensation: "+str(compensation)+"; fps: "+str(fps)+           "; sharpness: "+str(sharpness)+"; iso: "+str(iso)+"; contrast: "+str(contrast)+           "; brightness: "+str(brightness)+"; saturation: "+str(saturation)+"; and quality: "+str(quality)+"\n"

    while True:
        print(time.strftime("%H:%M:%S")+" - New session started")

        # Ask for session and id information when not single
        if single == "no":
            
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
                    
        # Single
        else:
            filename = date+"_"+task+"_"+rpi+"_"+time.strftime("%H%M%S")+"_U.h264"
        
        # Start recording
        print(time.strftime("%H:%M:%S")+" - Starting up...")
        with picamera.PiCamera() as camera:
            camera.resolution = resolution
            camera.exposure_compensation = compensation
            camera.framerate = fps
            camera.rotation = rotation
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

