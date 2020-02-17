#! /usr/bin/env python
"""
Copyright (c) 2015 - 2019 Jolle Jolles <j.w.jolles@gmail.com>

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

from .videoin import VideoIn
from pythutils.mediautils import add_transimg, imgresize

def stream(rotation = 0):

    """
    Opens a video stream of the rpi camera. With keypress 'f' the user can make
    the videostream fullscreen and with the 'ESC' key the window is closed.
    """

    fullscreen = False
    vid = VideoIn(vidsize=0.25, rotation=rotation).start()
    cv2.namedWindow("Stream", cv2.WND_PROP_FULLSCREEN)
    while True:
        frame = vid.read()
        cv2.imshow('Stream', frame)
        k = cv2.waitKey(1) & 0xFF
        if k == ord("f"):
            fullscreen = not fullscreen
            if fullscreen:
                cv2.setWindowProperty("Stream", cv2.WND_PROP_FULLSCREEN,
                                      cv2.WINDOW_FULLSCREEN)
            else:
                cv2.setWindowProperty("Stream",cv2.WND_PROP_AUTOSIZE,
                                               cv2.WINDOW_NORMAL)
                cv2.resizeWindow("Stream", vid.res[0], vid.res[1])

        if k == 27:
            break

    vid.stop()
    cv2.destroyAllWindows()
    cv2.waitKey(1)


def overlay_stream(imagefile = "", alpha = 0.5, rotation = 0):

    # Check if image file loads
    assert os.path.isfile(imagefile), "Image file could not be loaded.."

    # Start videostream
    fullscreen = False
    vid = VideoIn(vidsize=1, rotation=rotation).start()
    frame = vid.read()
    overlay = frame.copy()
    h, w, _ = frame.shape
    cv2.namedWindow("Stream", cv2.WND_PROP_FULLSCREEN)

    # Load and resize the image to fit
    photo = cv2.imread(imagefile)
    photo = imgresize(photo, resize = 1, dims = (w,h))

    # Draw photo on overlay
    overlay[0:h,0:w] = photo

    # Start the loop
    c = 0
    vid.stop()
    vid = VideoIn(vidsize=1, rotation=rotation).start()
    while True:

        c += 1
        print(c)
        # Extract the frame
        frame = vid.read()
        output = frame.copy()

        # Draw overlay semi-transparent on frame
        # cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)

        # Draw in black and white
        output = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)

        # Show the stream
        cv2.imshow("Stream", output)
        k = cv2.waitKey(1) & 0xFF
        if k == ord("["):
            alpha = max(alpha-0.05, 0)
        if k == ord("]"):
            alpha = min(alpha+0.05, 1)
        if k == ord("f"):
            fullscreen = not fullscreen
            if fullscreen:
                cv2.setWindowProperty("Stream", cv2.WND_PROP_FULLSCREEN,
                                      cv2.WINDOW_FULLSCREEN)
            else:
                cv2.setWindowProperty("Stream",cv2.WND_PROP_AUTOSIZE,
                                               cv2.WINDOW_NORMAL)
                cv2.resizeWindow("Stream", vid.res[0], vid.res[1])

        if k == 27:
            break

    vid.stop()
    cv2.destroyAllWindows()
    cv2.waitKey(1)


if __name__ == "__main__":
      stream()
