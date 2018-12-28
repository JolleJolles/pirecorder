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

from six.moves import input
from __future__ import print_function

from .__version__ import __version__
import animlab.utils as alu
import animlab.imutils as alimu

import os
import cv2
import sys
import glob
import argparse
import subprocess

from datetime import datetime
from pathos.multiprocessing import ProcessPool


class KeyboardInterruptError(Exception):
    pass

class Converter:

    """ Initializes a converter instance """

    def __init__(self, dir_in = "", vidtype = ".h264", conv_type = "standard",
                 remove = False, pools = 6, resizeval = 1, displayframenr = 100):

        """
        Converter class to convert a directory of videos to mp4 with
        potential to write frame number on each frames

        Parameters
        -----------
        dir_in : str, default = ""
            Directory containing the videos.
        vidtype : str, default = ""
            The filetype of the video to convert
        convtype : ["standard", "withframe"], default = "standard"
            Type of conversion, either very fast conversion using ffmpeg or
            using opencv to add frame number to each frame.
        remove :  boolean, default = False
            If the original videos should be removed or not.
        pools : int, default = 6
            Number of computer cores to use for conversion script.
        resizeval : float, default = 1
            Float value to which video should be resized.
        displayframenr : int, default = 100
            Interval at which frame nr should be displayed during conversion.
        """

        alu.lineprint("Convert function started!", label = "AnimRec")

        maindir = os.getcwd()
        dir_out = dir_in if dir_out == "" else dir_out
        assert os.path.exists(dir_in), "dir_in does not exist, try again.."
        assert os.path.exists(dir_out), "dir_out does not exist, try again.."
        self.dir_in = dir_in

        self.vidtype = vidtype
        self.conv_type = conv_type
        self.remove = remove
        self.pools = int(pools)
        self.resizeval = float(resizeval)
        self.displayframenr = int(displayframenr)

        self.conv_files = alu.listfiles(self.dir_in, self.vidtype, keepdir = True)
        self.done = False

        self.convert()


    def conv_ffmpeg(self):

        """ Runs convert command with ffmpeg"""

        for filein in self.conv_files:
            if self.resizeval != 1:
                comm = "' -vf 'scale=iw*" + str(self.resizeval) + ":ih*" +\
                comm = comm + str(self.resizeval) + "' '"
            else:
                comm = "' -vcodec copy '"
            bashcomm = "ffmpeg -i '" + filein + comm + filein[:-5] + ".mp4' -y"
            output = subprocess.check_output(['bash','-c', bashcomm])
            alu.lineprint("Finished converting " + filein, label = "AnimRec")

        self.done = True


    def conv_cv(self):

        """ Sets up running of convert command with opencv"""

        if self.pools == 1:
            for filein in self.conv_files:
                self.conv_cvfile(filein)
            self.done = True

        else:
            pool = ProcessPool(self.pools)
            try:
                pool.map(self.conv_cvfile, self.conv_files)
                pool.close()
                self.done = True
                alu.lineprint("Converting done!", label = "AnimRec")
            except KeyboardInterrupt:
                alu.lineprint("Got ^C, terminating pool", label = "AnimRec")
                pool.terminate()
            except Exception as e:
                excep = "Got exception: %r, terminating pool" % (e,)
                alu.lineprint(excep, label = "AnimRec")
                pool.terminate()


    def conv_cvfile(self, filein):

        """ Converts single file with opencv"""

        try:
            alu.lineprint("Start converting " + filein, label = "AnimRec")

            vid = cv2.VideoCapture(filein)
            fps,width,height,_ = alimu.get_vid_params(vid)
            vidout = alimu.videowriter(filein, width, height, fps, self.resizeval)

            while True:
                flag, frame = vid.read()
                if flag:
                    frame = alimu.imresize(frame, self.resizeval)
                    frame_nr = int(vid.get(cv2.CAP_PROP_POS_FRAMES))
                    if self.pools == 1:
                        if frame_nr % self.displayframenr == 0:
                            print(str(frame_nr), end=" ")

                    alimu.draw_text(frame, str(frame_nr), (10,35), 0.9)
                    vidout.write(frame)

                if not flag:
                    alu.lineprint("Finished converting " + filein, label = "AnimRec")
                    break

        except KeyboardInterrupt:
            raise KeyboardInterruptError()


    def convert(self):

        if len(self.conv_files) > 0:
            if self.conv_type == "standard":
                self.conv_ffmpeg()
            if self.conv_type == "withframe":
                self.conv_cv()

            if self.done and self.remove:
                for filein in self.conv_files:
                    os.remove(filein)
                alu.lineprint("Removed all original files..", label = "AnimRec")

        else:
            alu.lineprint("no files found..", label = "AnimRec")
