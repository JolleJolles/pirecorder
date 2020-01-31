#! /usr/bin/env python
"""
Copyright (c) 2015 - 2019 Jolle Jolles <j.w.jolles@gmail.com>

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
import sys
import yaml

import argparse
import numpy as np
from io import BytesIO
from ast import literal_eval
from datetime import datetime
from socket import gethostname
from fractions import Fraction
from time import sleep, strftime
from localconfig import LocalConfig
from pythutils.sysutils import Logger, lineprint, homedir, checkfrac
from pythutils.fileutils import name
from pythutils.mediautils import picamconv

from .schedule import Schedule
from .setgains import setgains
from .calibrate import Calibrate
from .__version__ import __version__

class PiRecorder:

    """
    Recorder class for setting up the rpi for controlled image & video recording

    Parameters
    ----------
    recdir : str, default = "pirecorder/recordings"
        The directory where media will be stored. Default is "recordings". If
        different, a folder with name corresponding to location will be created
        inside the home directory. If no name is provided (""), the files are
        stored in the home directory. If "NAS" is provided it will additionally
        check if the folder links to a mounted drive.
    label : str, default = "test"
        Label for associating with the recording and stored in the filenames.
    rectype : ["img", "imgseq", "vid", "vidseq"], default = "img"
        Recording type, either a single image or video or a sequence of images
        or videos.

    Config settings
    ---------------
    rotation : int, default = 0
        Custom rotation specific to the Raspberry Pi, should be either 0 or 180.
    brighttune : int, default = 0
        A rpi-specific brightness compensation factor to standardize light levels
        across multiple rpi's, an integer between -10 and 10.
    roi : tuple, default = None
        Region of interest to be used for recording. Consists of coordinates of
        topleft and bottom right coordinate of a rectangular area encompassing
        the region of interest. Can be set with the set_roi() method.
    gains : tuple, default = (1.0, 2.5)
        Custom gains specific to the Raspberry PI to set the colorspace. The
        gains for an ideal white balance can be automatically set with the
        get_gains() method.

    brightness : int, default = 45
        The brightness level of the camera, an integer value between 0 and 100.
    contrast : int, default = 20
        The image contrast, an integer value between 0 and 100.
    saturation : int, default -100
        The color saturation level of the image, an integer value between -100
        and 100.
    iso : int, default = 200
        The camera ISO value, an integer value in sequence [200,400,800,1600].
        Higher values are more light sensitive but have higher gain.
    sharpness : int, default = 50
        The sharpness of the camera, an integer value between -100 and 100.
    compensation : int, default = 0
        Camera lighting compensation. Ranges between 0 and 20. Compensation
        artificially adds extra light to the image.
    shutterspeed : int, detault = 10000
        Shutter speed of the camera in microseconds, i.e. the default of 10000
        is equivalent to 1/100th of a second. A longer shutterspeed will result
        in a brighter image but more motion blur. Important: the framerate of
        the camera will be adjusted based on the shutterspeed. At shutter-
        speeds above ~ 0.2s this results in increasingly longer waiting times
        between images so a standard imgwait time should be chosen that is 6+
        times more than the shutterspeed. For example, for a shutterspeed of
        300000 imgwait should be > 1.8s.
    imgdims : tuple, default = (2592, 1944)
        The resolution of the images to be taken in pixels. The default is the
        max resolution that does not return an error for this mode for the v1.5
        rpi camera. Note that rpi camera v2 has a much higher maximum resolution
        of 3280 x 2464.
    viddims : tuple, default = (1640,1232)
        The resolution of the videos to be taken in pixels. The default is the
        max resolution that does not return an error for this mode.
    imgfps : int, default = 1
        The framerate for recording images. Will be set automatically based on
        the imgwait setting so should not be set by user.
    vidfps : int, default = 24
        The framerate for recording video.
    imgwait : float, default = 5.0
    	The delay between subsequent images in seconds. When a delay is provided
      	that is less than ~x5 the shutterspeed, the camera processing time will
        take more time than the provided imgwait parameter and so images are
        taken immideately one after the other. To take a sequence of images at
        the exact right delay interval the imgwait parameter should be at least
        5x the shutterspeed (e.g. shutterspeed of 400ms needs imgwait of 2s).
    imgnr : int, default = 12
        The number of images that should be taken. When this number is reached,
        the recorder will automatically terminate.
    imgtime : integer, default = 60
        The time in seconds during which images should be taken. The minimum of
        a) imgnr and b) nr of images based on imgwait and imgtime will be
        selected.
    imgquality : int, default = 50
        Specifies the quality that the jpeg encoder should attempt to maintain.
        Use values between 1 and 100, where higher values are higher quality.
    vidduration : int, default = 10
        Duration of video recording in seconds.
    viddelay : int, default = 0
        Extra recording time in seconds that will be added to vidduration. Its
        use is for filming acclimatisation time that can then easily be cropped
        for tracking.
    vidquality : int, default = 11
        Specifies the quality that the h264 encoder should attempt to maintain.
        Use values between 10 and 40, where 10 is extremely high quality, and
        40 is extremely low.

    Output
    -------
    Either one or multiple .h264 or .jpg files. All files are automatically
    named according to the label, the host name, date, time and potentially
    session number or count nr, e.g.
    - single image: 'pilot_180312_PI13_101300.jpg
    - multiple images: 'pilot_180312_PI13_img00231_101300.jpg
    - video: 'pilot_180312_PI13_S01_101300.h264

    Returns
    -------
    self : class
        Recorder class instance
    """

    def __init__(self, configfile = "pirecorder.conf"):

        lineprint("pirecorder "+__version__+" started!")
        lineprint("="*47, False)

        self.system = "auto"
        self.host = gethostname()
        self.home = homedir()
        self.setupdir = self.home + "pirecorder"
        self.logfolder = self.setupdir+"/logs"
        if not os.path.exists(self.logfolder):
            os.makedirs(self.setupdir)
            os.makedirs(self.logfolder)
            lineprint("Setup folder created ("+self.setupdir+")..")
        if not os.path.exists(self.logfolder):
            lineprint("Setup folder already exists but was not set up properly..")

        sys.stdout = Logger(self.logfolder+"/pirecorder.log")

        self.brightfile = self.setupdir+"/cusbright.yml"
        self.configfile = self.setupdir+"/"+configfile

        self.config = LocalConfig(self.configfile, compact_form = True)
        if not os.path.isfile(self.configfile):
            lineprint("Config file not found, new file created..")
            for section in ["rec","cam","cus", "img","vid"]:
                if section not in list(self.config):
                    self.config.add_section(section)
            self.set_config(recdir="pirecorder/recordings", subdirs=False, label="test",
                            rectype="vid", rotation=0, brighttune=0, roi=None,
                            gains=(1.0,2.5), brightness=45, contrast=10,
                            saturation=-100, iso=200, sharpness=0, compensation=0,
                            shutterspeed=8000, imgdims=(2592,1944),
                            viddims=(1640,1232), imgfps=1, vidfps=24, imgwait=5.0,
                            imgnr=12, imgtime=60, imgquality=50, vidduration=10,
                            viddelay=10, vidquality=11, internal="")
            lineprint("Config settings stored..")

        else:
            lineprint("Config file " + configfile + " loaded..")
            lineprint("Recording " + self.config.rec.rectype + " in " +\
                          self.home + self.config.rec.recdir)

        self._imgparams()
        self._shuttertofps()
        if self.config.rec.rectype == "imgseq":
            if self.config.cam.shutterspeed/1000000. <= (self.config.img.imgwait/5):
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


    def _setup_cam(self):

        """Sets up the raspberry pi camera based on configuration"""

        #load picamera module in-function so pirecorder is installable on all OS
        import picamera
        import picamera.array

        self.cam = picamera.PiCamera()
        self.cam.rotation = self.config.cus.rotation
        self.cam.exposure_compensation = self.config.cam.compensation

        if self.config.rec.rectype in ["img","imgseq"]:
            self.cam.resolution = literal_eval(self.config.img.imgdims)
            self.cam.framerate = self.config.img.imgfps
        if self.config.rec.rectype in ["vid","vidseq"]:
            self.cam.resolution = literal_eval(self.config.vid.viddims)
            self.cam.framerate = self.config.vid.vidfps
        self.rawCapture = picamera.array.PiRGBArray(self.cam, size = self.cam.resolution)

        if self.config.cus.roi is None:
            self.cam.zoom = (0,0,1,1)
            self.resize = self.cam.resolution
        else:
            self.cam.zoom = literal_eval(self.config.cus.roi)
            w = int(self.cam.resolution[0]*self.cam.zoom[2])
            h = int(self.cam.resolution[1]*self.cam.zoom[3])
            self.resize = picamconv((w,h))

        self.longexpo = False if self.cam.framerate >= 6 else True
        if self.longexpo:
            lineprint("Long exposure, warming up camera..")
            sleep(6) if self.cam.framerate > 1.6 else sleep(10)
        else:
            lineprint("Camera warming up..")
            sleep(2)

        self.cam.shutter_speed = self.config.cam.shutterspeed
        self.cam.exposure_mode = "off"
        self.cam.awb_mode = "off"
        self.cam.awb_gains = checkfrac(self.config.cus.gains)
        brightness = self.config.cam.brightness + self.config.cus.brighttune
        self.cam.brightness = brightness

        self.cam.contrast = self.config.cam.contrast
        self.cam.saturation = self.config.cam.saturation
        self.cam.iso = self.config.cam.iso
        self.cam.sharpness = self.config.cam.sharpness


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

        fps = 1./(self.config.cam.shutterspeed/1000000.)
        fps = max(fps, minfps)
        self.config.img.imgfps = min(fps, maxfps)


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
            time = "{timestamp:%H%M%S}"
            self.filename = "_".join([self.config.rec.label,date,self.host,counter,time])
            self.filename = self.filename+self.filetype
        else:
            date = strftime("%y%m%d")
            self.filename = "_".join([self.config.rec.label, date, self.host])+"_"

        if self.config.rec.subdirs:
            subdir = name("_".join([self.config.rec.label,date,self.host]))
            os.makedirs(subdir, exist_ok=True)
            self.filename = subdir+"/"+self.filename


    def set_config(self, **kwargs):

        """ Dynamically sets the configuration file """

        if "recdir" in kwargs:
            self.config.rec.recdir = kwargs["recdir"]
        if "subdirs" in kwargs:
            self.config.rec.subdirs = kwargs["subdirs"]
        if "label" in kwargs:
            self.config.rec.label = kwargs["label"]
        if "rectype" in kwargs:
            self.config.rec.rectype = kwargs["rectype"]

        if "rotation" in kwargs:
            self.config.cus.rotation = kwargs["rotation"]
        if "brighttune" in kwargs:
            self.config.cus.brighttune = kwargs["brighttune"]
        if "roi" in kwargs:
            self.config.cus.roi = kwargs["roi"]
        if "gains" in kwargs:
            self.config.cus.gains = kwargs["gains"]

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
            self.config.save()

            if "internal" not in kwargs:
                lineprint("Config settings stored and loaded..")


    def set_roi(self):

        """
        Dynamically draw a region of interest

        Explanation
        ===========
        This function will open a video stream of the raspberry pi camera. Enter
        'd' to start drawing the region of interest on an image taken from the
        video stream. When happy with the region selected, press 's' to store
        the coordinates, or 'esc' key to exit drawing on the image. To exist the
        video stream enter 'esc' key again.
        """

        C = Calibrate(internal=True, rotation=self.config.cus.rotation)
        if C.roi:
            self.set_config(roi=C.roi, internal="")
            lineprint("Roi stored..")
        else:
            lineprint("No roi selected..")


    def set_gains(self, auto = True):

        """Find the best gains for the raspberry pi camera"""

        if self.config.cus.roi == None:
            zoom = (0,0,1,1)
        else:
            zoom = literal_eval(self.config.cus.roi)
        (rg, bg) = setgains(startgains = checkfrac(self.config.cus.gains),
                            zoom = zoom, auto = auto)
        self.set_config(gains="(%5.2f, %5.2f)" % (rg, bg), internal="")
        lineprint("Gains: " + "(R:%5.2f, B:%5.2f)" % (rg, bg) + " stored..")


    def schedule(self, jobname = None, timeplan = None, enable = True,
                showjobs = False, clear = None, test = False):

        S = Schedule(jobname, timeplan, enable, showjobs, clear, test,
                     logfolder = self.logfolder, internal=True)


    def record(self):

        """Runs the Recorder instance"""

        self._setup_cam()
        self._namefile()

        if self.config.rec.rectype == "img":

            self.filename = self.filename + strftime("%H%M%S") + self.filetype
            self.cam.capture(self.filename, format="jpeg", resize = self.resize,
                             quality = self.config.img.imgquality)
            lineprint("Captured "+self.filename)

        elif self.config.rec.rectype == "imgseq":

            timepoint = datetime.now()
            for i, img in enumerate(self.cam.capture_continuous(self.filename,
                                    format="jpeg", resize = self.resize,
                                    quality = self.config.img.imgquality)):
                if i < self.config.img.imgnr-1:
                    timepassed = (datetime.now() - timepoint).total_seconds()
                    delay = max(0, self.config.img.imgwait - timepassed)
                    lineprint("Captured "+img+", sleeping "+str(round(delay,2))+"s..")
                    sleep(delay)
                    timepoint = datetime.now()
                else:
                    lineprint("Captured "+img)
                    break

        elif self.config.rec.rectype in ["vid","vidseq"]:

            # Temporary fix for flicker at start of (first) video..
            self.cam.start_recording(BytesIO(), format="h264", resize = self.resize)
            self.cam.wait_recording(2)
            self.cam.stop_recording()

            for session in ["_S%02d" % i for i in range(1,999)]:
                session = "" if self.config.rec.rectype == "vid" else session
                filename = self.filename+strftime("%H%M%S")+session+self.filetype
                self.cam.start_recording(filename, resize = self.resize,
                                         quality = self.config.vid.vidquality)
                lineprint("Start recording "+filename)
                self.cam.wait_recording(self.config.vid.vidduration + self.config.vid.viddelay)
                self.cam.stop_recording()
                lineprint("Finished recording "+filename)
                if self.config.rec.rectype == "vid":
                    break
                else:
                    if input("\nAny key for new session, e to exit: ") == "e":
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
    recorder = PiRecorder(args.configfile)
    recorder.set_config(internal=True)
    recorder.record()
