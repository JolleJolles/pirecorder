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
import picamera
import picamera.array

import animlab.imutils as alimu


class showcam:

    def __init__(self, res = (640, 480), cross = False):

        """
        Videostream of raspberry pi with cross to accurately position the camera
        """

        self.cross = cross
        self.stream = True
        self.camera = picamera.PiCamera()
        res = (min(820, res[0]), min(616, res[1]))
        self.res = (alimu.closenr(res[0],32), alimu.closenr(res[1], 16))
        self.camera.framerate = 8
        self.camera.resolution = self.res
        self.camera.zoom = (0,0,1,1)
        self.raw = picamera.array.PiRGBArray(self.camera)

        time.sleep(1)

        cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
        self.m = alimu.mouse_events()
        cv2.setMouseCallback('Image', self.m.draw)

        self.drawer()


    def drawstream(self):
        print("Streaming video")

        for frame in self.camera.capture_continuous(self.raw, format="bgr", use_video_port=True):
            self.img = frame.array

            if self.cross:
                alimu.draw_cross(self.img, self.camera.resolution)

            cv2.imshow("Image", self.img)
            cv2.resizeWindow("Image", self.camera.resolution[0], self.camera.resolution[1])

            self.k = cv2.waitKey(1) & 0xFF
            if self.k == ord('c'):
                self.cross = not self.cross

            if self.k == ord('f'):
                winval = abs(1 - cv2.getWindowProperty('Image', 0))
                cv2.setWindowProperty("Image", 0, winval)

            self.raw.truncate(0)

            if self.k == ord("d"):
                self.stream = False
                break

            if self.k == 27:
                break


    def drawframe(self):
        print("Select roi for zoom")

        self.imgbak = self.img.copy()
        while True:
            self.img = self.imgbak.copy()
            alimu.draw_crosshair(self.img, self.m.pointer)
            alimu.draw_rectangle(self.img, self.m.pointer, self.m.rect, self.m.drawing)
            cv2.imshow("Image", self.img)

            self.k = cv2.waitKey(1) & 0xFF
            if self.k == ord('f'):
                winval = abs(1 - cv2.getWindowProperty('Image', 0))
                cv2.setWindowProperty("Image", 0, winval)

            if self.k == ord('z'):
                if self.m.rect:
                    if len(self.m.rect) == 2:
                        print("Creating zoomed image")
                        x = min(self.m.rect[0][0], self.m.rect[1][0])
                        y = min(self.m.rect[0][1], self.m.rect[1][1])
                        w = abs(self.m.rect[1][0] - self.m.rect[0][0])
                        h = abs(self.m.rect[1][1] - self.m.rect[0][1])

                        xp = x / float(self.res[0])
                        yp = y / float(self.res[1])
                        wp = w / float(self.res[0])
                        hp = h / float(self.res[1])

                        maxres = (2592, 1944)
                        self.camera.resolution = maxres
                        self.camera.zoom = (xp,yp,wp,hp)
                        self.camera.capture("testimg.jpg")
                        img = cv2.imread("testimg.jpg",0)
                        cv2.namedWindow("Zoomed", cv2.WINDOW_NORMAL)

                        while True:
                            cv2.imshow("Zoomed", img)
                            xwin, ywin = int(hp*maxres[0]), int(wp*maxres[1])
                            cv2.resizeWindow("Zoomed", xwin, ywin)

                            self.k = cv2.waitKey(1) & 0xFF
                            if self.k == ord('f'):
                                winval = abs(1 - cv2.getWindowProperty('Zoomed', 0))
                                cv2.setWindowProperty("Zoomed", 0, winval)

                            if self.k == 27:
                                self.camera.resolution = self.res
                                self.camera.zoom = (0,0,1,1)
                                self.stream = True
                                cv2.destroyWindow('Zoomed')
                                cv2.waitKey(1)
                                self.k = 255
                                break

            if self.k == 27:
                self.m.rect = ()
                self.k = 255
                break


    def drawer(self):
        while True:
            if self.stream:
                self.drawstream()
            if not self.stream:
                self.drawframe()
            if self.k == 27:
                break

        self.camera.close()
        cv2.destroyWindow('Image')
        for i in range(5):
            cv2.waitKey(1)
