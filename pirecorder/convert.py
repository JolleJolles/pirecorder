#! /usr/bin/env python
"""
Copyright (c) 2019 - 2023 Jolle Jolles <j.w.jolles@gmail.com>

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

from __future__ import print_function

import os
import cv2
import ast
import sys
import time
import glob
import argparse
import subprocess

from threading import Thread
from multiprocess import Pool
from pythutils.sysutils import lineprint
from pythutils.drawutils import draw_text
from pythutils.fileutils import listfiles, get_ext, commonpref, move
from pythutils.mediautils import get_vid_params, videowriter, imgresize

class KeyboardInterruptError(Exception): pass

class Convert:

    """
    Module to convert a directory of media files with potential to resize the
    media, write the unique frame number on each frame, and continuously monitor
    a folder for updated files. Multiple files can be converted simultaneously
    with the pools parameter to optimally use the computer's processing cores.

    Parameters
    -----------
    indir : str, default = ""
        Directory containing the videos.
    outdir : str, default = ""
        Directory where the converted videos should be stored. If the directory
        does not exist yet it will be newly created.
    type : str, default = ".h264"
        The filetype of the media to convert.
    withframe : bool, default = False
        Type of conversion, either very fast conversion using FFmpeg or using
        OpenCV to draw the frame number on each video frame.
    delete : bool, default = False
        If the original videos should be deleted or not.
    pools : int, default = 4
        Number of simultaneous converting processing that should be allowed.
        Works optimally when equal to the number of computer processing cores.
    resizeval : float, default = 1
        Float value to which the video should be resized.
    imgfps : int, default = 25
        Framerate for conversion of images to video.
    sleeptime : int, default = None
        Time in seconds between subsequent checks for files within a folder. The
        default value (None) only converts the current files.
    """

    def __init__(self, indir = "", outdir = "", type = ".h264",
                 withframe = False, overwrite = False, delete = False,
                 pools = 4, resizeval = 1, fps = None, imgfps = 25,
                 internal = False, sleeptime = None):

        if internal:
            lineprint("Running convert function..", label="pirecorder")

        self.indir = os.getcwd() if indir == "" else indir
        assert os.path.exists(self.indir), "in-directory does not exist.."
        self.outdir = self.indir if outdir == "" else outdir
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)

        self.rootdir = os.getcwd()
        os.chdir(self.indir)

        self.type = type
        self.withframe = withframe
        self.delete = delete
        self.pools = int(pools)
        self.resizeval = float(resizeval)
        self.fps = int(fps) if fps is not None else None
        self.imgfps = int(imgfps)
        self.terminated = False

        while True:
            files = listfiles(self.indir, self.type, keepdir = False)
            old = listfiles(self.indir, self.type, keepext = False)
            new = listfiles(self.outdir, ".mp4", keepext = False)
            self.todo = files
            if not overwrite:
                self.todo = [files[i] for i,file in enumerate(old) if file not in new]
            if self.type in [".jpg",".jpeg",".png"] and len(self.todo)>0:
                 if len([f for f in new if commonpref(self.todo) in f])>0 and not overwrite:
                     self.todo = []
            self.convertpool()
            msg = "No files to convert.."
            if sleeptime == None:
                if not self.terminated:
                    lineprint(msg, label="pirecorder")
                return
            else:
                try:
                    lineprint(msg+" rechecking in "+str(sleeptime)+"s..", label="pirecorder")
                    time.sleep(sleeptime)
                except KeyboardInterrupt:
                    lineprint("Terminating checking for files..", label="pirecorder")
                    return

    def conv_single(self, filein):

        try:
            filebase = os.path.basename(filein)
            fileout = filein if self.outdir == "" else self.outdir+"/"+filebase
            lineprint("Start converting "+filebase, label="pirecorder")

            if self.withframe:
                vid = cv2.VideoCapture(filein)
                fps, width, height, _ = get_vid_params(vid)
                if self.fps is None:
                    self.fps = fps
                vidout = videowriter(fileout, width, height, self.fps, self.resizeval)

                while True:
                    flag, frame = vid.read()
                    if flag:
                        if self.resizeval != 1:
                            frame = imgresize(frame, self.resizeval)
                        frame_nr = int(vid.get(cv2.CAP_PROP_POS_FRAMES))
                        draw_text(frame, str(frame_nr), (10,10), 0.9, col="white",
                                  shadow=True)
                        vidout.write(frame)
                    if not flag:
                        break

            else:
                if self.resizeval != 1:
                    comm = "' -vf 'scale=iw*" + str(self.resizeval) + ":-2' '"
                else:
                    comm = "' -vcodec copy '"
                bashcomm = "ffmpeg"
                if self.fps is not None:
                    bashcomm = bashcomm+" -r "+ str(self.fps)
                bashcomm = bashcomm+" -i '"+filein+comm+fileout[:-len(self.type)]+".mp4'"
                bashcomm = bashcomm + " -y -nostats -loglevel 0"
                output = subprocess.check_output(['bash','-c', bashcomm])

            lineprint("Finished converting "+filebase, label="pirecorder")

        except KeyboardInterrupt:
            raise KeyboardInterruptError()


    def convertpool(self):

        if len(self.todo) > 0:

            if self.type in [".h264",".mp4",".avi"]:

                pool = Pool(min(self.pools, len(self.todo)))
                try:
                    pool.map(self.conv_single, self.todo)
                    pool.close()
                    lineprint("Done converting all videofiles!", label="pirecorder")
                except KeyboardInterrupt:
                    lineprint("User terminated converting pool..", label="pirecorder")
                    self.terminated = True
                    pool.terminate()
                    return
                except Exception as e:
                    excep = "Got exception: %r, terminating pool" % (e,)
                    lineprint(excep, label="pirecorder")
                    pool.terminate()
                finally:
                    pool.join()

                if self.delete:
                    for filein in self.todo:
                        os.remove(filein)
                    lineprint("Deleted all original videofiles..", label="pirecorder")

            elif self.type in [".jpg",".jpeg",".png"]:

                vidname = commonpref(self.todo)
                lineprint("Start converting "+str(len(self.todo))+" images", label="pirecorder")

                frame_array = []
                for filename in self.todo:
                    frame = cv2.imread(filename)
                    frame_array.append(frame)
                    #os.rename(filename, self.outdir+"/"+filename)
                h, w, _ = frame_array[0].shape
                if self.outdir != "":
                    vidname = self.outdir+"/"+os.path.basename(vidname)
                vidout = videowriter(vidname, w, h, self.imgfps, self.resizeval)
                for i in range(len(frame_array)):
                    vidout.write(frame_array[i])
                vidout.release()
                lineprint("Finished converting "+os.path.basename(vidname), label="pirecorder")

            else:
                lineprint("No video or image files found..", label="pirecorder")


def conv():

    """To run the convert function from the command line"""

    parser = argparse.ArgumentParser(prog="Convert", description=Convert.__doc__,
             formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("-i", "--indir" ,default="", metavar="")
    parser.add_argument("-o", "--outdir" ,default="", metavar="")
    parser.add_argument("-t", "--type", default=".h264", metavar="")
    parser.add_argument("-w", "--withframe", default="False", metavar="")
    parser.add_argument("-d", "--delete", default="False", metavar="")
    parser.add_argument("-p", "--pools", default=4, type=int, metavar="")
    parser.add_argument("-r", "--resizeval", default=1, type=float, metavar="")
    parser.add_argument("-f", "--imgfps", default=25, type=int, metavar="")
    parser.add_argument("-s", "--sleeptime", default=None, type=int, metavar="")

    args = parser.parse_args()
    args.withframe = ast.literal_eval(args.withframe)
    args.delete = ast.literal_eval(args.delete)
    Convert(indir = args.indir, outdir = args.outdir, type = args.type,
            withframe = args.withframe, delete = args.delete, pools = args.pools,
            resizeval = args.resizeval, imgfps = args.imgfps,
            sleeptime = args.sleeptime)
