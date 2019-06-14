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

import picamera
import picamera.array
import time
import cv2
import animlab.imutils as alimu


def showcam(res = (832,624), zoom = (0,0,1,1), compensation = 0,
            cross = True):

    """
    Videostream of raspberry pi with cross to accurately position the camera
    """

    cam = picamera.PiCamera()
    cam.framerate = 32
    cam.resolution = res
    cam.zoom = zoom
    cam.exposure_compensation = compensation

    raw = picamera.array.PiRGBArray(cam)

    time.sleep(0.1)

    for frame in cam.capture_continuous(raw, format="bgr", use_video_port=True):

        img = frame.array
        if cross:
            alimu.draw_cross(img, res)

        cv2.imshow("Image", img)
        cv2.moveWindow('Image', 0,0)
        k = cv2.waitKey(1) & 0xFF

        raw.truncate(0)

        if k == 27:
            break

    cam.close()
    cv2.destroyWindow('Image')
    cv2.waitKey(1)
    cv2.waitKey(1)
    cv2.waitKey(1)
