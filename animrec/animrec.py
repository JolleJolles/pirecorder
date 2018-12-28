#! /usr/bin/env python
#
# Controlled media recording library for the Rasperry-Pi
# Copyright (c) 2015 - 2018 Jolle Jolles <j.w.jolles@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
from builtins import input

import os
import sys
import cv2
import yaml
import crontab
import getpass
import picamera
import picamera.array

import numpy as np
from time import sleep, strftime
from datetime import datetime
from localconfig import LocalConfig
from socket import gethostname
from ast import literal_eval
from fractions import Fraction

import animlab.utils as alu


class Recorder:

    """
    Recorder class for setting up the rpi for controlled video or image recording.

    Parameters
    ----------
    recdir : str, default = "recordings"
        The directory where media will be stored. Default is "recordings". If
        different, a folder with name corresponding to location will be created
        inside the home directory. If no name is provided (""), the files are
        stored in the home directory. If "NAS" is provided it will additionally
        check if the folder links to a mounted drive.
    label : str, default = "test"
        Label for associating with the recording and stored in the filenames.
    rectype : ["img", "imgseq", "vid"], default = "img"
        Recording type, either a single image, a sequence of images, or a video.

    Config settings
    ---------------
    rotation : int, default = 0
        Custom rotation specific to the RPi, should be either 0 or 180.
    brighttune : int, default = 0
        A rpi specific brightness compensation factor to standardize light levels
        across multiple rpi's, an integer between -10 and 10.
    roi : tuple, default = None
        Region of interest to be used for recording. Consists of coordinates of
        topleft and bottom right coordinate of a rectangular area encompassing
        the region of interest. Can be set with the set_roi() function.
    gains : tuple, default = (1.0, 2.5)
        Custom gains specific to the RPi to have a 'normal' colorspace.

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
    imgdims : tuple, default = (3280,2464)
        The resolution of the images to be taken in pixels. The default is the max
        resolution that does not return an error for this mode.
    viddims : tuple, default = (1640,1232)
        The resolution of the videos to be taken in pixels. The default is the max
        resolution that does not return an error for this mode.
    imgfps : int, default = 1
        The framerate for recording images. Will be set automatically based on
        the imgwait setting so should not be set by user.
    vidfps : int, default = 24
        The framerate for recording video.
    imgwait : float, default = 1.0
    	The delay between subsequent images in seconds. When a delay is provided
      	that is less than ~0.5s (shutterspeed + processingtime) it will be
      	automatically set to 0 and images thus taken immideately one after the other.
    imgnr : int, default = 60
        The number of images that should be taken. When this number is reached, the
        script will automatically terminate.
    imgtime : integer, default = 60
        The time in seconds during which images should be taken. The minimum of a)
        imgnr and b) nr of images based on imgwait and imgtime will be selected.
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
    Either one or multiple .h264 or .jpg files depending on the filetype and
    single input. All files are automatically named according to the label,
    the host name, date, time and potentially session number or count nr, e.g.
    - single image: 'pilot_180312_PI13_101300.jpg
    - multiple images: 'pilot_180312_PI13_img00231_101300.jpg
    - video: 'pilot_180312_PI13_S01_101300.h264

    Returns
    -------
    self : class
        Recorder class instance

    """

    def __init__(self, configfile = "animrec.conf"):

        alu.lineprint("==========================================", False)
        alu.lineprint(strftime("%d/%m/%y %H:%M:%S - AnimRec "+__version__+" started"), False)
        alu.lineprint("==========================================", False)

        self.host = gethostname()
        self.home = alu.homedir()
        self.setupdir = self.home + "setup"
        self.logfolder = self.setupdir+"/logs"
        if not os.path.exists(self.setupdir):
            os.makedirs(self.setupdir)
            os.makedirs(self.logfolder)
            alu.lineprint("Setup folder created (" + setupdir + ")")

        sys.stdout = alu.Logger(self.logfolder+"/animrec.log")

        self.brightfile = self.setupdir + "/cusbright.yml"
        self.roifile = self.setupdir + "/cusroi.yml"
        self.configfile = self.setupdir + "/"+configfile

        self.config = LocalConfig(self.configfile, compact_form = True)
        if not os.path.isfile(self.configfile):
            alu.lineprint("New config file created")
            for section in ['rec','cam','cus', 'img','vid']:
                if section not in list(self.config):
                    self.config.add_section(section)
            self.set_config(recdir="recordings", label="test", rectype="vid",
                            rotation=0, brighttune=0, roi=None, gains=(1.0, 2.5),
                            brightness=45, contrast=10, saturation=-100, iso=200,
                            sharpness=0, compensation=0, shutterspeed=8000,
                            imgdims=(3280, 2464), viddims=(1640, 1232), imgfps=1,
                            vidfps=24, imgwait=5.0, imgnr=100, imgtime=600,
                            imgquality=50, vidduration=10, viddelay=10,
                            vidquality = 11,internal="")
            alu.lineprint("Config settings stored")
        else:
            alu.lineprint("Config settings loaded. Type: "+self.config.rec.type+\
                          "; location: "+self.home+self.config.rec.dir)

        self._imgparams()
        self._shuttertofps()

        if self.config.rec.dir == "NAS":
            if not os.path.ismount(self.config.rec.dir):
                self.recdir = self.home
                alu.lineprint("Recdir not mounted, storing in home directory..")
        self.recdir = self.home + self.config.rec.dir
        if not os.path.exists(self.recdir):
            os.makedirs(self.recdir)

        self.filetype = ".jpg" if self.config.rec.type in ["img","imgseq"] else ".h264"

        os.chdir(self.recdir)


    def _setup_cam(self, simple = False):

        """ Sets-up the raspberry pi camera based on configuration """

        self.cam = picamera.PiCamera()
        self.cam.rotation = self.config.cus.rotation
        self.cam.exposure_compensation = self.config.cam.compensation

        if simple:
            self.cam.resolution = (1280, 720)
        else:
            if self.config.rec.type == "img":
                self.cam.resolution = literal_eval(self.config.img.dims)
                self.cam.framerate = self.config.img.fps
            if self.config.rec.type == "vid":
                self.cam.resolution = literal_eval(self.config.vid.dims)
                self.cam.framerate = self.config.vid.fps
            self.rawCapture = picamera.array.PiRGBArray(self.cam, size = self.cam.resolution)

        sleep(0.1)

        self.cam.shutter_speed = self.config.cam.shutterspeed
        self.cam.exposure_mode = 'off'
        self.cam.awb_mode = 'off'
        self.cam.awb_gains = alu.check_frac(self.config.cus.gains)
        brightness = self.config.cam.brightness + self.config.cus.brighttune
        self.cam.brightness = brightness

        if not simple:
            self.cam.contrast = self.config.cam.contrast
            self.cam.saturation = self.config.cam.saturation
            self.cam.iso = self.config.cam.iso
            self.cam.sharpness = self.config.cam.sharpness

        alu.lineprint("Camera started..")


    def _imgparams(self, mintime = 0.45):

        """
        Calculates minimum possible imgwait and imgnr based on imgtime. The
        minimum time between subsequent images is by default set to 0.45s, the
        time it takes to take an image with max resolution.
        """

        self.config.img.wait = max(mintime, self.config.img.wait)
        totimg = int(self.config.img.time / self.config.img.wait)
        self.config.img.nr = min(self.config.img.nr, totimg)


    def _shuttertofps(self, minfps = 1, maxfps = 40):

        """ Computes image fps based on shutterspeed within provided range """

        fps = int(1./(self.config.cam.shutterspeed/1000000.))
        fps = max(fps, minfps)
        self.config.img.fps = min(fps, maxfps)


    def _namefile(self):

        """
        Provides a filename for the media recorded. Filenames include label,
        date, rpi name, and time. Images part of image sequence additionally
        contain a sequence number. e.g. test_180708_pi12_S01_100410
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


    def _drawrect(self, event, x, y, flags, param):

        """ Draws a rectangle on an opencv window """

        self.draw_frame = self.frame.copy()
        if event == cv2.EVENT_LBUTTONDOWN:
            self.rectangle = True
            self.refPt = [(x,y)]

        elif event == cv2.EVENT_LBUTTONUP:
            self.rectangle = False
            self.refPt.append((x, y))
            cv2.rectangle(self.draw_frame,self.refPt[0],self.refPt[1],(0,0,255),2)

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.rectangle:
                cv2.rectangle(self.draw_frame,self.refPt[0],(x,y),(0,0,255),2)
            else:
                if hasattr(self, 'refPt'):
                    cv2.rectangle(self.draw_frame,self.refPt[0],self.refPt[1],(0,0,255),2)

        cv2.line(self.draw_frame, (x-5,y), (x+5,y), alu.namedcols("white"), 1)
        cv2.line(self.draw_frame, (x,y-5), (x,y+5), alu.namedcols("white"), 1)


    def _check_job(self):

        """ Returns scheduled jobs with a certain name """

        return [job for job in self.cron if job.comment == self.jobname]


    def _clear_jobs(self):

        """ Clears a specific or all jobs currently scheduled """

        if self.jobsclear == None:
            pass
        elif self.jobsclear == "all":
            self.cron.remove_all()
            alu.lineprint("All scheduled jobs removed..")
        elif self.jobsclear == "job":
            if len(self.jobfits)>0:
                self.cron.remove(self.jobfits[0])
                alu.lineprint(self.jobname+" job removed..")
            else:
                if(self.jobname == None):
                    alu.lineprint("No jobname provided..")
                else:
                    alu.lineprint("No fitting job found to remove..")
        else:
            alu.lineprint("No correct clear command provided..")
        self.cron.write()


    def _show_jobs(self):

        """ Prints a table of all scheduled jobs """

        if len(self.cron)>0:
            alu.lineprint("Current job schedule:")
            for job in self.cron:
                lenjob = max(8, len(job.comment))
                lenplan = max(8, len(str(job)[:str(job).find("py")-1]))
            print("Job"+" "*(lenjob-3)+"Time plan"+" "*(lenplan-7)+"Next recording")
            print("="*40)
            for job in self.cron:
                sch = job.schedule(date_from = datetime.now())
                jobname = job.comment+" "*(lenjob-len(job.comment))
                plan = str(job)[:str(job).find("py")-1]
                plan = plan + " "*(lenplan-(len(plan)-2))
                next = str(sch.get_next()) if job.is_enabled() else " disabled"
                print(jobname + plan + next)
        else:
            alu.lineprint("Currently no jobs scheduled..")


    def _set_job(self):

        """ Creates/modifies a specific job """

        if len(self.jobfits)>0:
            self.job = self.jobfits[0]
            self.job.command = self.task
        else:
            self.job = self.cron.new(command = self.task, comment = self.jobname)
        self.job.setall(self.jobtimeplan)

        #self.job.frequency_per_day()
        self.cron.write()
        alu.lineprint(self.jobname+" job succesfully set..")
        self._enable_job()


    def _enable_job(self):

        """ Enables/disables a specific job """

        if self.jobenable:
            self.job.enable(True)
            alu.lineprint(self.jobname+" job enabled..")
        else:
            self.job.enable(False)
            alu.lineprint(self.jobname+" job disabled..")
        self.cron.write()


    def set_config(self, **kwargs):

        """ Dynamically sets the configuration file """

        if "recdir" in kwargs:
            self.config.rec.dir = kwargs["recdir"]
        if "label" in kwargs:
            self.config.rec.label = kwargs["label"]
        if "rectype" in kwargs:
            self.config.rec.type = kwargs["rectype"]

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
            self.config.img.dims = kwargs["imgdims"]
        if "viddims" in kwargs:
            self.config.vid.dims = kwargs["viddims"]
        if "imgfps" in kwargs:
            self.config.img.fps = kwargs["imgfps"]
        if "vidfps" in kwargs:
            self.config.vid.fps = kwargs["vidfps"]

        if "imgwait" in kwargs:
            self.config.img.wait = kwargs["imgwait"]
        if "imgnr" in kwargs:
            self.config.img.nr = kwargs["imgnr"]
        if "imgtime" in kwargs:
            self.config.img.time = kwargs["imgtime"]
        if "imgquality" in kwargs:
            self.config.img.quality = kwargs["imgquality"]

        if "vidduration" in kwargs:
            self.config.vid.duration = kwargs["vidduration"]
        if "viddelay" in kwargs:
            self.config.vid.delay = kwargs["viddelay"]
        if "vidquality" in kwargs:
            self.config.vid.quality = kwargs["vidquality"]

        if os.path.exists(self.brightfile):
            with open(self.brightfile) as f:
                brighttune = yaml.load(f)
                if brighttune != self.config.cus.brighttune:
                    self.config.cus.brighttune = brighttune
                    brightchange = True

        if len(kwargs) > 0 or brightchange:

            self._imgparams()
            self._shuttertofps()
            self.config.save()

            if "internal" not in kwargs:
                alu.lineprint("Config settings stored and loaded..")


    def show_config(self):

        """ Shows the currently set configuration settings"""

        for section in self.config:
            print(section)
            for key,value in self.config.items(section):
                print(key,"=",value)
            print("")


    def set_roi(self):

        """ Sets the roi for recording with the Raspberry Pi camera"""

        self.rectangle = False
        self._setup_cam()
        res = (int(self.cam.resolution[0]/4),int(self.cam.resolution[0]/4))
        self.cam.capture(self.rawCapture, format="bgr")
        self.frame = self.rawCapture.array
        self.draw_frame = self.frame.copy()

        cv2.namedWindow('window', cv2.WINDOW_NORMAL)
        cv2.setMouseCallback('window', self._drawrect)

        alu.lineprint("Select roi..")

        while True:
            cv2.imshow('window', self.draw_frame)
            cv2.moveWindow('window', 50,0)
            k = cv2.waitKey(1) & 0xFF

            if k == ord('e') and hasattr(self, "refPt"):
                del self.refPt

            if k == ord('s'):
                if hasattr(self, "refPt"):
                    pt = self.refPt
                    if len(self.refPt) == 1:
                        pt = [self.refPt[0],self.refPt[0]]
                    pt1 = (min(pt[0][0], pt[1][0]), min(pt[0][1], pt[1][1]))
                    pt2 = (max(pt[0][0], pt[1][0]), max(pt[0][1], pt[1][1]))
                    roi = ((pt1,pt2))

                    self.set_config(roi=roi,internal="")
                    alu.lineprint("roi coordinates " + str(roi) + " stored..")
                    break

                else:
                    alu.lineprint("Nothing to save..")

            if k == 27:
                alu.lineprint("User escaped..")
                break

        self.cam.close()
        cv2.destroyWindow('window')
        cv2.waitKey(1)


    def set_gains(self, attempts = 100, step = 0.05):

        """ Automatically finds the best gains for the raspberry pi camera"""

        # This function was written based on code provided by Dave Jones in a
        # reply on a question posted on stackoverflow: https://bit.ly/2V49f48

        self._setup_cam(simple=True)
        rg, bg = self.cam.awb_gains

        with picamera.array.PiRGBArray(self.cam, size=(128, 72)) as output:

            for i in range(attempts):

                # Capture a tiny resized image in RGB format, and extract the
                # average R, G, and B values
                self.cam.capture(output, format='rgb', resize=(128, 80), use_video_port=True)
                r, g, b = (np.mean(output.array[..., i]) for i in range(3))
                print("R:%5.2f, B:%5.2f = (%5.2f, %5.2f, %5.2f)" % (rg, bg, r, g, b))

                # Adjust R and B relative to G, but only if they're significantly
                # different (delta +/- 2)
                if abs(r - g) > 2:
                    if r > g:
                        rg -= step
                    else:
                        rg += step
                if abs(b - g) > 1:
                    if b > g:
                        bg -= step
                    else:
                        bg += step

                self.cam.awb_gains = (rg, bg)
                output.seek(0)
                output.truncate()

        self.set_config(gains="(%5.2f, %5.2f)" % (rg, bg), internal="")
        alu.lineprint("Gains: " + "(R:%5.2f, B:%5.2f)" % (rg, bg) + " stored..")
        self.cam.close()


    def record(self):

        """ Runs the Recorder instance """

        self._setup_cam()
        self._namefile()

        if self.config.rec.type == "img":

            self.filename = self.filename + strftime("%H%M%S") + self.filetype
            self.cam.capture(self.filename, format="jpeg", quality = self.config.img.quality)
            alu.lineprint("Captured "+self.filename)
            self.cam.close()

        if self.config.rec.type == "imgseq":

            timepoint = datetime.now()
            for i, img in enumerate(self.cam.capture_continuous(self.filename,
                                    format="jpeg", quality = self.config.img.quality)):
                if i < self.config.img.nr-1:
                    timepassed = (datetime.now() - timepoint).total_seconds()
                    delay = max(0, self.config.img.wait - timepassed)
                    alu.lineprint("Captured "+img+", sleeping "+str(round(delay,2))+"s..")
                    sleep(delay)
                    timepoint = datetime.now()
                else:
                    alu.lineprint("Captured "+img)
                    break
            self.cam.close()

        if self.config.rec.type == "vid":

            for session in ["_S%02d" % i for i in range(1,999)]:
                filename = self.filename+strftime("%H%M%S" )+session+self.filetype
                self.cam.start_recording(filename, quality = self.config.vid.quality)
                alu.lineprint("Recording "+filename)
                self.cam.wait_recording(self.config.vid.duration + self.config.vid.delay)
                self.cam.stop_recording()
                alu.lineprint("Finished")
                if input("\nn for new session, e to exit: ") == 'e':
                    break


    def schedule(self, jobname = None, timeplan = None, enable = True,
                 showjobs = True, clear = None):

        """
        Schedules future recordings configured with a Recorder instance

        Parameters
        ----------
        jobname : str, default = None
            The name for the scheduled recorder task to create, modify or remove.
        timeplan : string, default = None
            The code string representing the time planning for the recorder to run
            with current configuration set. Build on CRON, the time plan should
            consist of the following parts:
            * * * * *
            - - - - -
            | | | | |
            | | | | +----- day of week (0 - 7) (Sunday = 0 or 7)
            | | | +---------- month (1 - 12)
            | | +--------------- day of month (1 - 31)
            | +-------------------- hour (0 - 23)
            +------------------------- min (0 - 59)
            Each of the parts supports wildcards (*), ranges (2-5), and lists
            (2,5,6,11). For example, if you want to schedule a recording at 22:00,
            every workday of the week, enter the code '0 22 * * 1-5' If uncertain,
            crontab.guru is a great website for checking your CRON code.
        enable : bool, default = True
            If the scheduled job should be enabled or not.
        showjobs : bool, default = False
            If the differently timed tasks should be shown or not.
        clear : [None, "job", "all"], default = None
            If a specific job ('job'), all jobs ('all') or no jobs (None)
            should be removed from the scheduler.
        """

        alu.lineprint("Running scheduler..")
        self.cron = crontab.CronTab(user = getpass.getuser())

        self.jobname = jobname
        self.jobtimeplan = timeplan
        self.jobenable = enable
        self.jobsshow = showjobs
        self.jobsclear = clear

        taskc1 = "python -c 'import animrec; AR=animrec.Recorder(); AR.record()'"
        taskc2 = " >> " + self.logfolder + "/"
        taskc3 = "`date + \%y\%m\%d_$HOSTNAME`_" + str(self.jobname) + ".log 2>&1"
        self.task = taskc1 + taskc2 + taskc3

        self.jobfits = self._check_job()
        if self.jobsclear is not None:
            self._clear_jobs()
        else:
            if self.jobtimeplan is None:
                if len(self.jobfits)==0:
                    alu.lineprint("No time plan provided or fitting job found..")
                else:
                    self.job = self.jobfits[0]
                    self._enable_job()
            else:
                self._set_job()
        if self.jobsshow:
            self._show_jobs()
