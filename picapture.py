
# coding: utf-8

# In[ ]:


#!/usr/bin/python

# Import packages
import picamera
from time import sleep, strftime
import datetime
from socket import gethostname
import os
import yaml
from ast import literal_eval
from fractions import Fraction

# Initial setting up
home = "/home/pi/"
rpi = gethostname()
lineprint = strftime("[%H:%M:%S][") + rpi + "] -",

# Define functions
def yamyam(filename, value = None, add = True):
    if os.path.exists(filename):
        with open(filename) as f:
            newvalue = yaml.load(f)
        if value is not None:
            if add:
                newvalue += value
            else:
                newvalue = value
    else:
        newvalue = value
        
    return newvalue


def customsetup(rpi, autorotate, brightfile = "cusbright.yml", gainsfile = "cusgains.yml", roifile = "roifile.yml"):

    # Set crop
    zoom = yamyam(HOME + "setup/" + roifile, "(0.0,0.0,1.0,1.0)", False)
    zoom = literal_eval(zoom)
        
    # Set brightness
    brightness = yamyam(HOME + "setup/" + brightfile, brightness, True)
    
    # Set gains
    awb = yamyam(HOME + "setup/" + gainsfile, awb, False)
    awb = literal_eval(awb)
    
    # Camera rotation
    rotation = 0
    if autorotate == "yes":
        rotation = 180 if rpi in ["jolpi101","jolpi103","jolpi105","jolpi107"] else 0
    
    return zoom, brightness, awb, rotation


