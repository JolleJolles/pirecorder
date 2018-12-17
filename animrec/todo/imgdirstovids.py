# !/usr/bin/python

import os
import subprocess
from datetime import datetime
import argparse
from time import time
from socket import gethostname


def iswin():
    return True if os.name == 'nt' else False


def homedir():

    return os.path.expanduser("~")+"/"


def isjup():

    '''checks if script is run interactivelly'''

    import __main__ as main

    return not hasattr(main, '__file__')


def listfiles(filedir = ".", filetype = (".jpg"), dirs = False):

    '''list directories in a folder'''

    if dirs:
        outlist = [i for i in os.listdir(filedir) if os.path.isdir(os.path.join(filedir, i))]
    else:
        outlist = [each for each in os.listdir(filedir) if each.endswith(filetype)]
        outlist = [i for i in outlist if not i.startswith('.')]
    outlist = sorted(outlist)

    return outlist


def createdir(dirname):

    '''creates a subdirectory'''

    try:
        os.makedirs(dirname)
    except OSError:
        if not os.path.isdir(dirname):
            raise


def dirconvert(maindir, viddir = "videos"):

    '''convert images in sub-directories'''

    print datetime.now().strftime('%H:%M:%S'), "- Image to video conversion started!\n     ============================================="

    host = gethostname()

    maindir = "/home/pi/" + maindir
    pidir = maindir + "/" + host
    pividdir = maindir + "/" + viddir + "/" + host

    createdir(viddir)
    createdir(pividdir)

    counter = 0

    print datetime.now().strftime('%H:%M:%S'), "- Processing folders for " + host + ":"
    os.chdir(pidir)

    subdirs = listfiles(dirs = True)

    for subdir in subdirs:
        datedir = pidir + "/" + subdir
        os.chdir(datedir)

        counter += 1
        t1 = time()
        print subdir,"-",

        vidname = pividdir + "/" + host + "_" + subdir + ".mp4"

        if iswin():
            output = subprocess.check_output("(for %i in (*.jpg) do @echo file '%i')|sort /o imglist.txt", shell=True)
            if not imglistonly:
                output = subprocess.check_output("ffmpeg -f concat -i imglist.txt -c:v libx264 -pix_fmt yuv420p -hide_banner -nostats -loglevel quiet -y " + vidname, shell=False)
            else:
                timediff = time() - t1
                print "Imglist created in "+"%.2f" % timediff+" sec.."

        else:
            bashCommand = ['bash','-c', 'ffmpeg -pattern_type glob -i "*.jpg" -c:v libx264 -pix_fmt yuv420p -hide_banner -nostats -loglevel quiet -y ' + vidname]
            output = subprocess.check_output(bashCommand)

        if iswin() and not imglistonly:
            timediff = time() - t1
            print "Video created in "+"%.2f" % timediff+" sec.."

        print ""

    print datetime.now().strftime('%H:%M:%S'), "- Done converting all " + str(counter) + " folders.."


# Load the user settings
#-----------------------
if isjup():
    filedir = raw_input("Main directory that holds sub-directories with images to convert: ")
    selectlist = raw_input("List of subdirectories to convert (blank is all): ")
else:
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--dir", default="SERVER", help="video directory")
    ap.add_argument("-s", "--select", default="", help="selection of sub directories")
    ap.add_argument("-e", "--exclude", default="", help="exclude directories")
    ap.add_argument("-i", "--imglistonly", default=False, help="only create imglist or not")
    args = vars(ap.parse_args())
    filedir = args["dir"]
    selectlist = args["select"]
    exclude = args["exclude"]
    imglistonly = args["imglistonly"]


# Start convert script
#-----------------------
dirconvert(filedir)
