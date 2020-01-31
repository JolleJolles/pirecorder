#! /usr/bin/env python
"""
Copyright (c) 2019 Jolle Jolles <j.w.jolles@gmail.com>

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

import cv2
import time
import argparse
import numpy as np

from pythutils.sysutils import lineprint
from pythutils.mediautils import checkroi, roi_to_zoom
import pythutils.drawutils as draw

from .videoin import VideoIn
from .__version__ import __version__

class Calibrate:

    def __init__(self, system="auto", framerate=8, vidsize=0.2, internal=False,
                 rotation = 0):

        """Opens a video stream with user interface to calibrate the camera"""

        if internal:
            lineprint("Running calibrate function.. ")

        self.system = system
        self.framerate = framerate
        self.vidsize = vidsize
        self.rotation = rotation
        self.cross = False
        self.stream = True
        self.exit = False
        self.roi = False
        self.fullscreen = False

        cv2.namedWindow("Image", cv2.WND_PROP_FULLSCREEN)
        self.m = draw.mouse_events()
        cv2.setMouseCallback('Image', self.m.draw)
        time.sleep(1)

        self.drawer()


    def draw_stream(self):

        lineprint("Streaming video..")

        self.vid = VideoIn(system=self.system, framerate=self.framerate,
                           vidsize=self.vidsize, rotation=self.rotation)
        self.vid.start()

        while True:
            self.img = self.vid.read()
            if self.cross:
                draw.draw_cross(self.img, pt2 = self.vid.res)
            cv2.imshow("Image", self.img)

            k = cv2.waitKey(1) & 0xFF
            if k == ord("c"):
                self.cross = not self.cross

            if k == ord("f"):
                self.fullscreen = not self.fullscreen
                if self.fullscreen:
                    cv2.setWindowProperty("Image",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
                else:
                    cv2.setWindowProperty("Image",cv2.WND_PROP_AUTOSIZE, cv2.WINDOW_NORMAL)
                    cv2.resizeWindow("Image", self.vid.res[0], self.vid.res[1])

            if k == ord("d"):
                self.stream = False
                break
            if k == 27:
                lineprint("User exited..")
                self.exit = True
                break

        self.vid.stop()


    def draw_frame(self):

        lineprint("Selecting roi..")
        self.imgbak = self.img.copy()

        while True:
            img = self.imgbak.copy()
            if len(self.m.pointer) > 0:
                draw.draw_crosshair(img, self.m.pointer)
            if self.m.rect != ():
                draw.draw_rectangle(img, self.m.pointer, self.m.rect, self.m.drawing)
            cv2.imshow("Image", img)

            k = cv2.waitKey(1) & 0xFF
            if k == ord("s"):
                if self.m.rect and len(self.m.rect) == 2:
                    self.m.rect = checkroi(self.m.rect, self.vid.res)
                    self.roi = roi_to_zoom(self.m.rect, self.vid.res)
                    lineprint("roi "+str(self.roi)+" stored..")
                    break
                else:
                    lineprint("Nothing to store..")

            if k == ord("e"):
                self.roi = False
                lineprint("new roi erased..")

            if k == ord("z"):
                if self.m.rect and len(self.m.rect) == 2:
                    lineprint("Creating zoomed image..")
                    self.vid2 = VideoIn(system=self.system, vidsize=self.vidsize,
                                        crop=self.m.rect, rotation=self.rotation)
                    zimg = self.vid2.img()
                    cv2.namedWindow("Zoomed", cv2.WINDOW_NORMAL)
                    while True:
                        cv2.imshow("Zoomed", zimg)
                        cv2.resizeWindow("Zoomed", self.vid2.roiw, self.vid2.roih)
                        k = cv2.waitKey(1) & 0xFF
                        if k == 27:
                            break

                    k = 255
                    cv2.destroyWindow("Zoomed")

            if k == 27:
                self.stream = True
                self.m.rect = ()
                break


    def drawer(self):

        while True:
            if self.stream:
                self.draw_stream()
            if not self.stream:
                self.draw_frame()
            if self.exit:
                cv2.waitKey(1)
                cv2.destroyAllWindows()
                for i in range(5):
                    cv2.waitKey(1)
                break
