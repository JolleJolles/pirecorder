#! /usr/bin/env python
"""
Copyright (c) 2017 - 2019 Jolle Jolles <j.w.jolles@gmail.com>

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

import sys
import crontab
import getpass
import argparse
import datetime

from pythutils.sysutils import lineprint
from cron_descriptor import get_description

from .__version__ import __version__

class Schedule:

    """
    Class for scheduling future recordings configured with a PiRecorder instance

    Note: Make sure Recorder configuration timing settings are within the
    timespan between subsequent scheduled recordings based on the provided
    timeplan. For example, a video duration of 20 min and a scheduled recording
    every 15 min between 13:00-16:00 (*/15 13-16 * * *) will fail. This will be
    checked automatically.

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
    enable : bool, default = None
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

    def __init__(self, jobname = None, timeplan = None, enable = None,
                showjobs = False, clear = None, test = False, internal = False):

        if internal:
            lineprint("Running schedule function.. ")

        self.cron = crontab.CronTab(user = getpass.getuser())

        if jobname is not None:
            self.jobname = "REC_" + jobname
            pexec = sys.executable + " -c "
            pcomm = "'import pirecorder; R=pirecorder.PiRecorder(); R.record()'"
            logloc = " >> /home/pi/pirecorder/"
            logcom = "`date +\%y\%m\%d_$HOSTNAME`"+str(self.jobname[4:])+".log 2>&1"
            self.task = pexec+pcomm+logloc+logcom
        else:
            self.jobname = None

        self.jobtimeplan = timeplan
        self.jobenable = enable
        self.jobsshow = showjobs
        self.jobsclear = clear
        if self.jobsclear not in [None, "all"] and self.jobname == None:
            self.jobname = "REC_" + self.jobsclear

        self.jobs = self.get_jobs()
        self.jobfits = self.get_jobs(name = self.jobname)

        if self.jobsclear is not None:
            self.clear_jobs()
        elif not self.jobsshow:
            if self.jobtimeplan is None and self.jobname is None and not test:
                self.jobsshow = True
            elif self.jobtimeplan is None and self.jobname is not None and not test:
                lineprint("No timeplan provided..")
            elif self.jobtimeplan is not None and self.jobname is None:
                lineprint("No jobname provided..")
            elif test and self.jobtimeplan is not None:
                self.checktimeplan()
            else:
                if enable is None:
                    self.checktimeplan()
                self.set_job()
        if self.jobsshow:
            self.show_jobs()


    def get_jobs(self, name = None):

        """Returns a list of jobs or specific jobs fitting a specific name"""

        if name == None:
            return [job for job in self.cron if job.comment[:3]=="REC"]
        else:
            return [job for job in self.cron if job.comment == name]

    def checktimeplan(self):

        """Checks timeplan and prints description"""

        valid = crontab.CronSlices.is_valid(self.jobtimeplan)
        if valid:
            timedesc = get_description(self.jobtimeplan)
            lineprint("Your timeplan will run " + timedesc)
        else:
            lineprint("Timeplan is not valid..")

        return valid


    def clear_jobs(self):

        """Clears a specific or all jobs currently scheduled"""

        if self.jobsclear == None:
            pass
        elif self.jobsclear == "all":
            for job in self.jobs:
                if job.comment[:3]=="REC":
                    self.cron.remove(job)
            lineprint("All scheduled jobs removed..")
        else:
            if len(self.jobfits)>0:
                self.cron.remove(self.jobfits[0])
                lineprint(self.jobname[4:]+" job removed..")
            else:
                lineprint("No fitting job found to remove..")
        self.cron.write()
        self.jobsshow = True


    def enable_job(self):

        """Enables/disables a specific job"""

        if self.jobenable == "True":
            self.job.enable(True)
            lineprint(self.jobname[4:]+" job enabled..")
        else:
            self.job.enable(False)
            lineprint(self.jobname[4:]+" job disabled..")
        self.cron.write()
        self.jobsshow = True


    def set_job(self):

        """Creates/modifies a specific job"""

        if len(self.jobfits)>0:
            self.job = self.jobfits[0]
            self.job.command = self.task
        else:
            self.job = self.cron.new(command = self.task, comment = self.jobname)
        if self.jobtimeplan is not None:
            self.job.setall(self.jobtimeplan)
            self.cron.write()
            lineprint(self.jobname[4:]+" job succesfully set..")

        if self.jobenable is not None:
            self.enable_job()


    def show_jobs(self):

        """Displays a table of all scheduled jobs"""

        if len(self.cron)>0:
            lineprint("Current job schedule:")
            for job in self.cron:
                lenjob = max(8, len(job.comment[4:]))
                lenplan = max(8, len(str(job)[:str(job).find(" /")]))
            header = "Job"+" "*(lenjob-1)+"Timeplan"+" "*(lenplan-7)+"Next recording"
            print(header)
            print("-"*len(header))
            self.jobs = self.get_jobs()
            for job in self.jobs:
                sch = job.schedule(date_from = datetime.datetime.now())
                jobname = job.comment[4:]+" "*(lenjob-(len(job.comment[4:])-2))
                plan = str(job)[:str(job).find(" /")-2]
                plan = plan[2:] if plan[0] == "#" else plan
                plan = plan + " "*(lenplan-(len(plan)-1))
                next = str(sch.get_next()) if job.is_enabled() else " disabled"
                print(jobname + plan + next)
        else:
            lineprint("Currently no jobs scheduled..")


def sch():

    """To run the schedule function from the command line"""

    parser = argparse.ArgumentParser(prog="schedule",
             description=Schedule.__doc__,
             formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("-j","--jobname",metavar="")
    parser.add_argument("-p","--timeplan",metavar="")
    parser.add_argument("-e","--enable",default=None,metavar="")
    parser.add_argument("-s","--showjobs",default=False,metavar="")
    parser.add_argument("-c","--clear",metavar="")
    parser.add_argument("-t","--test",default=False,metavar="")

    args = parser.parse_args()
    Schedule(jobname=args.jobname, timeplan=args.timeplan, enable=args.enable,
             showjobs=args.showjobs, clear=args.clear, test=args.test)
