#! /usr/bin/env python
"""
Copyright (c) 2015 - 2025 Jolle Jolles <j.w.jolles@gmail.com>

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
import io
import cv2
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
from pythutils.sysutils import Logger, lineprint, homedir, checkfrac, isrpi
from pythutils.fileutils import name
from pythutils.mediautils import picamconv

from .stream import Stream
from .camconfig import Camconfig
from .schedule import Schedule
from .__version__ import __version__

class VidOutput(object):

    """
    Video output object for continuous monitoring of file size while recording
    """

    def __init__(self, filename):
        self.vid = io.open(filename, 'wb')
        self.size = 0

    def write(self, s):
        self.vid.write(s)
        self.size += len(s)

    def flush(self):
        self.vid.flush()


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
        self.logfolder = self.setupdir + "/logs/"
        if not os.path.exists(self.logfolder):
            os.makedirs(self.setupdir)
            os.makedirs(self.logfolder)
            lineprint("Setup folder created ("+self.setupdir+")..")
        if not os.path.exists(self.logfolder):
            lineprint("Setup folder exists but was not set up properly..")

        if logging:
            self.log = Logger(self.logfolder + "/pirecorder.log")
            self.log.start()
            print("")

        lineprint("pirecorder " + __version__ + " started!", date = True)
        lineprint("="*47, False)

        self.brightfile = self.setupdir+"/cusbright.yml"
        self.configfilerel = configfile
        self.configfile = self.setupdir + "/" + configfile
        self.nametypes = ("label","date","time","datetime","counter","rpi","")

        self.config = LocalConfig(self.configfile, compact_form = True)
        overwrite = True
        if not os.path.isfile(self.configfile):
            lineprint("Config file " + configfile + " not found, new file created..")
            for section in ["rec","cam","cus","img","vid"]:
                if section not in list(self.config):
                    self.config.add_section(section)
            set = True
        elif str(self.config).count("=")<36:
            overwrite = False
            set = True
        else:
            set = False
            lineprint("Config file " + configfile + " loaded..")
            lineprint("Recording " + self.config.rec.rectype + " in " +\
                          self.home + self.config.rec.recdir)
        if set:
            self.settings(overwrite=overwrite, internal="",
                          recdir="pirecorder/recordings", subdirs=False, label="test", rectype="img", maxres="v2",
                          automode=True, brightness=45, contrast=10, saturation=0, iso=200, sharpness=0, compensation=0,shutterspeed=8000,
                          rotation=0, brighttune=0, roi=None, gains=(1.0,2.5), annotatesize=0, nameparam1="label", nameparam2="date",
                          nameparam3="rpi", nameparam4="counter", nameparam5="time", imgdims=(2592,1944), 
                          imgfps=1, imgwait=5.0, imgnr=12, imgtime=60, imgquality=50, viddims=(1640,1232),
                          vidfps=24, vidduration=10, viddelay=10, vidquality=11, maxviddur=3600, maxvidsize=0)
            lineprint("Config settings stored and updated..")


        self._imgparams()
        self._shuttertofps()
        if self.config.rec.rectype == "imgseq":
            if self.config.cam.shutterspeed / 1000000. >= (self.config.img.imgwait / 5):
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

        if self.config.cus.annotatesize > 5:
            self.cam.annotate_background = picamera.Color('black')
            self.cam.annotate_text_size = self.config.cus.annotatesize

        if self.config.rec.rectype in ["img","imgseq"]:
            self.cam.resolution = literal_eval(self.config.img.imgdims)
            self.cam.framerate = self.config.img.imgfps
        if self.config.rec.rectype in ["vid","vidseq"]:
            self.cam.resolution = picamconv(literal_eval(self.config.vid.viddims))
            self.cam.framerate = self.config.vid.vidfps
        
        if fps is not None:
            self.cam.framerate = fps

        # Set the region of interest, if provided
        if self.config.cus.roi is None:
            self.cam.zoom = (0, 0, 1, 1)
            self.resize = self.cam.resolution
        else:
            self.cam.zoom = literal_eval(self.config.cus.roi)
            w = int(self.cam.resolution[0] * self.cam.zoom[2])
            h = int(self.cam.resolution[1] * self.cam.zoom[3])
            self.resize = picamconv((w, h)) if self.config.rec.rectype in ["vid", "vidseq"] else (w, h)

        # Determine if long exposure is needed
        self.longexpo = False if self.cam.framerate >= 6 else True

        # Start in auto mode to allow the camera to adjust exposure and AWB
        self.cam.exposure_mode = "auto"
        self.cam.awb_mode = "auto"
        lineprint("Camera warming up..")

        # Wait for the camera to adjust—time can be tuned depending on your framerate
        if auto or self.config.cam.automode:
            #self.cam.shutter_speed = 0
            sleep(2)
        elif self.cam.framerate >= 6:
            sleep(6) if self.cam.framerate > 1.6 else sleep(10)
        else:
            sleep(2)

        # If you’re using fixed settings (i.e. not in auto mode), lock the camera settings
        if not (auto or self.config.cam.automode):
            # Capture the auto-adjusted settings from the warm-up period
            current_exposure = self.cam.exposure_speed
            current_awb_gains = self.cam.awb_gains

            # Lock exposure and white balance by disabling auto modes
            self.cam.exposure_mode = "off"
            self.cam.awb_mode = "off"
            # Use your preset shutter speed if provided; otherwise use the current exposure
            self.cam.shutter_speed = self.config.cam.shutterspeed if hasattr(self.config.cam, 'shutterspeed') else current_exposure
            # Apply preset gains if available; otherwise, keep auto-determined gains
            self.cam.awb_gains = eval(self.config.cus.gains) if self.config.cus.gains else current_awb_gains
            sleep(0.1)

        # Apply remaining fixed settings
        brightness = self.config.cam.brightness + self.config.cus.brighttune
        self.cam.brightness = brightness
        self.cam.contrast = self.config.cam.contrast
        self.cam.saturation = self.config.cam.saturation
        self.cam.iso = self.config.cam.iso
        self.cam.sharpness = self.config.cam.sharpness

        self.rawCapture = picamera.array.PiRGBArray(self.cam, size = self.cam.resolution)

        self.maxvidsize = self.config.vid.maxvidsize if self.config.vid.maxvidsize>0 else 999


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

        fps = round(1. / (self.config.cam.shutterspeed / 1000000.),2)
        self.config.img.imgfps = min(max(fps, minfps), maxfps)


    def _namefile(self):

        """
        Provides a filename for the media recorded. Filenames can include label,
        date, rpi name, and time. Images part of image sequence additionally
        can contain a sequence number. e.g. test_180708_pi12_S01_100410. Filename
        is constructed from provided nameparams 1-5.
        """

        self.filetype = ".jpg" if self.config.rec.rectype in ["img","imgseq"] else ".h264"
        nparlist = [self.config.cus.nameparam1,self.config.cus.nameparam2,self.config.cus.nameparam3,
                    self.config.cus.nameparam4,self.config.cus.nameparam5]

        if "label" in nparlist:
            nparlist[nparlist.index("label")] = self.config.rec.label
        if "date" in nparlist:
            nparlist[nparlist.index("date")] = strftime("%y%m%d")
        if "time" in nparlist:
            nparlist[nparlist.index("time")] = "{timestamp:%H%M%S}"
        if "datetime" in nparlist:
            nparlist[nparlist.index("datetime")] = strftime("%y%m%d")+"{timestamp:%H%M%S}"
        if "rpi" in nparlist:
            nparlist[nparlist.index("rpi")] = self.host
        if "counter" in nparlist:
            if self.config.rec.rectype == "imgseq":
                counter = "im{counter:05d}" if self.config.img.imgnr>999 else "im{counter:03d}"
                nparlist[nparlist.index("counter")] = counter
            else:
                nparlist[nparlist.index("counter")] = ""
        if "" in nparlist:
            inds = [i for (i,it) in enumerate(nparlist) if it==""]
            nparlist = [i for j, i in enumerate(nparlist) if j not in inds]

        self.filename = "_".join(nparlist)+self.filetype

        if self.config.rec.subdirs:
            subdir = name("_".join([self.config.rec.label, strftime("%y%m%d"), self.host]))
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
            lineprint("Shutterspeed set to " + str(self.cam.exposure_speed))
            lineprint("White balance gains set to " + str(self.config.cus.gains))

        stream.close()
        self.rawCapture.close()
        self.cam.close()


    def settings(self, overwrite = True, **kwargs):

        """
        Configure the camera and recording settings

        Parameters
        ---------------
        overwrite : bool, default = True
            If settings should be overwritten
        recdir : str, default = "pirecorder/recordings"
            The directory where media will be stored. Default is "recordings".
            If different, a folder with name corresponding to location will be
            created inside the home directory. If no name is provided (""), the
            files are stored in the home directory. If "NAS" is provided it will
            additionally check if the folder links to a mounted drive.
        subdirs : bool, default = False
            If files of individual recordings should be stored in subdirectories
            or not, to keep all files of a single recording session together.
        label : str, default = "test"
            Label that will be associated with the specific recording and stored
            in the filenames.
        rectype : ["img", "imgseq", "vid", "vidseq"], default = "img"
            Recording type, either a single image or video or a sequence of
            images or videos.
        automode : bool, default = True
            If the shutterspeed and white balance should be set automatically
            and dynamically for each recording.
        maxres : str or tuple, default = "v2"
            The maximum potential resolution of the camera used. Either provide
            a tuple of the max resolution, or use "v1.3", "v1.5", "v2" (default)
            or "hq" to get the maximum resolution associated with the official
            cameras directly. Note that "v2" is the default so when an older
            camera model is connected this should be set here.
        annotatesize : int, default = 0
            The font size of the annotation. If a value of less than 6 is provided
            no annotation will be shown.
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
        maxviddur : int, default = 3600
            The maximum duration in seconds for single videos, beyond which
            videos will be automatically split. A value of 0 indicates there is
            no maximum file duration.
        maxvidsize : int, default = 0
            The maximum file size in Megabytes for single videos, beyond which
            videos will be automatically split. A value of 0 indicates there is
            no maximum file size.
        nameparam1-5: str, default = ("label","date","rpi","counter","time")
            The elements of the filename to include
        """
        overwrite = kwargs["overwrite"] if "overwrite" in kwargs else overwrite

        if ("recdir" in kwargs and overwrite) or ("recdir" not in str(self.config) and not overwrite):
                self.config.rec.recdir = kwargs["recdir"]
        if ("subdirs" in kwargs and overwrite) or ("subdirs" not in str(self.config) and not overwrite):
            self.config.rec.subdirs = kwargs["subdirs"]
        if ("label" in kwargs and overwrite) or ("label" not in str(self.config) and not overwrite):
            self.config.rec.label = kwargs["label"]
        if ("rectype" in kwargs and overwrite) or ("rectype" not in str(self.config) and not overwrite):
            self.config.rec.rectype = kwargs["rectype"]
        if ("maxres" in kwargs and overwrite) or ("maxres" not in str(self.config) and not overwrite):
            self.config.rec.maxres = kwargs["maxres"]
            self.config.img.imgdims = (3264,2464)
            if self.config.rec.maxres is not None:
                if self.config.rec.maxres in ("v1.5","v1.3","v2","hq"):
                    if self.config.rec.maxres in ("v1.5","v1.3"):
                        self.config.img.imgdims = (2592,1944)
                    if self.config.rec.maxres == "v2":
                        self.config.img.imgdims = (3264,2464)
                    if self.config.rec.maxres == "hq":
                        self.config.img.imgdims = (4056,3040)
                elif isinstance(self.config.rec.maxres, tuple):
                    self.config.img.imgdims = self.config.rec.maxres
                else:
                    try:
                        self.config.zrec.imgdims = literal_eval(self.config.rec.maxres)
                    except:
                        pass

        if ("annotatesize" in kwargs and overwrite) or ("annotatesize" not in str(self.config) and not overwrite):
            self.config.cus.annotatesize = kwargs["annotatesize"]
        if ("rotation" in kwargs and overwrite) or ("rotation" not in str(self.config) and not overwrite):
            self.config.cus.rotation = kwargs["rotation"]
        if ("brighttune" in kwargs and overwrite) or ("brighttune" not in str(self.config) and not overwrite):
            self.config.cus.brighttune = kwargs["brighttune"]
        if ("roi" in kwargs and overwrite) or ("roi" not in str(self.config) and not overwrite):
            self.config.cus.roi = kwargs["roi"]
        if ("gains" in kwargs and overwrite) or ("gains" not in str(self.config) and not overwrite):
            self.config.cus.gains = kwargs["gains"]

        if ("nameparam1" in kwargs and overwrite) or ("nameparam1" not in str(self.config) and not overwrite):
            if kwargs["nameparam1"] in self.nametypes:
                self.config.cus.nameparam1 = kwargs["nameparam1"]
            else:
                lineprint("Name parameter 1 does not exist..")
        if ("nameparam2" in kwargs and overwrite) or ("nameparam2" not in str(self.config) and not overwrite):
            if kwargs["nameparam2"] in self.nametypes:
                self.config.cus.nameparam2 = kwargs["nameparam2"]
            else:
                lineprint("Name parameter 2 does not exist..")
        if ("nameparam3" in kwargs and overwrite) or ("nameparam3" not in str(self.config) and not overwrite):
            if kwargs["nameparam3"] in self.nametypes:
                self.config.cus.nameparam3 = kwargs["nameparam3"]
            else:
                lineprint("Name parameter 3 does not exist..")
        if ("nameparam4" in kwargs and overwrite) or ("nameparam4" not in str(self.config) and not overwrite):
            if kwargs["nameparam4"] in self.nametypes:
                self.config.cus.nameparam4 = kwargs["nameparam4"]
            else:
                lineprint("Name parameter 4 does not exist..")
        if ("nameparam5" in kwargs and overwrite) or ("nameparam5" not in str(self.config) and not overwrite):
            if kwargs["nameparam5"] in self.nametypes:
                self.config.cus.nameparam5 = kwargs["nameparam5"]
            else:
                lineprint("Name parameter 5 does not exist..")

        if ("automode" in kwargs and overwrite) or ("automode" not in str(self.config) and not overwrite):
            self.config.cam.automode = kwargs["automode"]
        if ("brightness" in kwargs and overwrite) or ("brightness" not in str(self.config) and not overwrite):
            self.config.cam.brightness = kwargs["brightness"]
        if ("contrast" in kwargs and overwrite) or ("contrast" not in str(self.config) and not overwrite):
            self.config.cam.contrast = kwargs["contrast"]
        if ("saturation" in kwargs and overwrite) or ("saturation" not in str(self.config) and not overwrite):
            self.config.cam.saturation = kwargs["saturation"]
        if ("iso" in kwargs and overwrite) or ("iso" not in str(self.config) and not overwrite):
            self.config.cam.iso = kwargs["iso"]
        if ("sharpness" in kwargs and overwrite) or ("sharpness" not in str(self.config) and not overwrite):
            self.config.cam.sharpness = kwargs["sharpness"]
        if ("compensation" in kwargs and overwrite) or ("compensation" not in str(self.config) and not overwrite):
            self.config.cam.compensation = kwargs["compensation"]
        if ("shutterspeed" in kwargs and overwrite) or ("shutterspeed" not in str(self.config) and not overwrite):
            self.config.cam.shutterspeed = kwargs["shutterspeed"]

        if ("imgdims" in kwargs and overwrite) or ("imgdims" not in str(self.config) and not overwrite):
            self.config.img.imgdims = kwargs["imgdims"]
        if ("viddims" in kwargs and overwrite) or ("viddims" not in str(self.config) and not overwrite):
            self.config.vid.viddims = kwargs["viddims"]
        if ("imgfps" in kwargs and overwrite) or ("imgfps" not in str(self.config) and not overwrite):
            self.config.img.imgfps = kwargs["imgfps"]
        if ("vidfps" in kwargs and overwrite) or ("vidfps" not in str(self.config) and not overwrite):
            self.config.vid.vidfps = kwargs["vidfps"]

        if ("imgwait" in kwargs and overwrite) or ("imgwait" not in str(self.config) and not overwrite):
            self.config.img.imgwait = kwargs["imgwait"]
        if ("imgnr" in kwargs and overwrite) or ("imgnr" not in str(self.config) and not overwrite):
            self.config.img.imgnr = kwargs["imgnr"]
        if ("imgtime" in kwargs and overwrite) or ("imgtime" not in str(self.config) and not overwrite):
            self.config.img.imgtime = kwargs["imgtime"]
        if ("imgquality" in kwargs and overwrite) or ("imgquality" not in str(self.config) and not overwrite):
            self.config.img.imgquality = kwargs["imgquality"]

        if ("vidduration" in kwargs and overwrite) or ("vidduration" not in str(self.config) and not overwrite):
            self.config.vid.vidduration = kwargs["vidduration"]
        if ("viddelay" in kwargs and overwrite) or ("viddelay" not in str(self.config) and not overwrite):
            self.config.vid.viddelay = kwargs["viddelay"]
        if ("vidquality" in kwargs and overwrite) or ("vidquality" not in str(self.config) and not overwrite):
            self.config.vid.vidquality = kwargs["vidquality"]
        if ("maxviddur" in kwargs and overwrite) or ("maxviddur" not in str(self.config) and not overwrite):
            self.config.vid.maxviddur = kwargs["maxviddur"]
        if ("maxvidsize" in kwargs and overwrite) or ("maxvidsize" not in str(self.config) and not overwrite):
            self.config.vid.maxvidsize = kwargs["maxvidsize"]

        brightchange = False
        if os.path.exists(self.brightfile):
            with open(self.brightfile) as f:
                brighttune = yaml.load(f, Loader=yaml.FullLoader)
                if brighttune != self.config.cus.brighttune:
                    if "internal" not in kwargs:
                        lineprint("cusbright.yml file found and loaded..")
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
                       maxres=self.config.rec.maxres)
        if vidstream.roi:
            self.settings(roi=vidstream.roi, internal="")
            lineprint("Roi stored..")
        else:
            lineprint("No roi selected..")


    def camconfig(self, fps=None, vidsize=0.4):

        lineprint("Opening stream for interactive configuration..")
        fps = max(self.config.vid.vidfps,1) if fps == None else int(fps)
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
        .h264 or .jpg files that are named automatically
        """

        self._setup_cam()
        self._namefile()
        startdate = datetime.now()

        if self.config.rec.rectype == "img":

            if "{timestamp:%H%M%S}" in self.filename:
                filename = self.filename.replace("{timestamp:%H%M%S}",strftime("%H%M%S"))
            if self.config.cus.annotatesize > 5:
                self.cam.annotate_text = filename.replace(".jpg","").split("/",1)[0]
            self.cam.capture(filename, format="jpeg", resize = self.resize,
                             quality = self.config.img.imgquality)
            lineprint("Captured "+filename)

        elif self.config.rec.rectype == "imgseq":

            starttime = datetime.now()
            timepoint = starttime
            if self.config.cus.annotatesize > 5:
                if "{timestamp:%H%M%S}" in self.filename:
                    filename = self.filename.replace("{timestamp:%H%M%S}",strftime("%H%M%S"))
                    filename = filename.replace("{counter:03d}","001").split("/",1)[::-1][0]
                    filename = filename.replace("{counter:05d}","00001").split("/",1)[::-1][0]
                self.cam.annotate_text = filename.replace(".jpg","")
            counter= 1
            for i, img in enumerate(self.cam.capture_continuous(self.filename,
                                    format="jpeg", resize = self.resize,
                                    quality = self.config.img.imgquality)):
                counter += 1
                if startdate.day < datetime.now().day:
                    self.cam.close()
                    self.record()
                tottimepassed = (datetime.now() - starttime).total_seconds()
                if i < self.config.img.imgnr-1 and tottimepassed < self.config.img.imgtime:
                    timepassed = (datetime.now() - timepoint).total_seconds()
                    delay = max(0, self.config.img.imgwait - timepassed)
                    lineprint("Captured "+img+", sleeping "+str(round(delay,2))+"s..")
                    sleep(delay)
                    timepoint = datetime.now()
                    if self.config.cus.annotatesize>5:
                        if "{timestamp:%H%M%S}" in self.filename:
                            filename = self.filename.replace("{timestamp:%H%M%S}",strftime("%H%M%S"))
                            filename = filename.replace("{counter:03d}","{:03d}".format(counter)).split("/",1)[::-1][0]
                            filename = filename.replace("{counter:05d}","{:05d}".format(counter)).split("/",1)[::-1][0]
                            self.cam.annotate_text = filename.split("/",1)[::-1][0].replace(".jpg","")
                else:
                    lineprint("Captured "+img)
                    break

        elif self.config.rec.rectype in ["vid","vidseq"]:

            # # Temporary fix for flicker at start of (first) video
            # self.cam.start_recording(BytesIO(), format = "h264",
            #                         resize = self.resize, level = "4.2")
            # self.cam.wait_recording(2)
            # self.cam.stop_recording()

            # Wait for user input before starting the first video session
            input("Press Enter to start the first video session...")
        
            for session in ["_S%02d" % i for i in range(1,999)]:
                if "{timestamp:%H%M%S}" in self.filename:
                    filename = self.filename.replace("{timestamp:%H%M%S}",strftime("%H%M%S"))
                session = "" if self.config.rec.rectype == "vid" else session
                filename = filename.replace(".h264",session)
                timeremaining = self.config.vid.vidduration+self.config.vid.viddelay
                counter = 0
                while timeremaining > 0:
                    counter += 1
                    waittime = timeremaining
                    if self.config.vid.maxviddur > 0:
                        waittime = min(timeremaining, self.config.vid.maxviddur)
                    if waittime == timeremaining and self.config.vid.maxvidsize == 0:
                        nr = ""
                    else:
                        nr = "_v"+str(counter).zfill(2)
                    finalname = filename+nr+self.filetype
                    video = VidOutput(finalname)
                    if self.config.cus.annotatesize > 5:
                        self.cam.annotate_text = finalname.replace(".h264","").split("/",1)[::-1][0]
                    self.cam.start_recording(video, resize = self.resize,
                                            quality = self.config.vid.vidquality,
                                            level = "4.2",
                                            format = self.filetype[1:])
                    lineprint("Start recording "+filename)
                    rectime = 0
                    while video.size < self.maxvidsize*1000000 and rectime < waittime:
                        rectime += 0.1
                        if self.config.cus.annotatesize > 5:
                            filename = self.filename.replace("{timestamp:%H%M%S}",strftime("%H%M%S"))
                            self.cam.annotate_text = filename.replace(".h264","").split("/",1)[::-1][0]
                        self.cam.wait_recording(0.1)
                    timeremaining -= rectime
                    self.cam.stop_recording()
                    vidinfo = " ("+str(round(rectime))+"s; "+str(round(video.size/1000000,2))+"MB)"
                    lineprint("Finished recording "+finalname+vidinfo)
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