def record(location = "NAS",
           single = "no",
           task = "test",
           rectype = "img",
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
           quality = 11,
           autorotate = "yes"):
    
    """
        A fully automated image recording script for the rpi
                
        Parameters
        ----------
        location : str, default = "NAS"
            The location where media is stored. Default is "NAS",
            which is the automatically mounted NAS drive. If different, 
            a folder with name corresponding to location will be created
            inside the home directory. Images are stored in separate 
            automatically created folders each day. Providing no name 
            stores in home directory.
        single : str, default = "no"
            If a single image should be record, yes or no. 
        task : str, default = "test"
            Name of task used.
        rectype : str, default = "img"
            Recording type, either img or video.
        duration : int, default = 10
            *Video parameter only*. Total duration of the trials in 
            seconds.
        delay : int, default = 0
            *Video parameter only*. Extra recording time in seconds. 
            Main use is for filming acclimatisation time. 
        imgwait : float, default = 5.0
            *Image parameter only*. The delay between subsequent images 
            in seconds. When a delay is provided that is less than ~0.5s 
            (shutterspeed + processingtime) it will be automatically set 
            to 0 and images thus taken immideately one after the other.
        imgnr : int, default = 100
            *Image parameter only*. The number of images that should be 
            taken. When this number is reached, the script will automatically 
            terminate. The minimum of a) imgnr and b) nr of images based on 
            imgwait and imgtime will be selected.
        imgtime : integer, default = 600
            *Image parameter only*. The time in seconds during which images 
            should be taken. The minimum of a) imgnr and b) nr of images 
            based on imgwait and imgtime will be selected.
        width : int, default = 1640
            The width of the image in pixels.
        height : int, default = 1232
            The height of the image in pixels. For video recording,
            max dimensions are 1640 x 1232.
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
        brightness : int, default = 45
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
        quality : int, default = 11
            Specifies the quality that the encoder should attempt
            to maintain. Valid values are between 10 and 40, where
            10 is extremely high quality, and 40 is extremely low.
        autorotate : bool, default True
            If the camera image should be automatically rotated based 
            on the raspberrpi location (1,3,5,7 are rotated 180)
        
        Output
        -------
        For videos a .h264 file and for images a .jpg file. When not 
        single, a series of JPEG images will be created. All files are
        automatically named based on the rpi name, date, and time.
        """
    
    # Print starting statement
    print lineprint + "Recording started. The date is "+strftime("%y/%m/%d")+". Warming up..."           
    
    # Convert input to right type (with runp)    
    #----------------------------
    #general settings
    resolution = (int(width),int(height))
    compensation = int(compensation)
    shutterspeed = int(shutterspeed)
    iso = int(iso)
    brightness = int(brightness)
    sharpness = int(sharpness)
    contrast = int(contrast)
    saturation = int(saturation)
    quality = int(quality)
    
    #img settings
    imgwait = float(imgwait)
    imgnr = int(imgnr)
    imgtime = int(imgtime)
    
    #video settings
    duration = int(duration)
    delay = int(delay)
    fps = int(fps)
    
    
    # Make sure image recording settings are correct
    if rectype == "img":

        # When imgwait is close to zero, change to mininum
        # value that roughly equals time to take image
        mintime = 0.45
        imgwait = mintime if imgwait < mintime else imgwait

        # Calculate number of images to record
        totimg = int(imgtime / imgwait)
        imgnr = min(imgnr, totimg)
    
        # Set fps based on shutterspeed
        shuttsec = shutterspeed / float(1000000)
        if shuttsec < 0.025:
            fps = 40
        elif shuttsec <= 1:
            fps = int(1/shuttsec)
        else:
            print "shutterspeed too low.. reverting back to framerate of 1fps"
            fps = 1

    # Set directory
    #----------------------------
    location = HOME + location
    
    # Check if location is mounted when NAS
    if not os.path.ismount(location):
        location = ""
    
    # Add date folder for image sequence
    if rectype == "img" and single == "no":
        location = location + strftime("/%y%m%d")

    # Change to directory
    if not os.path.exists(location):
        os.makedirs(location)
    os.chdir(location)
    
    # Filenaming
    #----------------------------
    daystamp = "{timestamp:%Y%m%d}_"
    counter = "_im{counter:05d}"
    timestamp = "_{timestamp:%H%M%S}"
    filename = task + "_" + daystamp + rpi
    ftype = ".jpg" if rectype == "img" else ".h264"
    if single == "yes":
        filename = filename + timestamp + ftype
    else:
        if rectype == "img":
            filename = filename + counter + timestamp + ftype
            
    
    # Load custom settings
    #----------------------------
    zoom, brightness, awb, rotation = customsetup(rpi, autorotate)
    

    # Set up the camera with parameters
    #----------------------------
    print lineprint + "Starting up camera..."
    camera = picamera.PiCamera()
    camera.framerate = fps
    camera.resolution = resolution
    camera.zoom = zoom
    camera.rotation = rotation
    camera.exposure_compensation = compensation
    sleep(1)
    camera.exposure_mode = 'off'
    camera.awb_mode = 'off'
    camera.awb_gains = awb
    camera.shutter_speed = shutterspeed
    camera.sharpness = sharpness
    camera.iso = iso
    camera.contrast = contrast
    camera.saturation = saturation
    camera.brightness = brightness
    
    # Print recording settings
    print lineprint + "Settings = location: "+location+"; duration "+str(duration+delay)+          "sec; resolution: "+str(resolution)+"; shutterspeed: "+           str(shutterspeed/1000)+"ms; compensation: "+str(compensation)+"; fps: "+str(fps)+           "; sharpness: "+str(sharpness)+"; iso: "+str(iso)+"; contrast: "+str(contrast)+           "; brightness: "+str(brightness)+"; saturation: "+str(saturation)+"; and quality: "+str(quality)+"\n"
    
    
    # Start recording
    #----------------------------
    # Take image(s)
    if rectype == "img":
        if single == "yes":
            camera.capture(filename, format = "jpeg", quality = quality)
            print lineprint, "captured", filename
        else:
            bef = datetime.datetime.now()
            for i, img in enumerate(camera.capture_continuous(filename, format = "jpeg", quality = quality)):
                
                # Stop when required image number is reached
                if i == (imgnr-1):
                    break

                # Calculate delay and wait before taking next image
                delay = imgwait - (datetime.datetime.now() - bef).total_seconds()
                delay = 0 if delay < 0 else delay
                print lineprint, "captured" + img + ", sleeping " + str(round(delay,2)) + "s..",
                sleep(delay)
                bef = datetime.datetime.now()
                print bef
    
    # Take video(s)
    else:
        if single == "yes"
            filenamefull = filename
        else:
            print lineprint, "New session started"
            while True:
                session = "_" + raw_input("Session nr (e.g. S01): ")
                if len(session) != 3:
                    print "Session nr should be 3 characters long, try again"
                    continue
                else:
                    break
            while True:
                idnr = "_" + raw_input("Fish/Group ID (e.g. F101 or GR20): ")
                if len(idnr) != 4:
                    print "ID should be 4 characters long, try again"
                    continue
                else:
                    break
            filenamefull = filename + session + idnr + ftype
            print lineprint, "Recording " + filenamefull
            camera.start_recording(filename, quality = quality)
            camera.wait_recording(delay + duration)
            camera.stop_recording()
            
            # Continue until user breaks
            answer = raw_input("\nPress ENTER to start new session or 'e' to exit: ")
            if answer == 'e':
                break
            else:
                continue
    
    # Release camera when finished
    camera.close()

    
# Only execute record function when file is run
if __name__ == '__main__':
    record()

