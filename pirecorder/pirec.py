#! /usr/bin/env python
"""
Copyright (c) 2018 - 2019 Jolle Jolles <j.w.jolles@gmail.com>

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

from .pirecorder import Recorder

def pirec():

    # Initiate the recorder instance
    pirec = Recorder()

    # # General config
    # pirec.set_config(recdir = "", label = "test", rectype = "vid",
    #               brightness = 45, contrast = 10, saturation = -100, iso = 200,
    #               sharpness = 0, compensation = 0, shutterspeed = 8000,
    #               quality = 11, brighttune = 0)

    # # Config for videos
    # pirec.set_config(viddims = (1640, 1232), vidfps = 24, vidduration = 5, viddelay = 2)

    # # Config for images
    # pirec.set_config(imgdims = (3280, 2464), imgfps = 1, imgwait = 5.0, imgnr = 100,
    #               imgtime = 600)

    # # Draw the region of interest
    # pirec.set_roi()

    # # Dynamically set the Gains
    # pirec.set_gains()

    # Run record function
    pirec.record()

if __name__ == "__main__":
      pirec()
