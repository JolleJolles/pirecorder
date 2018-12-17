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
#
# The setgains function was written based on code provided by Dave Jones of the
# picamera library on stackoverflow.

import picamera
import picamera.array
import numpy as np
import yaml
import os

def setgains(resolution = (1280, 720), brightness = 45, rg = 0.5, bg = 0.5,
             attempts = 100):

    ''' Automatically find gains for Raspberry-Pi camera'''

    setupdir = "/home/pi/setup/"
    brightfile = setupdir + "cusbright.yml"
    gainsfile = setupdir + "cusgains.yml"
    if not os.path.exists(setupdir):
        os.makedirs(self.setupdir)
        lineprint("Setup folder created (" + self.setupdir + ")")

    cam = picamera.PiCamera()
    cam.resolution = resolution
    cam.awb_mode = 'off'

    if not os.path.exists(brightfile):
        cam.brightness = brightness
    else:
        with open(brightfile) as f:
            cam.brightness += yaml.load(f)

    cam.awb_gains = (rg, bg)
    with picamera.array.PiRGBArray(cam, size=(128, 72)) as output:

        for i in range(attempts):

            # Capture a tiny resized image in RGB format, and extract the
            # average R, G, and B values
            cam.capture(output, format='rgb', resize=(128, 80), use_video_port=True)
            r, g, b = (np.mean(output.array[..., i]) for i in range(3))
            print('R:%5.2f, B:%5.2f = (%5.2f, %5.2f, %5.2f)' % (rg, bg, r, g, b))

            # Adjust R and B relative to G, but only if they're significantly
            # different (delta +/- 2)
            if abs(r - g) > 2:
                if r > g:
                    rg -= 0.05
                else:
                    rg += 0.05
            if abs(b - g) > 1:
                if b > g:
                    bg -= 0.05
                else:
                    bg += 0.05

            cam.awb_gains = (rg, bg)
            output.seek(0)
            output.truncate()

    gains = str((round(rg,2), round(bg,2)))
    with open(gainsfile, 'w') as f:
        yaml.safe_dump(gains, f, default_flow_style=False)
    print("Gains: " + gains + "stored..!")
