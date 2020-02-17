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

import cv2
import numpy as np

def setgains(attempts = 100, step = 0.05, startgains = (1,2),
             zoom = (0,0,1,1), auto = True):

    """
    Find the best gains for the raspberry pi camera

    Parameters
    ----------
    attempts : int, default = 100
        Number of times gains should be shifted when in automatic mode
    step : float, detault = 0.05
        The stepsize between the different gains
    startgains : tuple, default = (1,2)
        The starting gains
    zoom : tuple, default = (0,0,1,1)
        The camera zoom (x,y,w,h)
    auto : bool, default = True
        If gains should be determined automatically or manually

    Returns
    -------
    (rg,bg) : A tuple of red and blue camera gains
    """

    #load picamera module in-function so pirecorder is installable on all OS
    import picamera
    import picamera.array

    camera = picamera.PiCamera()
    height, width = (480, 640)
    camera.resolution = (width, height)
    camera.zoom = zoom
    camera.awb_mode = 'off'
    rg, bg = startgains
    camera.awb_gains = (rg, bg)

    if auto:
        with picamera.array.PiRGBArray(camera, size=(128, 72)) as output:
            for i in range(attempts):
                camera.capture(output, format="rgb", resize=(128, 80), use_video_port=True)
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
                camera.awb_gains = (rg, bg)
                output.seek(0)
                output.truncate()
    else:
        cv2.namedWindow("Image")
        while True:
            image = np.empty((height * width * 3,), dtype=np.uint8)
            camera.capture(image, "bgr")
            image = image.reshape((height, width, 3))
            cv2.imshow("Image", image)
            print("R:%5.2f, B:%5.2f" % (rg, bg))
            camera.awb_gains = (rg, bg)

            k = cv2.waitKey(1) & 0xFF
            if k == ord("q"):
                rg = round(max(rg-step,0.5),2)
            if k == ord("w"):
                rg = round(min(rg+step,2.5),2)
            if k == ord("e"):
                bg = round(max(bg-step,0.5),2)
            if k == ord("r"):
                bg = round(min(bg+step,2.5),2)
            if k == ord("s"):
                print("User exited..")
                break
            if k == 27:
                rg, bg = startgains
                print("User escaped..")
                break

        cv2.waitKey(1)
        cv2.destroyAllWindows()

    camera.close()

    return (rg, bg)


if __name__ == "__main__":
      setgains()
