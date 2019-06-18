#! /usr/bin/env python
#
# Controlled media recording library for the Rasperry-Pi
# Copyright (c) 2015 - 2019 Jolle Jolles <j.w.jolles@gmail.com>
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

import cv2
import time
import numpy as np

import animlab.utils as alu
import animlab.imutils as alimu

from .videoin import VideoIn

class Calibrate:

    def __init__(self, stream = True, cam = "rpi", framerate=8,
                 resolution=(640, 480), cross = False):

        """
        Opens a video stream with user interface for calibrating the camera
        """

        self.framerate = framerate
        self.resolution = (min(820, resolution[0]), min(616, resolution[1]))
        self.cross = cross

        self.vid = VideoIn(framerate=self.framerate,
                           resolution=self.resolution).start()
        self.img = self.vid.read()

        cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
        self.m = alimu.mouse_events()
        cv2.setMouseCallback('Image', self.m.draw)

        self.stream = stream
        self.roi = False

        if self.stream:
            self.drawer()


    def draw_stream(self):
        alu.lineprint("Streaming video..")

        while True:
            self.img = self.vid.read()

            if self.cross:
                animlab.imutils.draw_cross(self.img, self.resolution)

            cv2.imshow("Image", self.img)
            cv2.resizeWindow("Image", self.resolution[0], self.resolution[1])

            self.k = cv2.waitKey(1) & 0xFF
            if self.k == ord("c"):
                self.cross = not self.cross

            if self.k == ord("f"):
                winval = abs(1 - cv2.getWindowProperty('Image', 0))
                cv2.setWindowProperty("Image", 0, winval)

            if self.k == ord("d"):
                self.stream = False

            if self.k in ["d",27]:
                self.vid.stop()
                break


    def draw_frame(self):
        alu.lineprint("Select roi..")
        self.imgbak = self.img.copy()

        while True:
            self.img = self.imgbak.copy()
            alimu.draw_crosshair(self.img, self.m.pointer)
            alimu.draw_rectangle(self.img, self.m.pointer,
                                           self.m.rect, self.m.drawing)
            cv2.imshow("Image", self.img)

            self.k = cv2.waitKey(1) & 0xFF
            if self.k == ord("f"):
                winval = abs(1 - cv2.getWindowProperty('Image', 0))
                cv2.setWindowProperty("Image", 0, winval)

            if self.k == ord("s"):
                if self.m.rect and len(self.m.rect) == 2:
                    self.roi = alimu.get_reccoords(self.m.rect)
                    alu.lineprint("roi coordinates " + str(roi) + " stored..")
                    return self.roi
                else:
                    alu.lineprint("Nothing to store..")

            if self.k == ord("z"):
                if self.m.rect and len(self.m.rect) == 2:
                    alu.lineprint("Creating zoomed image..")
                    rect = alimu.get_reccoords(self.m.rect)
                    zoom = alimu.roi_to_zoom(rect, self.resolution)
                    maxres = (2592, 1944)
                    img = VideoIn(resolution=maxres, zoom = (0,0,1,1)).img()
                    cv2.namedWindow("Zoomed", cv2.WINDOW_NORMAL)

                    while True:
                        cv2.imshow("Zoomed", img)
                        xwin, ywin = int(hp*maxres[0]), int(wp*maxres[1])
                        cv2.resizeWindow("Zoomed", xwin, ywin)

                        self.k = cv2.waitKey(1) & 0xFF
                        if self.k == ord("f"):
                            winval = abs(1 - cv2.getWindowProperty('Zoomed', 0))
                            cv2.setWindowProperty("Zoomed", 0, winval)

                        if self.k == 27:
                            cv2.destroyWindow("Zoomed")
                            cv2.waitKey(1)
                            self.vid = VideoIn(resolution=self.resolution,
                                             zoom = (0,0,1,1)).start()
                            self.stream = True
                            self.k = 255
                            break

            if self.k == 27:
                self.m.rect = ()
                self.k = 255
                break


    def drawer(self):
        while True:
            if self.stream:
                self.draw_stream()
            if not self.stream:
                self.draw_frame()
            if self.k == 27:
                cv2.waitKey(1)
                cv2.destroyWindow('Image')
                break
