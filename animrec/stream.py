#! /usr/bin/env python
"""
Controlled media recording library for the Rasperry-Pi
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

# Import opencv and the Videostream package
import cv2
from animrec.videoin import VideoIn

def stream():
    # Open a video stream: cam = "rpi" will open the native raspberry
    # pi camera, while cam = 0 will open the natively attached camera or webcam
    vid = VideoIn(resolution=(1920, 1080)).start()

    # Run videostream until user presses ESC
    while True:

        # Get frame from the videostream
        frame = vid.read()

        # Show the frame
        cv2.imshow('window', frame)
        k = cv2.waitKey(1) & 0xFF

        # Change to/from fullscreen
        if k == ord("f"):
            winval = abs(1 - cv2.getWindowProperty('window', 0))
            cv2.setWindowProperty("window", 0, winval)

        # Exit
        if k == 27:
            break

    # Stop the videostream and close the video window
    vid.stop()
    cv2.destroyAllWindows()
    cv2.waitKey(1)

if __name__ == "__main__":
      stream()
