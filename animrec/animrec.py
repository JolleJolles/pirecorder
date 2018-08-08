
# coding: utf-8

# - Store file with camera settings

# In[ ]:

import picamera
from time
import datetime
from socket import gethostname
import os
from ast import literal_eval
from fractions import Fraction

from animlab.utils import homedir, isscript, loadyml

class AnimRec:

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
        imgwait : float, default = 1.0
            *Image parameter only*. The delay between subsequent images
            in seconds. When a delay is provided that is less than ~0.5s
            (shutterspeed + processingtime) it will be automatically set
            to 0 and images thus taken immideately one after the other.
        imgnr : int, default = 60
            *Image parameter only*. The number of images that should be
            taken. When this number is reached, the script will
            automatically terminate.
        imgtime : integer, default = 60
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

    def lineprint(self, text, stamp = True, sameline = False, reset = False):

        if stamp:
            text = time.strftime("%H:%M:%S") + " [" + self.host + "] - " + text
        if sameline:
            if reset:
                self.line = text
                sys.stdout.write("\r")
                sys.stdout.write(" "*100)
            else:
                text = self.line + " " + text
            self.line = "\r" + text
        else:
            self.line = text if self.line == "" else "\n" + text
        print self.line,


    def imgparams(self, mintime = 0.45):

        """ Calculates minimum possible imgwait and imgnr based on imgtime.
            The minimum time between subsequent images is by default set to
            0.45s, the time it takes to  take an image with max resolution.
        """

        self.imgwait = max(mintime, self.imgwait)
        totimg = int(self.imgtime / self.imgwait)
        self.imgnr = min(self.imgnr, totimg)


    def shuttertofps(self, minfps = 1, maxfps = 40)

        """ Computes fps based on shutterspeed within a range"""

        self.fps = int(1./(self.shutterspeed/1000000.))
        self.fps = max(fps, minfps)
        self.fps = min(fps, maxfps)



    def __init__(location = "NAS", single = True, filetype = ".jpg", taskname = "test", setupdir = "setup"):

        lineprint("AnimRec started. The date is: " + strftime("%y/%m/%d"))
        lineprint("====================================")

        self.home = _homedir()
        self.setupdir = self.home + setupdir
        self.location = self.home + location
        if location == "NAS":
            if not os.path.ismount(location):
                self.location = self.home
        if not os.path.exists(self.location):
            os.makedirs(self.location)
        os.chdir(self.location)

        self.line = ""
        self.host = gethostname()
        self.single = single
        self.filetype = filetype
        self.task = taskname

        self.settings_cam()
        self.settings_rec()
        self.settings_cus()

        self.shuttertofps()

        if self.filetype == ".jpg":
            self.imgparams()

        self.record()



    def settings_cam(width = 3280, height = 2464, compensation = 0, shutterspeed = 8000,
                     iso = 200, brightness = 45, sharpness = 0, contrast = 10,
                     saturation = -100, quality = 11, fps = 24, zoom = (0.0,0.0,1.0,1.0),
                     rotation = 0):

        self.resolution = (int(width),int(height))
        self.compensation = int(compensation)
        self.shutterspeed = int(shutterspeed)
        self.iso = int(iso)
        self.brightness = int(brightness)
        self.sharpness = int(sharpness)
        self.contrast = int(contrast)
        self.saturation = int(saturation)
        self.quality = int(quality)
        self.fps = int(fps)
        self.zoom = literal_eval(str(zoom))
        self.rotation = int(rotation)

        lineprint("Camera settings stored..")


    def settings_rec(imgwait = 5.0, imgnr = 100, imgtime = 600, duration = 10, delay = 10):

        self.imgwait = int(imgwait)
        self.imgnr = int(imgnr)
        self.imgtime = int(imgtime)
        self.duration = int(duration+delay)

        lineprint("Recording settings stored..")


    def settings_cus(self):

        os.chdir(self.setupdir)

        self.zoom = loadyml("roifile.yml", value = self.zoom, add = False)
        self.brightness = loadyml("cusbright.yml", value = self.brightness, add = True)
        self.awb = loadyml("cusgains.yml", value = self.awb, add = False)
        self.rotation = loadyml("cusrotate.yml", value = self.rotation, add = False)

        lineprint("Custom settings for "+self.host+" loaded..")


    def setup_cam(self):

        self.camera = picamera.PiCamera()
        self.camera.framerate = self.fps
        self.camera.resolution = self.resolution
        self.camera.zoom = self.zoom
        self.camera.rotation = selfrotation
        self.camera.exposure_compensation = self.compensation

        time.sleep(1)

        self.camera.exposure_mode = 'off'
        self.camera.awb_mode = 'off'
        self.camera.awb_gains = self.awb
        self.camera.shutter_speed = self.shutterspeed
        self.camera.sharpness = self.sharpness
        self.camera.iso = self.iso
        self.camera.contrast = self.contrast
        self.camera.saturation = self.saturation
        self.camera.brightness = self.brightness

        lineprint("Camera started..")


    def namefile(self):

        """
            Provides a filename for the media recorded.

            Filenames include task, date, rpi name, and time.
            Images part of image sequence additionally contain
            a sequence number. e.g. test_180708_pi12_S01_100410

        """

        filename = self.task + "_" + daystamp + self.host

        if self.filetype == ".jpg" and not self.single:
            daystamp = "{timestamp:%Y%m%d}_"
            counter = "_im{counter:05d}"
            timestamp = "_{timestamp:%H%M%S}"
            self.filename = filename + counter + timestamp
        else:
            daystamp = time.strftime("%Y%m%d")
            timestamp = time.strftime("%H%M%S")
            self.filename = filename + timestamp


    def vidrecord(self, filename):

        lineprint("Recording "+filename)
        self.camera.start_recording(filename, quality = self.quality)
        self.camera.wait_recording(self.duration)
        self.camera.stop_recording()
        lineprint("Finished")


    def record(self):

        self.setup_cam()
        self.namefile()

        if self.rectype == "img":

            self.filename += self.filetype

            if self.single:

                self.camera.capture(self.filename, format = "jpeg", quality = self.quality)
                lineprint("Captured "+self.filename)

            else:

                timepoint = datetime.datetime.now()
                for i, img in enumerate(self.camera.capture_continuous(self.filename,
                                        format = "jpeg", quality = self.quality)):
                    if i < imgnr:
                        delay = self.imgwait - (datetime.datetime.now() - timepoint).total_seconds()
                        delay = min(0, delay)
                        lineprint("Captured "+img+", sleeping "+str(round(delay,2))+"s..")
                        time.sleep(delay)
                        timepoint = datetime.datetime.now()
                    else:
                        break

        else:

            if self.single:

                self.filename += self.filetype
                self.vidrecord(self.filename)

            else:

                for filename in camera.record_sequence(
                    self.filename+'S%02d' % i+self.filetype for i in range(9999)):
                    vidrecord(filename)
                    if raw_input("\nENTER for new session, E to exit: ") == 'e':
                        break

        self.camera.close()


if isscript:
    AnimRec = AnimRec()
    AnimRec.record()


# In[ ]:
