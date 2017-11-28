
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
ap = argparse.ArgumentParser()
ap.add_argument("-l", "--cronline", type=str, default="0 7 * * *",
        help="crontab code for executing the code. Default\
              executes job every day at 07:00")
ap.add_argument("-n", "--name", type=str, default="molly", 
                help="name of the crontab")
ap.add_argument("-e", "--enable", default="True", 
                help="if a job should be enabled or not")
ap.add_argument("-s", "--show", default="False", 
                help="if the crontab schedule should be shown")
args = vars(ap.parse_args())

# create access to the system crontab of pi
cron = CronTab(user='pi')

# create job functions
def enablejob():
    if args["enable"] == "True":
        job.enable()
        print args["name"]+" enabled"
    elif args["enable"] == "False":
        job.enable(False)
        print args["name"]+" disabled"
    else:
        print "Please provide 'True' or 'False' for parameter enable"

def createjob():
    job = cron.new(command='python /home/pi/AnimRec/imgrec.py >> /home/pi/imglog.txt 2>&1',comment=args["name"])
    job.setall(args["cronline"])
    enablejob()
    cron.write()
    print "\n"+args["name"]+ " cron job created succesfully"

def modifyjob():
    job.setall(args["cronline"])
    enablejob()
    cron.write()
    print "\n"+args["name"]+" cron job modified successfully"
    


# check if already jobs exist; if not create job
if len(cron) == 0:
    createjob()

# there are jobs so check if specific job exists
else:
    for i, job in enumerate(cron):

        # a job with specific name exists, so modify
        if job.comment == args["name"]:
            modifyjob()
            break

        # the specific job does not exist so create it
        if len(cron) == (i+1):
            createjob()

# print crontab schedule
if args["show"] == "True":
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

