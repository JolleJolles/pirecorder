#! /usr/bin/env python
#
# Python toolset for the mechanistic study of animal behaviour
# Copyright (c) 2018 - 2019 Jolle Jolles <j.w.jolles@gmail.com>
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

from __future__ import print_function

import os
import cv2
import ast
import sys
import glob
import argparse
import subprocess

from multiprocess import Pool
from pythutils.sysutils import lineprint
from pythutils.drawutils import draw_text
from pythutils.fileutils import listfiles, get_ext, commonpref
from pythutils.mediautils import get_vid_params, videowriter, imgresize

class KeyboardInterruptError(Exception): pass

class Convert:

    """
    Converter class to convert a directory of videos to mp4 with
    potential to write frame number on each frames

    Parameters
    -----------
    indir : str, default = ""
        Directory containing the videos
    outdir : str, default = ""
        Directory where the converted videos should be stored
    type : str, default = ".h264"
        The filetype of the media to convert
    withframe : bool, default = False
        Type of conversion, either very fast conversion using ffmpeg or
        using opencv to add frame number to each frame
    delete : bool, default = False
        If the original videos should be delete or not
    pools : int, default = 4
        Number of computer cores to use for conversion script
    resizeval : float, default = 1
        Float value to which video should be resized
    imgfps : int, default = 25
        Framerate for conversion of images to video
    """

    def __init__(self, indir = "", outdir = "", type = ".h264",
                 withframe = False, delete = False, pools = 4, resizeval = 1,
                 imgfps = 25, internal = False):

        if internal:
            lineprint("Running convert function..")

        self.indir = os.getcwd() if indir == "" else indir
        assert os.path.exists(self.indir), "in-directory does not exist.."
        self.outdir = self.indir if outdir == "" else outdir
        assert os.path.exists(self.outdir), "out-directory does not exist.."

        self.type = type
        self.withframe = ast.literal_eval(withframe)
        self.delete = ast.literal_eval(delete)
        self.pools = int(pools)
        self.resizeval = float(resizeval)
        self.imgfps = int(imgfps)

        self.conv_files = listfiles(self.indir, self.type, keepdir = True)
        self.flen = len(self.conv_files)
        self.done = False

        self.convertpool()


    def conv_single(self, filein):

        try:
            filebase = os.path.basename(filein)
            fileout = filein if self.outdir == "" else self.outdir+"/"+filebase
            lineprint("Start converting "+filebase)

            if self.withframe:
                vid = cv2.VideoCapture(filein)
                fps, width, height, _ = get_vid_params(vid)
                vidout = videowriter(fileout, width, height, fps, self.resizeval)

                while True:
                    flag, frame = vid.read()
                    if flag:
                        if self.resizeval != 1:
                            frame = imgresize(frame, self.resizeval)
                        frame_nr = int(vid.get(cv2.CAP_PROP_POS_FRAMES))
                        draw_text(frame, str(frame_nr), (10,10), 0.9)
                        vidout.write(frame)
                    if not flag:
                        break

            else:
                if self.resizeval != 1:
                    comm = "' -vf 'scale=iw*" + str(self.resizeval) + ":-2' '"
                else:
                    comm = "' -vcodec copy '"
                bashcomm = "ffmpeg -i '"+filein+comm+fileout[:-len(self.type)]+".mp4'"
                bashcomm = bashcomm + " -y -nostats -loglevel 0"
                output = subprocess.check_output(['bash','-c', bashcomm])

            lineprint("Finished converting "+filebase)

        except KeyboardInterrupt:
            raise KeyboardInterruptError()


    def convertpool(self):

        if len(self.conv_files) > 0:

            if self.type in [".h264",".mp4",".avi"]:

                pool = Pool(min(self.pools, self.flen))
                try:
                    pool.map(self.conv_single, self.conv_files)
                    pool.close()
                    self.done = True
                    lineprint("Done converting all videofiles!")
                except KeyboardInterrupt:
                    lineprint("User terminated converting pool..")
                    pool.terminate()
                except Exception as e:
                    excep = "Got exception: %r, terminating pool" % (e,)
                    lineprint(excep)
                    pool.terminate()
                finally:
                    pool.join()

                if self.done and self.delete:
                    for filein in self.conv_files:
                        os.remove(filein)
                    lineprint("Deleted all original videofiles..")

            elif self.type in [".jpg",".jpeg",".png"]:

                frame_array = []
                for filename in self.conv_files:
                    frame = cv2.imread(filename)
                    frame_array.append(frame)
                h, w, _ = frame_array[0].shape
                vidname = commonpref(self.conv_files)
                if self.outdir != "":
                    vidname = self.outdir+"/"+os.path.basename(vidname)
                vidout = videowriter(vidname, w, h, self.imgfps, self.resizeval)
                for i in range(len(frame_array)):
                    vidout.write(frame_array[i])
                vidout.release()

            else:
                lineprint("No video or image files found..")

        else:
            lineprint("No files found..")


def conv():

    """To run the convert function from the command line"""

    parser = argparse.ArgumentParser(prog="Convert", description=Convert.__doc__,
             formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("-i", "--indir" ,default="", metavar="")
    parser.add_argument("-o", "--outdir" ,default="", metavar="")
    parser.add_argument("-t", "--type", default=".h264", metavar="")
    parser.add_argument("-w", "--withframe", default="False", metavar="")
    parser.add_argument("-d", "--delete", default="False", metavar="")
    parser.add_argument("-p", "--pools", default=4, metavar="")
    parser.add_argument("-r", "--resizeval", default=1, metavar="")
    parser.add_argument("-f", "--imgfps", default=25, metavar="")


    args = parser.parse_args()
    Convert(indir=args.indir, outdir=args.outdir, type=args.type,
            withframe=args.withframe, delete=args.delete, pools=args.pools,
            resizeval=args.resizeval, imgfps=args.imgfps)
            