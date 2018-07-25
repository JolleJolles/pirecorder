
# coding: utf-8

# In[1]:


#!/usr/bin/env python2.7
# author JW Jolles
# Last updated: 23 July 2018

# Import libraries
#-----------------------
import os
import subprocess
from datetime import datetime
import argparse
from time import time

# load functions
#-----------------------
def iswin():    
    return True if os.name == 'nt' else False

        
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
                

def dirconvert(maindir = ".", viddirname = "videos"):
    
    '''convert images in sub-directories'''
    
    print datetime.now().strftime('%H:%M:%S'), "- Image to video conversion started!\n     ============================================="
    
    # Change working directory to main directory
    os.chdir(maindir)
    
    # Get list of all rpi directories
    pidirs = listfiles(dirs=True) if selectlist == "" else [selectlist]

    # Create directory for videos
    createdir(viddirname)

    # Create counter
    counter = 0

    # Check each pidir
    for pidir in pidirs:

        # Create sub videos dir
        subviddir = maindir + "/" + viddirname + "/" + pidir
        createdir(subviddir)
                  
        # Change working directory
        print datetime.now().strftime('%H:%M:%S'), "- Processing folders for " + pidir + ":"
        os.chdir(maindir + "/" + pidir)

        # Get directories per dir
        subdirs = listfiles(dirs=True)

        # For each day make a video and place in viddirname with pidir
        for subdir in subdirs:
            os.chdir(maindir + "/" + pidir + "/" + subdir)
            counter += 1
            t1 = time()
            print subdir,"-",

            vidname = subviddir + "/" + pidir + "_" + subdir + ".mp4"
            if iswin():
                output = subprocess.check_output("(for %i in (*.jpg) do @echo file '%i')|sort /o imglist.txt", shell=True)
                output = subprocess.check_output("ffmpeg -f concat -i imglist.txt -c:v libx264 -pix_fmt yuv420p -hide_banner -nostats -loglevel quiet -y " + vidname, shell=False)
            else:
                bashCommand = ['bash','-c', 'ffmpeg -pattern_type glob -i "*.jpg" -c:v libx264 -pix_fmt yuv420p -hide_banner -nostats -loglevel quiet -y ' + vidname]
                output = subprocess.check_output(bashCommand)
            
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
    ap.add_argument("-d", "--dir", default="", help="video directory")
    ap.add_argument("-s", "--select", default="", help="selection of sub directories")
    args = vars(ap.parse_args())
    filedir = args["dir"]
    selectlist = args["select"]


# Start convert script
#-----------------------
dirconvert(filedir)


# In[ ]:


