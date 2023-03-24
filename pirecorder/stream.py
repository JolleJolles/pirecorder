#! /usr/bin/env python
"""
Copyright (c) 2019 - 2023 Jolle Jolles <j.w.jolles@gmail.com>

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

import os
import cv2
import time
import argparse
import numpy as np

from pythutils.sysutils import lineprint
from pythutils.mediautils import checkroi, roi_to_zoom, imgresize
import pythutils.drawutils as draw

from .videoin import VideoIn
from .__version__ import __version__

class Stream:

    def __init__(self, system = "auto", framerate = 8, vidsize = 0.2,
                 rotation = 0, internal = False, maxres = None,
                 imgoverlay = None):

        """
        Opens a video stream with user interface to help position and
        adjust the camera

        parameters
        -----------
        system : str, default = "auto"
            If the system should be automatically determined. Should detect if
            the computer is a raspberry pi or not. If this somehow fails, set
            to "rpi" manually.
        framerate : int, default = 8
            The framerate of the displayed video stream. Lower framerates take
            longer to start up. When using an image overlay, maximum possible
            framerate is 5, to avoid getting shutter effects
        vidsize : float, default = 0.2
            The relative size of the video window to the maximum resolution of
            the raspberry pi camera type.
        rotation : int, default = 180
            If the camera should be rotated or not. 0 and 180 are valid values.
        maxres : str or tuple, default = "v2"
            The maximum potential resolution of the camera used. Either provide
            a tuple of the max resolution, or use "v1.5", "v2" (default), or
            "hq" to get the maximum resolution associated with the official cameras
            directly.
        imgoverlay : str, default = None
            The path to an image that will be overlaid on the video stream. This
            can be helpful for accurate positioning of the camera in line with
            previous recordings or setups.

        interface
        -----------
        This interactive module stores mouse position and clicks and responds to
        the following keypresses:
        f-key : display the stream fullscreen/display the stream in a window
        c-key : display/hide a diagonal cross across the screen
        s-key : save the coordinates of the rectangular area when drawn
        e-key : erase the rectangular area when drawn
        z-key : show a zoomed-in section of the video inside the rectangular
            area in maximum resolution
        n-key : refresh the zoom-in image
        o-key : if the potential overlay image should be shown or not
        [- and ]-keys : decrease or increase the relative opacity of the
            potential overlay image with 5%
        esc-key : exit the the zoom window; exit the calibrate function
        """

        self.internal = internal
        if self.internal:
            lineprint("Running stream function.. ")

        self.system = system
        self.framerate = framerate
        self.vidsize = vidsize
        self.rotation = rotation
        self.maxres = maxres

        if imgoverlay == None:
            self.overlay = False
            self.waitms = 1
        else:
            if os.path.isfile(imgoverlay):
                self.overlay = True
                self.overlayimg = cv2.imread(imgoverlay)
                self.alpha = 0.5
                self.waitms = 200
                self.framerate = min(self.framerate, 5)
            else:
                print("Image file could not be loaded..")

        self.cross = False
        self.stream = True
        self.exit = False
        self.roi = False
        self.fullscreen = False
        self.tempcol = draw.namedcols("orange")
        self.col = draw.namedcols("red")

        cv2.namedWindow("Image", cv2.WND_PROP_FULLSCREEN)
        self.m = draw.mouse_events()
        cv2.setMouseCallback('Image', self.m.draw)
        time.sleep(1)

        self.drawer()


    def draw_stream(self):

        lineprint("Streaming video..")

        self.vid = VideoIn(system=self.system, framerate=self.framerate,
                           vidsize=self.vidsize, rotation=self.rotation,
                           maxres=self.maxres)
        self.vid.start()

        if self.overlay:
            h, w, _ = self.vid.read().shape
            self.overlayimg = imgresize(self.overlayimg, resize=1, dims=(w,h))

        while True:
            self.img = self.vid.read()

            if self.overlay:
                overlay = self.img.copy()
                overlay[0:h,0:w] = self.overlayimg
                cv2.addWeighted(overlay, self.alpha, self.img, 1-self.alpha, 0, self.img)
            if self.cross:
                draw.draw_cross(self.img, pt2 = self.vid.res)
            if self.m.twoPoint is not None:
                draw.draw_crosshair(self.img, self.m.pos)
            if self.m.posDown is not None:
                cv2.rectangle(self.img, self.m.posDown, self.m.pos,
                              self.tempcol, 2)
            if self.m.posUp is not None:
                cv2.rectangle(self.img, self.m.pts[-1], self.m.posUp,
                              self.col, 2)
            cv2.imshow("Image", self.img)

            k = cv2.waitKey(self.waitms) & 0xFF
            if k == ord("o"):
                self.overlay = not self.overlay
            if k == ord("c"):
                self.cross = not self.cross
            if k == ord("f"):
                self.fullscreen = not self.fullscreen
                if self.fullscreen:
                    cv2.setWindowProperty("Image", cv2.WND_PROP_FULLSCREEN,
                                          cv2.WINDOW_FULLSCREEN)
                else:
                    cv2.setWindowProperty("Image", cv2.WND_PROP_AUTOSIZE,
                                          cv2.WINDOW_NORMAL)
                    cv2.resizeWindow("Image", self.vid.res[0], self.vid.res[1])
            if k == ord("s"):
                if self.m.twoPoint is not None:
                    self.m.twoPoint = checkroi(self.m.twoPoint, self.vid.res)
                    self.roi = roi_to_zoom(self.m.twoPoint, self.vid.res)
                    if self.internal is True:
                        lineprint("roi "+str(self.roi)+" stored..")
                    else:
                        lineprint("roi: "+str(self.roi))
                else:
                    lineprint("Nothing selected..")
            if k == ord("e"):
                self.m.posUp = None
                self.roi = False
                lineprint("roi data erased..")
            if k == ord("z"):
                if self.m.twoPoint is not None:
                    lineprint("Creating zoomed image..")
                    self.stream = False
                    break
            if self.overlay and k == ord("["):
                self.alpha = max(self.alpha-0.05, 0)
            if self.overlay and k == ord("]"):
                self.alpha = min(self.alpha+0.05, 1)
            if k == 27:
                lineprint("User exited..")
                self.exit = True
                break

        self.vid.stop()
        time.sleep(1)


    def drawer(self):
        while True:
            if self.stream:
                self.draw_stream()

            if not self.stream:
                cv2.namedWindow("Zoomed", cv2.WINDOW_NORMAL)
                cv2.setWindowProperty("Zoomed", cv2.WND_PROP_AUTOSIZE,
                                      cv2.WINDOW_NORMAL)
                while True:
                    self.vid2 = VideoIn(system=self.system, vidsize=self.vidsize,
                                        crop=self.m.twoPoint, rotation=self.rotation,
                                        maxres=self.maxres)
                    zimg = self.vid2.img()
                    cv2.imshow("Zoomed", zimg)
                    cv2.resizeWindow("Zoomed", self.vid2.roiw, self.vid2.roih)
                    k = cv2.waitKey(0) & 0xFF
                    if k == 27:
                        break
                k = 255
                cv2.destroyWindow("Zoomed")
                self.stream = True

            if self.exit:
                cv2.waitKey(1)
                cv2.destroyAllWindows()
                for i in range(5):
                    cv2.waitKey(1)
                break

def strm():

    """To run the stream function from the command line"""

    parser = argparse.ArgumentParser(prog="Stream",
             description=Stream.__doc__,
             formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("-f", "--framerate", default=8, type=int, metavar="")
    parser.add_argument("-v", "--vidsize", default=0.2, type=float, metavar="")
    parser.add_argument("-r", "--rotation", default=0, type=int, metavar="")
    parser.add_argument("-o", "--imgoverlay", default=None, metavar="")
    parser.add_argument("-m", "--maxres", default="v2", metavar="")
    parser.add_argument("-c", "--configfile", default=None,
                        action="store", help="pirecorder configuration file")

    args = parser.parse_args()
    if args.configfile is None:
        Stream(framerate = args.framerate, vidsize = args.vidsize,
               rotation = args.rotation, maxres = args.maxres,
               imgoverlay = args.imgoverlay)
    else:
        from pirecorder import PiRecorder
        rec = PiRecorder(args.configfile)
        rec.settings(internal = True)
        rec.stream()
