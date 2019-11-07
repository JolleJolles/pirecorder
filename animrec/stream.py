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

import cv2

from animrec.videoin import VideoIn

def stream():

    """
    Opens a video stream of the rpi camera. With keypress 'f' the user can make
    the videostream fullscreen and with the 'ESC' key the window is closed.
    """

    vid = VideoIn(vidsize=0.25).start()
    while True:
        frame = vid.read()
        cv2.imshow('window', frame)
        k = cv2.waitKey(1) & 0xFF
        if k == ord("f"):
            winval = abs(1 - cv2.getWindowProperty('window', 0))
            cv2.setWindowProperty("window", 0, winval)
        if k == 27:
            break

    vid.stop()
    cv2.destroyAllWindows()
    cv2.waitKey(1)

if __name__ == "__main__":
      stream()
