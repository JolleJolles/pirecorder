
# coding: utf-8

# In[ ]:

#!/usr/bin/python

#######################################
# Script for planning recording task  #
# Author: J. Jolles                   #
# Last updated: 28 Nov 2017           #
#######################################

# import packages
import argparse
from crontab import CronTab
from datetime import datetime as dt

# construct the argument parse and parse the arguments
# (for using the script from commandline without runp)
ap = argparse.ArgumentParser()
ap.add_argument("-w", "--imgwait", type=float, default=5.0,
        help="The delay between subsequent images in seconds")
ap.add_argument("-i", "--imgnr", type=int, default=10,
        help="The number of images that should be taken. ")
ap.add_argument("-t", "--imgtime", type=int, default=1,
        help="The duration in minutes during which images\
              should be taken.")
ap.add_argument("-c", "--taskcode", type=str, default="0 7 * * *",
        help="crontab code for executing the code. Default\
              executes job every day at 07:00")
ap.add_argument("-n", "--name", type=str, default="molly", 
        help="name of the crontab")
ap.add_argument("-e", "--set", default="True", 
        help="if a job should be enabled or not")
ap.add_argument("-s", "--show", default="False", 
        help="if the crontab schedule should be shown")
args = vars(ap.parse_args())
imgwait = args["imgwait"]
imgnr = args["imgnr"]
imgtime = args["imgtime"]
taskcode = str(args["code"])
taskname = str(args["name"])
taskset = str(args["set"])
taskshow = str(args["show"])

# define plan function
def plan(imgwait=5.0,imgnr=100,imgtime=480,taskname="molly",
         taskcode="0 7 * * *",taskset="True",taskshow="False"):

    """
    Run automated image recording with the rpi camera

    Parameters
    ----------
    imgwait : float, default = 5.0
        The delay between subsequent images in seconds. When a 
        delay is provided that is less than shutterspeed + 
        processingtime "delay" will be automatically set at 0 
        and images thus taken one after the other.
    imgnr : integer, default = 100
        The number of images that should be taken. When this 
        number is reached the script will automatically terminate.
        The minimum of imgnr and nr of images based on imgwait and
        imgtime will be selected.
    imgtime : integer, default = 10
        The time in minutes during which images should be taken.
        The minimum of imgnr and nr of images based on imgwait and
        imgtime will be selected.
    taskname : str, default = "molly"
        The name for the timing task. Really only needed to set 
        when wanting to run multiple different tasks.
    taskcode : string, default = "0 7 * * *"
        The taskcode representing the schedule for the image script
        to be executed, based on CRON scheduling. The parts it
        should contain are as follows:
        * * * * * *
        - - - - - -
        | | | | | |
        | | | | | + year [optional]
        | | | | +----- day of week (0 - 7) (Sunday=0 or 7)
        | | | +---------- month (1 - 12)
        | | +--------------- day of month (1 - 31)
        | +-------------------- hour (0 - 23)
        +------------------------- min (0 - 59)
        Each of the parts supports wildcards (*), ranges (2-5),
        and lists (2,5,6,11). For example, if you want to run the
        img recording script at 22:00 on every day of the week 
        from Monday through Friday: 0 7 (2,5) * *
    taskset : str, default = "True"
        If the timing task should be enabled ("True") or disabled
        ("False")
    timeshow : str, default = "False"
        If the different timed tasks should be shown ("True") or
        not ("False")
    
    Output
    -------
    A scheduled task to record images for a certain duration of time or
    number according to a specific schedule

    """
        
    # create access to the system crontab of pi
    cron = CronTab(user='pi')

    # define crontab job command
    exe = "python"
    scriptloc = " /home/pi/AnimRec/imgrec.py"
    fcode = " -w "+str(imgwait)+" -n"+str(imgnr)+" -t "+str(imgtime)
    write = " >> /home/pi/imglog.txt 2>&1"
    task = exe+scriptloc+fcode+write
    
    # create job functions
    def enablejob(job):
        if timeenable == "True":
            job.enable()
            print taskname+" enabled"
        elif timeenable == "False":
            job.enable(False)
            print taskname+" disabled"
        else:
            print "Please provide 'True' or 'False' for parameter enable"

    def createjob():
        job = cron.new(command=task,comment=taskname)
        job.setall(taskcode)
        enablejob(job)
        cron.write()
        print "\n"+taskname+ " cron job created succesfully"

    def modifyjob():
        job.setall(timecode)
        enablejob(job)
        cron.write()
        print "\n"+timename+" cron job modified successfully"

    # check if already jobs exist; if not create job
    if len(cron) == 0:
        createjob()

    # there are jobs so check if specific job exists
    else:
        for i, job in enumerate(cron):

            # a job with specific name exists, so modify
            if job.comment == timename:
                modifyjob()
                break

            # the specific job does not exist so create it
            if len(cron) == (i+1):
                createjob()

    # print crontab schedule
    if timeshow == "True":
        print "\nCurrent task schedule:"

        # get length of maximum crontab name
        maxlen = 8
        for job in cron:
            maxlen = len(job) if (len(job)>maxlen and len(job)<30) else maxlen

        # now show last and next job
        for job in cron:
            sch = job.schedule(date_from=dt.now())
            previous = sch.get_prev()
            next = sch.get_next()
            jobname = job.comment
            jobname = jobname+" "*(maxlen-len(jobname))
            print jobname+" - last job: "+str(previous)+"; next job: "+str(next)

