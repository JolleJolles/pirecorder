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
from animlab.imutils import imresize

def is_interactive():
    import __main__ as main
    return not hasattr(main, '__file__')

class KeyboardInterruptError(Exception):
    pass

def converter(filedir="", filedir2="", vidtype=".h264", conv_type="standard",
              remove=False, pools=6, resizeval=1, displayframenr = 100):

    # Load files
    if is_interactive():
        maindir = os.path.realpath('.')
    else:
        maindir = os.getcwd() #os.path.dirname(__file__)
    if filedir2 == "":
        filedir2 = filedir
    if maindir not in filedir:
        filedir = maindir+"/"+filedir
    if maindir not in filedir2:
        filedir2 = maindir+"/"+filedir2
    if not os.path.exists(filedir):
        print("Directory does not exist, try again")
        assert(False)

    # Are there any files?
    done = False
    os.chdir(filedir)
    print(glob.glob("*.h264"))
    print(vidtype)
    conv_files = glob.glob("*"+vidtype)
    os.chdir(maindir)
    if len(conv_files) > 0:

        print("Converting started!   Date: "+datetime.now().strftime('%y/%m/%d')+" Time: "+datetime.now().strftime('%H:%M:%S'))
        print("==================================================")

        if conv_type == "standard":
            for conv_filein in conv_files:
                bashCommand = "ffmpeg -i '"+ filedir+"/"+conv_filein + "' -vcodec copy '" + filedir2+"/"+conv_filein[:-5] +".mp4'"
                output = subprocess.check_output(['bash','-c', bashCommand])
                print(datetime.now().strftime('%H:%M:%S')+" - Finished converting "+conv_filein)
            done = "True"

        if conv_type == "withframe":
            if pools>1:
                pool = Pool(processes=pools)
                try:
                    print(pool.map(singleconv, [filedir+"/"+i for i in conv_files]))
                    pool.close()
                    done = "True"
                    print(datetime.now().strftime('%H:%M:%S')+" - Converting stopped")
                except KeyboardInterrupt:
                    print(datetime.now().strftime('%H:%M:%S')+" - \ngot ^C, terminating pool converting")
                    pool.terminate()
                except Exception as e:
                    print(datetime.now().strftime('%H:%M:%S')+" - \ngot exception: %r, terminating pool converting" % (e,))
                    pool.terminate()
            else:
                for conv_file in conv_files:
                    singleconv(filedir+"/"+conv_file)
                done = "True"


        # When finished, remove all videos
        if done == "True" and remove == "True":
            for conv_filein in conv_files:
                os.remove(conv_filein)
            print(datetime.now().strftime('%H:%M:%S')+" - Removed all original files")

    else:
        print("no files found...")


def singleconv(conv_filein, resizeval=0.5):

    try:
        print(datetime.now().strftime('%H:%M:%S')+" - Start converting "+conv_filein)

        # Load video and store variables
        cap = cv2.VideoCapture(conv_filein)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))

        # Set-up writing of converted video
        fourcc = cv2.VideoWriter_fourcc("m","p","4","v")
        videoname = conv_filein[:-5]+".mp4"
        viddims = (width,height) if resizeval == 1 else (int(width*resizeval),int(height*resizeval))
        videoout = cv2.VideoWriter(videoname, fourcc, fps, viddims) #0x00000021

        # Go through frames
        while True:
            flag, frame = cap.read()
            if flag:
                frame = imresize(frame, resizeval)
                frame_nr = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
                if frame_nr % displayframenr == 0:
                    print(str(frame_nr),end=" ")

                # Print the framenumber on the video frame
                cv2.putText(frame,str(frame_nr),(10,35),cv2.FONT_HERSHEY_SIMPLEX,0.9,(0,0,0),2)
                videoout.write(frame)

            if not flag:
                print(datetime.now().strftime('%H:%M:%S')+" - Finished converting "+conv_filein)
                break

    except KeyboardInterrupt:
        raise KeyboardInterruptError()


# Load the user settings
if True:
    if is_interactive():
        filedir = input("Type in the video directory: ")
        filedir2 = input("Type in the storage directory: ")
        vidtype = input("Video filetype")
        conv_type = input("Type in the conversion type (standard, withframe): ")
        remove = input("Type in if you want files to be removed (True or False): ")
        pools = input("Number of pools")
        resizeval = input("Resize value: ")
        displayframenr = input("displayframenr: ")

    else:
        ap = argparse.ArgumentParser()
        ap.add_argument("-d", "--dir", default="", help="video directory")
        ap.add_argument("-s", "--dir2", default="", help="store directory")
        ap.add_argument("-v", "--vidtype", default="", help="video filetype")
        ap.add_argument("-t", "--convtype", default="standard",
                        help="type of conversion, either 'standard', fast with \
                              ffmpeg, or 'withframe' using opencv adding frame number")
        ap.add_argument("-r", "--remove", default="False", help="remove video True or False")
        ap.add_argument("-p", "--pools", default=6, help="Number of pools")
        ap.add_argument("-x", "--resizeval", default="1", help="Resize multiplier")
        ap.add_argument("-f", "--displayframenr", default="100", help="Display frame nr")
        args = vars(ap.parse_args())
        pools = args["pools"]
        filedir = args["dir"]
        filedir2 = args["dir2"]
        vidtype = args["vidtype"]
        conv_type = args["convtype"]
        remove = args["remove"]
        resizeval = args["resizeval"]

    pools = int(pools)
    resizeval = float(resizeval)


# Run converter
if not is_interactive():
    converter(filedir,filedir2,vidtype,conv_type,remove,pools,resizeval)
