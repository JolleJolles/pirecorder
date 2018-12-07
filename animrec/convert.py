#! /usr/bin/env python

from __future__ import print_function

import os
import cv2
import glob
import argparse
import subprocess

from datetime import datetime
from multiprocessing import Pool
from six.moves import input

import sys

sys.path.append('/Users/jollejolles/dropbox/Science/5 Coding/AnimLab/')
import animlab.utils as alu
import animlab.imutils as alimu

class KeyboardInterruptError(Exception):
    pass

class Converter:

    """ Initializes a converter instance """

    def __init__(self, dir_in="", dir_out="", vidtype=".h264", conv_type="standard",
                  remove=False, pools=6, resizeval=1, displayframenr = 100):

        '''
            Converter class to conver a directory of videos to mp4 with potential
            to write frame number on each frames

            Parameters
            -----------
            vidtype : str, default=""
                The filetype of the video to convert
            convtype : ["standard","withframe"], default = "standard"
                Type of conversion, either very fast conversion using ffmpeg or
                using opencv to add frame number to each frame
            remove :  boolean, default=False
                If the original videos should be removed or not
            pools : int, default=6
                Number of cores to use for conversion
            resizeval : float, default=1,
                Float value to which video should be resized
            displayframenr : int, default="100"
                Interval at which frame nr should be displayed during conversion
        '''

        alu.lineprint("Convert function started!\n", label = "AnimRec")

        maindir = os.getcwd()
        dir_in = dir_in if maindir in dir_in else maindir+"/"+dir_in
        dir_out = dir_in if dir_out == "" else dir_out
        dir_out = dir_out if maindir in dir_out else maindir+"/"+dir_out
        assert os.path.exists(dir_in), "dir_in directory does not exist, try again"
        assert os.path.exists(dir_out), "dir_out directory does not exist, try again"
        self.dir_in = dir_in
        self.dir_out = dir_out

        self.vidtype = vidtype
        self.conv_type = conv_type
        self.remove = remove
        self.pools = int(pools)
        self.resizeval = float(resizeval)
        self.displayframenr = int(displayframenr)

        self.conv_files = alu.listfiles(self.dir_in, self.vidtype, keepdir = True)
        self.done = False

        if len(self.conv_files) > 0:
            if conv_type == "standard":
                self.conv_ffmpeg()
            if conv_type == "withframe":
                self.conv_cv()

            if self.done and self.remove:
                for filein in self.conv_files:
                    os.remove(filein)
                alu.lineprint("Removed all original files", label = "AnimRec")

        else:
            alu.lineprint("no files found...", label = "AnimRec")


    def conv_ffmpeg(self):

        for filein in self.conv_files:
            bashCommand = "ffmpeg -i '"+filein+"' -vcodec copy '"+filein[:-5] +".mp4'"
            output = subprocess.check_output(['bash','-c', bashCommand])
            alu.lineprint("Finished converting "+filein+"\n", label = "AnimRec")

        self.done = True


    def conv_cv(self):

        if self.pools == 1:
            for filein in self.conv_files:
                self.conv_cvfile(filein)
            self.done = "True"

        else:
            pool = Pool(processes = self.pools)
            try:
                print(pool.map(self.conv_cvfile, self.conv_files))
                pool.close()
                self.done = True
                lineprint("Converting stopped\n", label = "AnimRec")
            except KeyboardInterrupt:
                lineprint("Got ^C, terminating pool converting\n", label = "AnimRec")
                pool.terminate()
            except Exception as e:
                lineprint("got exception: %r, terminating pool converting" % (e,)+"\n", label = "AnimRec")
                pool.terminate()

    def conv_cvfile(self, filein):

        try:
            alu.lineprint("Start converting "+filein+"\n", label = "AnimRec")

            vid = cv2.VideoCapture(filein)
            fps,width,height,_ = alimu.get_vid_params(vid)
            vidout = alimu.videowriter(filein, width, height, fps, resizeval)

            while True:
                flag, frame = cap.read()
                if flag:
                    frame = imresize(frame, resizeval)
                    frame_nr = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
                    if frame_nr % displayframenr == 0:
                        print(str(frame_nr),end=" ")

                    # Print the framenumber on the video frame
                    cv2.putText(frame,str(frame_nr),(10,35),cv2.FONT_HERSHEY_SIMPLEX,0.9,(0,0,0),2)
                    vidout.write(frame)

                if not flag:
                    print(datetime.now().strftime('%H:%M:%S')+" - Finished converting "+conv_filein)
                    break

        except KeyboardInterrupt:
            raise KeyboardInterruptError()
