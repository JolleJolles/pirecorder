#! /usr/bin/env python
"""
Controlled media recording library for the Rasperry-Pi
Copyright (c) 2015 - 2019 Jolle Jolles <j.w.jolles@gmail.com>

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
from builtins import input

from datetime import datetime
import sys

import animlab.utils as alu
from cron_descriptor import get_description
import crontab
import getpass


class Schedule:

    """
    Class for scheduling future recordings configured with a Recorder instance.

    !Important: Make sure Recorder configuration timing settings are within
    the timespan between subsequent scheduled recordings based on the
    provided timeplan. For example, a vid duration of 20 min and a scheduled
    recording every 15 min between 13:00-16:00 (*/15 13-16 * * *) will fail.

    Parameters
    ----------
    jobname : str, default = None
        Name for the scheduled recorder task to create, modify or remove.
    timeplan : string, default = None
        Code string representing the time planning for the recorder to run
        with current configuration set. Build on CRON, the time plan should
        consist of the following parts:
        * * * * *
        - - - - -
        | | | | |
        | | | | +----- day of week (0 - 7) (sunday = 0 or 7)
        | | | +---------- month (1 - 12)
        | | +--------------- day of month (1 - 31)
        | +-------------------- hour (0 - 23)
        +------------------------- min (0 - 59)
        Each of the parts supports wildcards (*), ranges (2-5), and lists
        (2,5,6,11). For example, if you want to schedule a recording at
        22:00, every workday of the week, enter the code '0 22 * * 1-5' If
        uncertain, crontab.guru is a great website for checking your CRON
        code. Note that the minimum time between subsequent scheduled
        recordings is 1 minute. Smaller intervals between recordings is
        possible for images with the imgseq command with the Record method.
    enable : bool, default = True
        If the scheduled job should be enabled or not.
    showjobs : bool, default = False
        If the differently timed tasks should be shown or not.
    clear : [None, "job", "all"], default = None
        If a specific job ('job'), all jobs ('all') or no jobs (None)
        should be removed from the scheduler.
    test : bool; default = False
        Determine if the timeplan is valid and how often it will run the
        record command.
    """

    def __init__(self, jobname = None, timeplan = None, enable = True,
                showjobs = False, clear = None, test = False,
                logfolder = "/home/pi/setup"):

        alu.lineprint("Running scheduler.. ")
        self.cron = crontab.CronTab(user = getpass.getuser())

        if jobname is not None:
            self.jobname = "AR_" + jobname
            pythexec = sys.executable + " -c "
            pythcomm = "'import animrec; AR=animrec.Recorder(); AR.record()'"
            logloc = " >> " + logfolder + "/"
            logcom = "`date +\%y\%m\%d_$HOSTNAME`_" + str(self.jobname[3:]) + ".log 2>&1"
            self.task = pythexec + pythcomm + logloc + logcom
        else:
            self.jobname = None

        self.jobtimeplan = timeplan
        self.jobenable = enable
        self.jobsshow = showjobs
        self.jobsclear = clear

        self.jobs = self.get_jobs()
        self.jobfits = self.get_jobs(name = self.jobname)

        if self.jobsclear is not None:
            self.clear_jobs()
        else:
            if self.jobtimeplan is None:
                alu.lineprint("No timeplan provided..")
            elif test:
                self.checktimeplan()
            elif self.jobname is None:
                alu.lineprint("No jobname provided..")
            else:
                if self.checktimeplan():
                    self.set_job()
        if self.jobsshow:
            self.jobs = self.get_jobs()
            self.show_jobs()


    def get_jobs(self, name = None):

        """ Returns a list of jobs or specific jobs fitting a specific name """

        if name == None:
            return [job for job in self.cron if job.comment[:3]=="AR_"]
        else:
            return [job for job in self.cron if job.comment == name]


    def checktimeplan(self):

        """ Checks timeplan and prints description """

        valid = crontab.CronSlices.is_valid(self.jobtimeplan)
        if valid:
            timedesc = get_description(self.jobtimeplan)
            print("Your timeplan will run " + timedesc)
        else:
            alu.lineprint("Timeplan is not valid..")

        return valid


    def clear_jobs(self):

        """ Clears a specific or all jobs currently scheduled """

        if self.jobsclear == None:
            pass
        elif self.jobsclear == "all":
            for job in self.jobs:
                if job.comment[:3]=="AR_":
                    self.cron.remove(job)
            alu.lineprint("All scheduled jobs removed..")
        elif self.jobsclear == "job":
            if len(self.jobfits)>0:
                self.cron.remove(self.jobfits[0])
                alu.lineprint(self.jobname[3:]+" job removed..")
            else:
                if(self.jobname == None):
                    alu.lineprint("No jobname provided..")
                else:
                    alu.lineprint("No fitting job found to remove..")
        else:
            alu.lineprint("No correct clear command provided..")
        self.cron.write()


    def enable_job(self):

        """ Enables/disables a specific job """

        if self.jobenable:
            self.job.enable(True)
            alu.lineprint(self.jobname[3:]+" job enabled..")
        else:
            self.job.enable(False)
            alu.lineprint(self.jobname[3:]+" job disabled..")
        self.cron.write()
        self.jobsshow = True


    def set_job(self):

        """ Creates/modifies a specific job """

        if len(self.jobfits)>0:
            self.job = self.jobfits[0]
            self.job.command = self.task
        else:
            self.job = self.cron.new(command = self.task, comment = self.jobname)
        self.job.setall(self.jobtimeplan)

        self.cron.write()
        alu.lineprint(self.jobname[3:]+" job succesfully set..")
        self.enable_job()


    def show_jobs(self):

        """ Prints a table of all scheduled jobs """

        if len(self.cron)>0:
            alu.lineprint("Current job schedule:")
            for job in self.cron:
                lenjob = max(8, len(job.comment[3:]))
                lenplan = max(8, len(str(job)[:str(job).find("/usr")-1]))
            print("Job"+" "*(lenjob-3)+"Time plan"+" "*(lenplan-7)+"Next recording")
            print("="*40)
            self.jobs = self.get_jobs()
            for job in self.jobs:
                sch = job.schedule(date_from = datetime.now())
                jobname = job.comment[3:]+" "*(lenjob-len(job.comment[3:]))
                plan = str(job)[:str(job).find("/usr")-1]
                plan = plan[2:] if plan[0] == "#" else plan
                plan = plan + " "*(lenplan-(len(plan)-2))
                next = str(sch.get_next()) if job.is_enabled() else " disabled"
                print(jobname + plan + next)
        else:
            alu.lineprint("Currently no jobs scheduled..")
