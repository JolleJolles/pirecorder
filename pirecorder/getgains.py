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

This function was partly based on code provided by Dave Jones in a
reply on a question posted on stackoverflow: https://bit.ly/2V49f48
"""

from __future__ import print_function

import numpy as np

def getgains(attempts = 100, step = 0.05, startgains = (0.5, 0.5)):

    """Automatically finds the best gains for the raspberry pi camera"""

    # Load picamera module here so pirecorder is installable on non-rpi OS
    import picamera
    import picamera.array

    cam = picamera.PiCamera()
    cam.resolution = (1280, 720)
    cam.awb_mode = 'off'
    rg, bg = startgains
    cam.awb_gains = (rg, bg)

    with picamera.array.PiRGBArray(cam, size=(128, 72)) as output:

        for i in range(attempts):

            cam.capture(output, format="rgb", resize=(128, 80), use_video_port=True)
            r, g, b = (np.mean(output.array[..., i]) for i in range(3))
            print("R:%5.2f, B:%5.2f = (%5.2f, %5.2f, %5.2f)" % (rg, bg, r, g, b))

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

            cam.awb_gains = (rg, bg)
            output.seek(0)
            output.truncate()

        cam.close()

    return (rg, bg)


if __name__ == "__main__":
      getgains()
