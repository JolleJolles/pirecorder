#! /usr/bin/env python
"""
Copyright (c) 2017 - 2023 Jolle Jolles <j.w.jolles@gmail.com>

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
    for documentation, see the PiRecorder.schedule function
    """

    def __init__(self, jobname = None, timeplan = None, enable = None,
                 showjobs = False, delete = None, test = False,
                 internal = False, configfile = "pirecorder.conf",
                 logfolder = "/home/pi/pirecorder/"):

        if internal:
            lineprint("Running schedule function.. ")

        self.cron = crontab.CronTab(user = getpass.getuser())

        if jobname is not None:
            self.jobname = "REC_" + jobname
            pexec = sys.executable + " -c "
            pcomm1 = """'import pirecorder; """
            pcomm2 = """R=pirecorder.PiRecorder("%s"); R.record()'""" % configfile
            log1 = " >> " + logfolder + "$(date +%y%m%d)_"
            log2 = str(self.jobname[4:])+".log 2>&1"
            self.task = pexec+pcomm1+pcomm2+log1+log2
        else:
            self.jobname = None

        self.jobtimeplan = timeplan
        self.jobenable = enable
        self.jobsshow = showjobs
        self.jobsclear = delete
        if self.jobsclear not in [None, "all"] and self.jobname == None:
            self.jobname = "REC_" + self.jobsclear

        self.jobs = self.get_jobs()
        self.jobfits = self.get_jobs(name = self.jobname)

        if self.jobsclear is not None:
            self.clear_jobs()
        elif not self.jobsshow:
            if self.jobtimeplan is None and self.jobname is None and not test:
                self.jobsshow = True
            elif self.jobtimeplan is None and self.jobname is not None and not test and len(self.jobfits)==0:
                lineprint("No timeplan provided..")
            elif self.jobtimeplan is not None and self.jobname is None and not test:
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

        if self.jobenable == "True" or self.jobenable == True:
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
                next = str(sch.get_next()) if job.is_enabled() else "disabled"
                print(jobname + plan + next)
        else:
            lineprint("Currently no jobs scheduled..")


def sch():

    """To run the schedule function from the command line"""

    parser = argparse.ArgumentParser(prog="schedule",
             description=Schedule.__doc__,
             formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("-j","--jobname", default=None, metavar="")
    parser.add_argument("-p","--timeplan",default=None, metavar="")
    parser.add_argument("-e","--enable", default=None, metavar="")
    parser.add_argument("-s","--showjobs", default=False, metavar="")
    parser.add_argument("-d","--delete", default=None, metavar="")
    parser.add_argument("-t","--test", default=False, metavar="")
    parser.add_argument("-c","--configfile", default="pirecorder.conf", metavar="")

    args = parser.parse_args()
    Schedule(jobname = args.jobname, timeplan = args.timeplan,
             enable = args.enable, showjobs = args.showjobs,
             delete = args.delete, test = args.test,
             configfile = args.configfile)
