#! /usr/bin/env python
#
# Controlled media recording library for the Rasperry-Pi
# Copyright (c) 2019 Jolle Jolles <j.w.jolles@gmail.com>
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

from threading import Thread
import cv2
import time
import animlab.imutils as alimu

class VideoIn:
    def __init__(self, cam=0, resolution=(1920,1080), framerate=32,
                 zoom = (0,0,1,1)):

        """ Opens a video stream from native camera, webcam or rpi camera """

        self.cam = cam

        if self.cam == "rpi":
            from picamera.array import PiRGBArray
            from picamera import PiCamera
            self.camera = Picamera()
            self.camera.resolution = resolution
            self.camera.framerate = framerate
            self.camera.zoom = zoom
            self.rawCapture = PiRGBArray(self.camera, size=resolution)
            self.stream = self.camera.capture_continuous(self.rawCapture,
                          format="bgr", use_video_port=True)
            time.sleep(1)
            self.frame = None

        else:
            self.stream = cv2.VideoCapture(self.cam)
            self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
            self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
            (self.grabbed, self.frame) = self.stream.read()
            if zoom != (0,0,1,1):
                ((x1,y1),(x2,y2)) = alimu.zoom_to_roi(zoom, self.resolution)
                self.frame = self.frame[y1:y2, x1:x2]

        if not self.stream.isOpened():
            raise Exception("Could not open video device")

        self.stopped = False


    def start(self):
        Thread(target=self.update, args=()).start()
        return self


    def update(self):
        if self.cam == "rpi":
            for f in self.stream:
                self.frame = f.array
                self.rawCapture.truncate(0)
                if self.stopped:
                    self.stream.close()
                    self.rawCapture.close()
                    self.camera.close()
                    return
        else:
            while True:
                if self.stopped:
                    return
                (self.grabbed, self.frame) = self.stream.read()


    def read(self):
        return self.frame


    def img(self):
        if self.cam == "rpi":
            self.camera.capture(".temp.jpg")
            return cv2.imread(".temp.jpg",0)
        else:
            return self.frame


    def stop(self):
        self.stopped = True