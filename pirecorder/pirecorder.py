#! /usr/bin/env python
"""
Copyright (c) 2015 - 2020 Jolle Jolles <j.w.jolles@gmail.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at:

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from __future__ import print_function
from builtins import input

import os
import cv2
import sys
import yaml

import argparse
import numpy as np
from io import BytesIO
from ast import literal_eval
from datetime import datetime, timedelta
from socket import gethostname
from fractions import Fraction
from time import sleep, strftime
from localconfig import LocalConfig
from pythutils.sysutils import Logger, lineprint, homedir, checkfrac, isrpi
from pythutils.fileutils import name
from pythutils.mediautils import picamconv

from .stream import Stream
from .camconfig import Camconfig
from .schedule import Schedule
from .__version__ import __version__

class PiRecorder:

    """
    Sets up the rpi with a pirecorder folder with configuration and log files,
    and initiates a recorder instance for controlled image and video recording

    Parameters
    ----------
    configfile : str, default = "pirecorder.conf"
        The name of the configuration file to be used for recordings. If the
        file does not exist yet, automatically a new file with default
        configuration values will be created.

    Returns
    -------
    self : class
        PiRecorder class instance that can be used to set the configuration,
        start a video stream to calibrate and configure the camera, to set the
        shutterspeed and white balance automatically, to start recordings, and
        to schedule future recordings.
    """

    def __init__(self, configfile = "pirecorder.conf", logging = True):

        if not isrpi():
            lineprint("PiRecorder only works on a raspberry pi. Exiting..")
            return

        self.system = "auto"
        self.host = gethostname()
        self.home = homedir()
        self.setupdir = self.home + "pirecorder"
        self.logfolder = self.setupdir+"/logs/"
        if not os.path.exists(self.logfolder):
            os.makedirs(self.setupdir)
            os.makedirs(self.logfolder)
            lineprint("Setup folder created ("+self.setupdir+")..")
        if not os.path.exists(self.logfolder):
            lineprint("Setup folder exists but was not set up properly..")

        if logging:
            self.log = Logger(self.logfolder+"/pirecorder.log")
            self.log.start()
            print("")

        lineprint("pirecorder "+__version__+" started!")
        lineprint("="*47, False)

        self.brightfile = self.setupdir+"/cusbright.yml"
        self.configfilerel = configfile
        self.configfile = self.setupdir+"/"+configfile

        self.config = LocalConfig(self.configfile, compact_form = True)
        if not os.path.isfile(self.configfile):
            lineprint("Config file "+configfile+" not found, new file created..")
            for section in ["rec","cam","cus","img","vid"]:
                if section not in list(self.config):
                    self.config.add_section(section)
            self.settings(recdir="pirecorder/recordings",subdirs=False,
                          label="test",rectype="img",rotation=0,brighttune=0,
                          roi=None,gains=(1.0,2.5),brightness=45,contrast=10,
                          saturation=0,iso=200,sharpness=0,compensation=0,
                          shutterspeed=8000,imgdims=(2592,1944),cameratype=None,
                          viddims=(1640,1232),imgfps=1,vidfps=24,imgwait=5.0,
                          imgnr=12,imgtime=60,imgquality=50,vidduration=10,
                          viddelay=10,vidquality=11,automode=True,internal="")
            lineprint("Config settings stored..")

        else:
            lineprint("Config file "+configfile+" loaded..")
            lineprint("Recording " + self.config.rec.rectype + " in " +\
                          self.home + self.config.rec.recdir)

        self._imgparams()
        self._shuttertofps()
        if self.config.rec.rectype == "imgseq":
            if self.config.cam.shutterspeed/1000000.>=(self.config.img.imgwait/5):
                lineprint("imgwait is not enough for provided shutterspeed" + \
                          ", will be overwritten..")

        if self.config.rec.recdir == "NAS":
            if not os.path.ismount(self.config.rec.recdir):
                self.recdir = self.home
                lineprint("Recdir not mounted, storing in home directory..")
        self.recdir = self.home + self.config.rec.recdir
        if not os.path.exists(self.recdir):
            os.makedirs(self.recdir)

        os.chdir(self.recdir)


    def _setup_cam(self, auto = False, fps = None):

        """Sets up the raspberry pi camera based on the configuration"""

        import picamera
        import picamera.array

        self.cam = picamera.PiCamera()
        self.cam.rotation = self.config.cus.rotation
        self.cam.exposure_compensation = self.config.cam.compensation

        if self.config.rec.rectype in ["img","imgseq"]:
            self.cam.resolution = literal_eval(self.config.img.imgdims)
            self.cam.framerate = self.config.img.imgfps
        if self.config.rec.rectype in ["vid","vidseq"]:
            self.cam.resolution = picamconv(literal_eval(self.config.vid.viddims))
            self.cam.framerate = self.config.vid.vidfps
        if fps != None:
            self.cam.framerate = fps

        if self.config.cus.roi is None:
            self.cam.zoom = (0,0,1,1)
            self.resize = self.cam.resolution
        else:
            self.cam.zoom = literal_eval(self.config.cus.roi)
            w = int(self.cam.resolution[0]*self.cam.zoom[2])
            h = int(self.cam.resolution[1]*self.cam.zoom[3])
            if self.config.rec.rectype in ["vid","vidseq"]:
                self.resize = picamconv((w,h))
            else:
                self.resize = (w,h)

        self.longexpo = False if self.cam.framerate >= 6 else True

        self.cam.exposure_mode = "auto"
        self.cam.awb_mode = "auto"
        lineprint("Camera warming up..")
        if auto or self.config.cam.automode:
            self.cam.shutter_speed = 0
            sleep(2)
        elif self.cam.framerate >= 6:
            sleep(6) if self.cam.framerate > 1.6 else sleep(10)
        else:
            sleep(2)
        if not auto and self.config.cam.automode == False:
            self.cam.shutter_speed = self.config.cam.shutterspeed
            self.cam.exposure_mode = "off"
            self.cam.awb_mode = "off"
            self.cam.awb_gains = eval(self.config.cus.gains)
            sleep(0.1)

        brightness = self.config.cam.brightness + self.config.cus.brighttune
        self.cam.brightness = brightness
        self.cam.contrast = self.config.cam.contrast
        self.cam.saturation = self.config.cam.saturation
        self.cam.iso = self.config.cam.iso
        self.cam.sharpness = self.config.cam.sharpness

        self.rawCapture = picamera.array.PiRGBArray(self.cam,
                          size=self.cam.resolution)


    def _imgparams(self, mintime = 0.45):

        """
        Calculates minimum possible imgwait and imgnr based on imgtime. The
        minimum time between subsequent images is by default set to 0.45s, the
        time it takes to take an image with max resolution.
        """

        self.config.img.imgwait = max(mintime, self.config.img.imgwait)
        totimg = int(self.config.img.imgtime / self.config.img.imgwait)
        self.config.img.imgnr = min(self.config.img.imgnr, totimg)


    def _shuttertofps(self, minfps = 1, maxfps = 40):

        """Computes image fps based on shutterspeed within provided range"""

        fps = round(1./(self.config.cam.shutterspeed/1000000.),2)
        self.config.img.imgfps = min(max(fps, minfps), maxfps)


    def _namefile(self):

        """
        Provides a filename for the media recorded. Filenames include label,
        date, rpi name, and time. Images part of image sequence additionally
        contain a sequence number. e.g. test_180708_pi12_S01_100410
        """

        imgtypes = ["img","imgseq"]
        self.filetype = ".jpg" if self.config.rec.rectype in imgtypes else ".h264"

        if self.config.rec.rectype == "imgseq":
            date = strftime("%y%m%d")
            counter = "im{counter:05d}" if self.config.img.imgnr>999 else "im{counter:03d}"
            time = "{timestamp:%H%M%S%f}"
            self.filename = "_".join([self.config.rec.label,date,self.host,counter,time])
            self.filename = self.filename+self.filetype
        else:
            date = strftime("%y%m%d")
            self.filename = "_".join([self.config.rec.label, date, self.host])+"_"

        if self.config.rec.subdirs:
            subdir = name("_".join([self.config.rec.label,date,self.host]))
            os.makedirs(subdir, exist_ok=True)
            self.filename = subdir+"/"+self.filename


    def autoconfig(self):

        """
        Sets the shutterspeed and white balance automatically using the
        framerate provided in the configuration file
        """

        self._setup_cam(auto=True)
        with self.rawCapture as stream:
            for a in range(5):
                self.cam.capture(stream, format="bgr", use_video_port=True)
                image = stream.array
                stream.seek(0)
                stream.truncate()

            self.config.cam.shutterspeed = self.cam.exposure_speed
            self.config.cus.gains = tuple([round(float(i),2) for i in self.cam.awb_gains])
            self.config.save()
            lineprint("Shutterspeed automaticall set to",self.cam.exposure_speed)
            lineprint("White balance gains automatically set to",self.config.cus.gains)


    def settings(self, **kwargs):

        """
        Configure the camera and recording settings

        Parameters
        ---------------
        recdir : str, default = "pirecorder/recordings"
            The directory where media will be stored. Default is "recordings".
            If different, a folder with name corresponding to location will be
            created inside the home directory. If no name is provided (""), the
            files are stored in the home directory. If "NAS" is provided it will
            additionally check if the folder links to a mounted drive.
        label : str, default = "test"
            Label that will be associated with the specific recording and stored
            in the filenames.
        rectype : ["img", "imgseq", "vid", "vidseq"], default = "img"
            Recording type, either a single image or video or a sequence of
            images or videos.
        automode : bool, default = True
            If the shutterspeed and white balance should be set automatically
            and dynamically for each recording.
        cameratype : str, default = None
            The raspberry cameratype used. Can be either None, "v1", "v2", or
            "hq" to indicate the different models and will help set the maximum
            recording resolution.
        rotation : int, default = 0
            Custom rotation specific to the Raspberry Pi, should be either 0 or
            180.
        brighttune : int, default = 0
            A rpi-specific brightness compensation factor to standardize light
            levels across multiple rpi"s, an integer between -10 and 10.
        roi : tuple, default = None
            Region of interest to be used for recording. Consists of coordinates
            of top left and bottom right coordinate of a rectangular area
            encompassing the region of interest. Can be set with the set_roi()
            method.
        gains : tuple, default = (1.0, 2.5)
            Sets the blue and red gains to acquire the desired white balance.
            Expects a tuple of floating values (e.g. "(1.5, 1.85)"). Can be
            automatically set with the autoconfig() function and interactively
            with the camconfig() function using a live video stream.
        brightness : int, default = 45
            Sets the brightness level of the camera. Expects an integer value
            between 0 and 100. Higher values result in brighter images.
        contrast : int, default = 20
            Sets the contrast for the recording. Expects an integer value
            between 0 and 100. Higher values result in images with higher
            contrast.
        saturation : int, default 0
            Sets the saturation level for the recording. Expects an integer
            value between -100 and 100.
        iso : int, default = 200
            Sets the camera ISO value. Should be one of the following values:
            [100, 200, 320, 400, 500, 640, 800]. Higher values result in
            brighter images but with higher gain.
        sharpness : int, default = 50
            Sets the sharpness of the camera. Expects an integer value between
            -100 and 100. Higher values result in sharper images.
        compensation : int, default = 0
            Adjusts the camera’s exposure compensation level before recording.
            Expects a value between -25 and 25, with each increment representing
            1/6th of a stop and thereby a brighter image.
        shutterspeed : int, detault = 10000
            Sets the shutter speed of the camera in microseconds, i.e. a value
            of 10000 would indicate a shutterspeed of 1/100th of a second. A
            longer shutterspeed will result in a brighter image but more motion
            blur. Important to consider is that the framerate of the camera will
            be adjusted based on the shutterspeed. At low shutterspeeds (i.e.
            above ~ 0.2s) the required waiting time between images increases
            considerably due to the raspberry pi hardware. To control for this,
            automatically a standard `imgwait` time should be chosen that is at
            least 6x the shutterspeed. For example, for a shutterspeed of 300000
            imgwait should be > 1.8s.
        imgdims : tuple, default = (2592, 1944)
            The resolution of the images to be taken in pixels. The default is
            the max resolution for the v1.5 model, the v2 model has a max
            resolution of 3280 x 2464 pixels, and the hq camera 4056 x 3040
            pixels.
        viddims : tuple, default = (1640, 1232)
            The resolution of the videos to be taken in pixels. The default is
            the max resolution that does not return an error for this mode.
        imgfps : int, default = 1
            The framerate for recording images. Will be set automatically based
            on the imgwait setting so should not be set by user.
        vidfps : int, default = 24
            The framerate for recording video.
        imgwait : float, default = 5.0
        	The delay between subsequent images in seconds. When a delay is
            provided that is less than ~x5 the shutterspeed, the camera
            processing time will take more time than the provided imgwait
            parameter and so images are taken immideately one after the other.
            To take a sequence of images at the exact right delay interval the
            imgwait parameter should be at least 5x the shutterspeed (e.g.
            shutterspeed of 400ms needs imgwait of 2s).
        imgnr : int, default = 12
            The number of images that should be taken. When this number is
            reached, the recorder will automatically terminate.
        imgtime : integer, default = 60
            The time in seconds during which images should be taken. The minimum
            of a) imgnr and b) nr of images based on imgwait and imgtime will be
            used.
        imgquality : int, default = 50
            Specifies the quality that the jpeg encoder should attempt to
            maintain. Use values between 1 and 100, where higher values are
            higher quality.
        vidduration : int, default = 10
            Duration of video recording in seconds.
        viddelay : int, default = 0
            Extra recording time in seconds that will be added to vidduration.
            Its use is to add a standard amount of time to the video that can be
            easily cropped or skipped, such as for tracking, but still provides
            useful information, such as behaviour during acclimation.
        vidquality : int, default = 11
            Specifies the quality that the h264 encoder should attempt to
            maintain. Use values between 10 and 40, where 10 is extremely high
            quality, and 40 is extremely low.
        """

        if "recdir" in kwargs:
            self.config.rec.recdir = kwargs["recdir"]
        if "subdirs" in kwargs:
            self.config.rec.subdirs = kwargs["subdirs"]
        if "label" in kwargs:
            self.config.rec.label = kwargs["label"]
        if "rectype" in kwargs:
            self.config.rec.rectype = kwargs["rectype"]
        if "cameratype" in kwargs:
            self.config.rec.cameratype = kwargs["cameratype"]
            if self.config.rec.cameratype == "v2":
                self.config.img.imgdims = (3264,2464)
            if self.config.rec.cameratype == "hq":
                self.config.img.imgdims = (4056,3040)

        if "rotation" in kwargs:
            self.config.cus.rotation = kwargs["rotation"]
        if "brighttune" in kwargs:
            self.config.cus.brighttune = kwargs["brighttune"]
        if "roi" in kwargs:
            self.config.cus.roi = kwargs["roi"]
        if "gains" in kwargs:
            self.config.cus.gains = kwargs["gains"]

        if "automode" in kwargs:
            self.config.cam.automode = kwargs["automode"]
        if "brightness" in kwargs:
            self.config.cam.brightness = kwargs["brightness"]
        if "contrast" in kwargs:
            self.config.cam.contrast = kwargs["contrast"]
        if "saturation" in kwargs:
            self.config.cam.saturation = kwargs["saturation"]
        if "iso" in kwargs:
            self.config.cam.iso = kwargs["iso"]
        if "sharpness" in kwargs:
            self.config.cam.sharpness = kwargs["sharpness"]
        if "compensation" in kwargs:
            self.config.cam.compensation = kwargs["compensation"]
        if "shutterspeed" in kwargs:
            self.config.cam.shutterspeed = kwargs["shutterspeed"]

        if "imgdims" in kwargs:
            self.config.img.imgdims = kwargs["imgdims"]
        if "viddims" in kwargs:
            self.config.vid.viddims = kwargs["viddims"]
        if "imgfps" in kwargs:
            self.config.img.imgfps = kwargs["imgfps"]
        if "vidfps" in kwargs:
            self.config.vid.vidfps = kwargs["vidfps"]

        if "imgwait" in kwargs:
            self.config.img.imgwait = kwargs["imgwait"]
        if "imgnr" in kwargs:
            self.config.img.imgnr = kwargs["imgnr"]
        if "imgtime" in kwargs:
            self.config.img.imgtime = kwargs["imgtime"]
        if "imgquality" in kwargs:
            self.config.img.imgquality = kwargs["imgquality"]

        if "vidduration" in kwargs:
            self.config.vid.vidduration = kwargs["vidduration"]
        if "viddelay" in kwargs:
            self.config.vid.viddelay = kwargs["viddelay"]
        if "vidquality" in kwargs:
            self.config.vid.vidquality = kwargs["vidquality"]

        brightchange = False
        if os.path.exists(self.brightfile):
            with open(self.brightfile) as f:
                brighttune = yaml.load(f, Loader=yaml.FullLoader)
                if brighttune != self.config.cus.brighttune:
                    self.config.cus.brighttune = brighttune
                    brightchange = True

        if len(kwargs) > 0 or brightchange:

            self._imgparams()
            self._shuttertofps()
            if self.config.rec.rectype == "imgseq":
                if self.config.cam.shutterspeed/1000000. >= (self.config.img.imgwait/5):
                    lineprint("imgwait is not enough for provided shutterspeed" + \
                              ", will be overwritten..")
            self.config.save()

            if "internal" not in kwargs:
                lineprint("Config settings stored and loaded..")


    def stream(self, fps = None):

        """Shows an interactive video stream"""

        lineprint("Opening stream for cam positioning and roi extraction..")
        vidstream = Stream(internal=True, rotation=self.config.cus.rotation,
                       cameratype=self.config.rec.cameratype)
        if vidstream.roi:
            self.settings(roi=vidstream.roi, internal="")
            lineprint("Roi stored..")
        else:
            lineprint("No roi selected..")

    def camconfig(self, fps=None, vidsize=0.4):

        lineprint("Opening stream for interactive configuration..")
        fps = max(self.config.vid.vidfps,1) if fps==None else int(fps)
        self._setup_cam(fps=fps)
        configout = Camconfig(self.cam, auto=self.config.cam.automode,
                              vidsize=vidsize)
        if len(configout)>0:
            self.settings(**configout)


    def schedule(self, jobname = None, timeplan = None, enable = True,
                 showjobs = False, delete = None, test = False):

        """
        Schedule future recordings

        Parameters
        ----------
        jobname : str, default = None
            Name for the scheduled recorder task to create, modify or remove.
        timeplan : string, default = None
            Code string representing the time planning for the recorder to run
            with current configuration set. Build on CRON, the time plan should
            consist of the following parts:
            * * * * *
            - - - - -
            | | | | |
            | | | | +----- day of week (0 - 7) (sunday = 0 or 7)
            | | | +---------- month (1 - 12)
            | | +--------------- day of month (1 - 31)
            | +-------------------- hour (0 - 23)
            +------------------------- min (0 - 59)
            Each of the parts supports wildcards (*), ranges (2-5), and lists
            (2,5,6,11). For example, if you want to schedule a recording at
            22:00, every workday of the week, enter the code '0 22 * * 1-5' If
            uncertain, crontab.guru is a great website for checking your CRON
            code. Note that the minimum time between subsequent scheduled
            recordings is 1 minute. Smaller intervals between recordings is
            possible for images with the imgseq command with the Record method.
        enable : bool, default = None
            If the scheduled job should be enabled or not.
        showjobs : bool, default = False
            If the differently timed tasks should be shown or not.
        delete : [None, "job", "all"], default = None
            If a specific job ('job'), all jobs ('all') or no jobs (None)
            should be cleared from the scheduler.
        test : bool; default = False
            Determine if the timeplan is valid and how often it will run the
            record command.
        configfile : str, default = "pirecorder.conf"
            The name of the configuration file to be used for the scheduled
            recordings. Make sure the file exists, otherwise the default
            configuration settings will be used.

        Note: Make sure Recorder configuration timing settings are within the
        timespan between subsequent scheduled recordings based on the provided
        timeplan. For example, a video duration of 20 min and a scheduled
        recording every 15 min between 13:00-16:00 (*/15 13-16 * * *) will fail.
        This will be checked automatically.
        """

        S = Schedule(jobname, timeplan, enable, showjobs, delete, test,
                     logfolder = self.logfolder, internal=True,
                     configfile = self.configfilerel)


    def record(self):

        """
        Starts a recording as configured and returns either one or multiple
        .h264 or .jpg files that are named automatically according to the label,
        the host name, date, time and potentially session number or count nr.

        Example output files:
        rectype = "img" : test_180312_pi13_101300.jpg
        rectype = "vid" : test_180312_pi13_102352.h264
        rectype = "imgseq" : test_180312_pi13_img00231_101750.jpg
        rectype = "vidseq" : test_180312_pi13_101810_S01.h264
        """

        self._setup_cam()
        self._namefile()

        if self.config.rec.rectype == "img":

            self.filename = self.filename + strftime("%H%M%S") + self.filetype
            self.cam.capture(self.filename, format="jpeg", resize = self.resize,
                             quality = self.config.img.imgquality)
            lineprint("Captured "+self.filename)

        elif self.config.rec.rectype == "imgseq":

            #while True:
            #    timept2 = datetime.now()
            #    if timept2.second > timept1.second and timept2.microsecond >= 0:
            #        break
            #! Start on the next full minute
            nextmin = (datetime.now()+timedelta(minutes=1)).replace(second=0, microsecond=0)
            delay = (nextmin - datetime.now()).total_seconds()
            minute = str((datetime.now()+timedelta(minutes=1)).replace(second=0, microsecond=0).minute)
            lineprint("Sleeping until start of min "+minute+"..")
            sleep(delay)
            timept1 = datetime.now()
            for i, img in enumerate(self.cam.capture_continuous(self.filename,
                                    format="jpeg", resize = self.resize,
                                    quality = self.config.img.imgquality)):
                if i < self.config.img.imgnr-1:
                    #!temp blocked for experiment
                    #timepassed = (datetime.now() - timept2).total_seconds()
                    #delay = max(0, self.config.img.imgwait - timepassed)

                    #timeimgtaken = int(img.split("_")[-1:][0][6:-4])/1000000
                    #delay = self.config.img.imgwait-timeimgtaken
                    nextimg = (timept1+timedelta(seconds=int(self.config.img.imgwait*i+self.config.img.imgwait))).replace(microsecond=0)
                    delay = (nextimg - datetime.now()).total_seconds()
                    lineprint("Captured "+img+", sleeping "+str(round(delay,4))+"s..")
                    sleep(delay)
                    #timept2 = datetime.now()
                else:
                    lineprint("Captured "+img)
                    break

        elif self.config.rec.rectype in ["vid","vidseq"]:

            # Temporary fix for flicker at start of (first) video
            self.cam.start_recording(BytesIO(), format = "h264",
                                     resize = self.resize, level = "4.2")
            self.cam.wait_recording(2)
            self.cam.stop_recording()

            for session in ["_S%02d" % i for i in range(1,999)]:
                session = "" if self.config.rec.rectype == "vid" else session
                filename = self.filename+strftime("%H%M%S")+session+self.filetype
                self.cam.start_recording(filename, resize = self.resize,
                                         quality = self.config.vid.vidquality,
                                         level = "4.2")
                lineprint("Start recording "+filename)
                self.cam.wait_recording(self.config.vid.vidduration+self.config.vid.viddelay)
                self.cam.stop_recording()
                lineprint("Finished recording "+filename)
                if self.config.rec.rectype == "vid":
                    break
                else:
                    msg = "\nPress Enter for new session, or e and Enter to exit: "
                    if input(msg) == "e":
                        break
        self.cam.close()


def rec():

    """To run pirecorder from the command line"""

    parser = argparse.ArgumentParser(prog="record",
    description="Runs PiRecorder record function")
    parser.add_argument("-c",
                        "--configfile",
                        default="pirecorder.conf",
                        action="store",
                        help="pirecorder configuration file")
    args = parser.parse_args()
    if not isrpi():
        lineprint("PiRecorder only works on a raspberry pi. Exiting..")
        return
    rec = PiRecorder(args.configfile)
    rec.settings(internal = True)
    rec.record()
