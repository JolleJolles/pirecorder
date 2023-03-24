#! /usr/bin/env python
"""
Copyright (c) 2020 - 2023 Jolle Jolles <j.w.jolles@gmail.com>

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
import time
import shutil
from pythutils.fileutils import listfiles

# import the package
print("TEST: import pirecorder package")
import pirecorder
time.sleep(1)
print("DONE..\n")

# Initialise PiRecorder class with default configfile
## Sets up the pirecorder directory, creates configfile, stores settings
print("TEST: initialise PiRecorder class")
rec = pirecorder.PiRecorder()
time.sleep(1)
print("DONE..\n")

# Initialise PiRecorder with custom configuration file
print("TEST: initialise PiRecorder class with custom configuration file")
rec = pirecorder.PiRecorder(configfile = "test.conf")
time.sleep(1)
print("DONE..\n")

# Change configuration settings and store automatically
print("TEST: setting all custom configuration settings")
rec.settings(recdir = "TESTS", label = "TEST", rectype = "img", subdirs = False,
             rotation = 0, brighttune = 0, gains = (1.0, 2.5), brightness = 45,
             contrast = 20, saturation = -100, iso = 200, sharpness = 50,
             compensation = 0, shutterspeed = 10000, imgdims = (3280,2464),
             viddims = (1640,1232), imgfps = 1, vidfps = 24, imgwait = 1.0,
             imgnr = 60, imgtime = 60, imgquality = 50, vidduration = 10,
             viddelay = 0, vidquality = 11)
time.sleep(1)
print("DONE..\n")

# Automatically get the configuration Settings
print("TEST: running auto configuration (shutterspeed and whitebalance)")
print("Before: shutterspeed = " + str(rec.config.cam.shutterspeed) + "; gains = " + str(rec.config.cus.gains))
rec.autoconfig()
time.sleep(1)
print("DONE..\n")

# Test recording 1: a single image
print("TEST: recording a single image")
rec.record()
print("DONE..\n")

# Test recording 2: a sequence of 10 images, 5s apart
print("TEST: recording a sequence of 10 images, 5s apart")
rec.settings(rectype = "imgseq", imgnr = 10, imgtime = 60, imgwait = 5,
             subdirs = True)
rec.record()
print("DONE..\n")

# Test recording 3: a single 10s video
print("TEST: recording a 10s video")
rec.settings(rectype = "vid", vidduration = 10, viddelay = 0, subdirs = False)
rec.record()
print("DONE..\n")

# Test recording 4: a sequence of videos
print("TEST: recording a sequence of videos")
rec.settings(rectype = "vidseq")
rec.record()
time.sleep(1)
print("DONE..\n")

# Run video stream
print("TEST: run video stream")
print("Function records mouse clicks and movements and responds to keypresses:")
print("f-key: Display the stream fullscreen/display the stream in a window")
print("c-key: Display/hide a diagonal cross across the screen")
print("s-key: Save the coordinates of the rectangular area when drawn")
print("e-key: Erase the rectangular area when drawn")
print("z-key: Show a zoomed-in section of the video inside the rectangular area in maximum resolution")
print("n-key: Refresh the zoom-in image")
print("o-key: If the potential overlay image should be shown or not")
print("[- and ]-keys: Decrease or increase the relative opacity of the potential overlay image with 5%")
print("esc-key: Exit the the zoom window as well as the calibrate function completely")
pirecorder.Stream()
time.sleep(1)
print("DONE..\n")

# Run interactive camera configuration
print("TEST: run interactive camera configuration")
print("Parameters can be set dynamically using the UI trackbars")
pirecorder.Camconfig()
time.sleep(1)
print("DONE..\n")

# Schedule recording tests
print("TEST: Scheduling recordings - test a timeplan")
rec.schedule(timeplan = "*/10 */2 10-15 * *", test = True)
time.sleep(1)
print("DONE..\n")

print("TEST: Scheduling recordings - plan a recording job")
print("record an video of 10s every minute")
rec.settings(rectype = "vid", vidduration = 10)
rec.schedule(timeplan = "* * * * *", jobname = "rec1")
time.sleep(1)
print("DONE..\n")

print("TEST: Scheduling recordings - enable a recording job")
rec.schedule(jobname = "rec1", enable = True)
print("Sleeping 150s to test schedule functionality")
time.sleep(150)
print("DONE..\n")

print("TEST: Scheduling recordings - remove test job")
rec.schedule(jobname = "rec1", delete = "job")
time.sleep(1)
print("DONE..\n")

# Converting media
print("TEST: Converting media - folder of image sequence to video")
imagedir = listfiles(dir = "/home/pi/TESTS", type = "dir", keepdir = True)[0]
pirecorder.Convert(indir = imagedir, type = ".jpg", outdir = "/home/pi/TESTS/converted/imgstovid")
print("DONE..\n")

print("TEST: Converting media - h264 video without framenumber")
pirecorder.Convert(indir = "/home/pi/TESTS", outdir = "/home/pi/TESTS/converted/vid")
print("DONE..\n")

print("TEST: Converting media - h264 video, resized to 50% the size")
pirecorder.Convert(indir = "/home/pi/TESTS", resizeval = 0.5,
                   outdir = "/home/pi/TESTS/converted/vidresized")
print("DONE..\n")

print("TEST: Converting media - h264 video, video with framenumber")
pirecorder.Convert(indir = "/home/pi/TESTS", outdir = "/home/pi/TESTS/converted/vidwithframe",
        withframe = True)
print("DONE..\n")

os.remove("/home/pi/pirecorder/test.conf")
print("Recorded and converted media can be found in /home/pi/TESTS")
print("FINISHED RUNNING ALL TESTS..")
