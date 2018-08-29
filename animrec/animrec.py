# coding: utf-8

import picamera
from time import sleep, strftime
from datetime import datetime
import os
import sys

from localconfig import LocalConfig
from socket import gethostname
from ast import literal_eval
from fractions import Fraction

from animlab.utils import homedir, isscript, lineprint
from .__version__ import __version__

class Tee:
    def write(self, *args, **kwargs):
        self.out1.write(*args, **kwargs)
        self.out2.write(*args, **kwargs)
    def __init__(self, out1, out2):
        self.out1 = out1
        self.out2 = out2

class Recorder:

    """ Recorder class for setting up the rpi to record images or video """

    def __init__(self, configfile = "animrec.conf"):

        self.host = gethostname()
        self.home = homedir()
        self.setupdir = self.home + "setup"
        sys.stdout = Tee(open(self.setupdir+"/animrec.log", "a"), sys.stdout)

        lineprint("==========================================", False)
        lineprint(strftime("%d/%m/%y %H:%M:%S - AnimRec "+__version__+" started"), False)
        lineprint("==========================================", False)

        if not os.path.exists(self.setupdir):
            os.makedirs(self.setupdir)
        self.configfile = self.setupdir + "/"+configfile
        self.config = LocalConfig(self.configfile, compact_form = True)
        if not os.path.isfile(self.configfile):
            lineprint("New config file created")
            for section in ['rec','cam','cus', 'img','vid']:
                if section not in list(self.config):
                    self.config.add_section(section)
            self.set_config(recdir="NAS", label="test", rectype="vid",
                            brightness=45, contrast=10, saturation=-100, iso=200,
                            sharpness=0, compensation=0, shutterspeed=8000,
                            imgquality=50, vidquality = 11, gains=(1.0, 2.5),
                            rotation=0, brighttune=0, imgdims=(3280, 2464),
                            imgfps=1, imgwait=5.0, imgnr=100, imgtime=600,
                            viddims=(1640, 1232), vidfps=24, vidduration=10,
                            viddelay=10)
        else:
            lineprint("Config settings loaded. Recording "+\
                           self.config.rec.type+" @ "+self.config.rec.dir)

        self.imgparams()
        self.shuttertofps()

        if self.config.rec.dir == "NAS":
            if not os.path.ismount(self.config.rec.dir):
                self.recdir = self.home
                lineprint("Recdir not mounted, storing in home directory..")
        self.recdir = self.home + self.config.rec.dir
        if not os.path.exists(self.recdir):
            os.makedirs(self.recdir)

        self.filetype = ".jpg" if self.config.rec.type in ["img","imgseq"] else ".h264"

        os.chdir(self.recdir)


    def set_config(self, **kwargs):

        if "recdir" in kwargs:
            self.config.rec.dir = kwargs["recdir"]
        if "label" in kwargs:
            self.config.rec.label = kwargs["label"]
        if "rectype" in kwargs:
            self.config.rec.type = kwargs["rectype"]

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
        if "imgfps" in kwargs:
            self.config.img.fps = kwargs["imgfps"]
        if "vidfps" in kwargs:
            self.config.vid.fps = kwargs["vidfps"]

        if "rotation" in kwargs:
            self.config.cus.rotation = kwargs["rotation"]
        if "brighttune" in kwargs:
            self.config.cus.brighttune = kwargs["brighttune"]
        if "gains" in kwargs:
            self.config.cus.gains = kwargs["gains"]

        if "imgdims" in kwargs:
            self.config.img.dims = kwargs["imgdims"]
        if "viddims" in kwargs:
            self.config.vid.dims = kwargs["viddims"]
        if "imgquality" in kwargs:
            self.config.img.quality = kwargs["imgquality"]

        if "imgwait" in kwargs:
            self.config.img.wait = kwargs["imgwait"]
        if "imgnr" in kwargs:
            self.config.img.nr = kwargs["imgnr"]
        if "imgtime" in kwargs:
            self.config.img.time = kwargs["imgtime"]

        if "vidduration" in kwargs:
            self.config.vid.duration = kwargs["vidduration"]
        if "viddelay" in kwargs:
            self.config.vid.delay = kwargs["viddelay"]
        if "vidquality" in kwargs:
            self.config.vid.quality = kwargs["vidquality"]

        if len(kwargs) > 0:

            self.imgparams()
            self.shuttertofps()

            if os.path.isfile(self.configfile):
                lineprint("Config settings stored and loaded..")

            self.config.save()


    def setup_cam(self):

        self.cam = picamera.PiCamera()

        self.cam.rotation = self.config.cus.rotation
        self.cam.exposure_compensation = self.config.cam.compensation

        if self.config.rec.type == "img":
            self.cam.resolution = literal_eval(self.config.img.dims)
            self.cam.framerate = self.config.img.fps
        if self.config.rec.type == "vid":
            self.cam.resolution = literal_eval(self.config.vid.dims)
            self.cam.framerate = self.config.vid.fps

        sleep(2)

        self.cam.shutter_speed = self.config.cam.shutterspeed
        self.cam.exposure_mode = 'off'
        self.cam.awb_mode = 'off'
        self.cam.awb_gains = literal_eval(self.config.cus.gains)
        self.cam.brightness = self.config.cam.brightness
        self.cam.contrast = self.config.cam.contrast
        self.cam.saturation = self.config.cam.saturation
        self.cam.iso = self.config.cam.iso
        self.cam.sharpness = self.config.cam.sharpness

        lineprint("Camera started..")


    def imgparams(self, mintime = 0.45):

        """ Calculates minimum possible imgwait and imgnr based on imgtime.
            The minimum time between subsequent images is by default set to
            0.45s, the time it takes to take an image with max resolution.
        """

        self.config.img.wait = max(mintime, self.config.img.wait)
        totimg = int(self.config.img.time / self.config.img.wait)
        self.config.img.nr = min(self.config.img.nr, totimg)


    def shuttertofps(self, minfps = 1, maxfps = 40):

        """ Computes image fps based on shutterspeed within provided range """

        fps = int(1./(self.config.cam.shutterspeed/1000000.))
        fps = max(fps, minfps)
        self.config.img.fps = min(fps, maxfps)


    def namefile(self):

        """ Provides a filename for the media recorded. Filenames include label,
            date, rpi name, and time. Images part of image sequence
            additionally contain a sequence number. e.g.
            test_180708_pi12_S01_100410
        """

        if self.config.rec.type == "imgseq":
            date = "{timestamp:%y%m%d}"
            counter = "im{counter:05d}" if self.config.img.nr>999 else "im{counter:03d}"
            time = "{timestamp:%H%M%S}"
            self.filename = "_".join([self.config.rec.label,date,self.host,counter,time])
            self.filename = self.filename+self.filetype
        else:
            date = strftime("%y%m%d")
            self.filename = "_".join([self.config.rec.label, date, self.host])+"_"


    def record(self):

        self.setup_cam()
        self.namefile()

        if self.config.rec.type == "img":

            self.filename = self.filename + strftime("%H%M%S") + self.filetype
            self.cam.capture(self.filename, format="jpeg", quality = self.config.img.quality)
            lineprint("Captured "+self.filename)

        if self.config.rec.type == "imgseq":

            timepoint = datetime.now()
            for i, img in enumerate(self.cam.capture_continuous(self.filename,
                                    format="jpeg", quality = self.config.img.quality)):
                if i < self.config.img.nr-1:
                    timepassed = (datetime.now() - timepoint).total_seconds()
                    delay = max(0, self.config.img.wait - timepassed)
                    lineprint("Captured "+img+", sleeping "+str(round(delay,2))+"s..")
                    sleep(delay)
                    timepoint = datetime.now()
                else:
                    lineprint("Captured "+img)
                    break

        if self.config.rec.type == "vid":

            for filename in self.cam.record_sequence(self.filename+strftime("%H%M%S" )+\
                            "_S%02d" % i + self.filetype for i in range(1,9999)):
                lineprint("Recording "+filename)
                self.cam.wait_recording(self.config.vid.duration + self.config.vid.delay)
                lineprint("Finished")
                if raw_input("\nn for new session, e to exit: ") == 'e':
                    break

        self.cam.close()
