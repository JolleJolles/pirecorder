---
layout: page
title: 6 Record and schedule recordings
nav_order: 8
---
# Record and schedule recordings=
{: .no_toc }

With the pirecorder package it is very easy to make recordings as well as schedule recordings in the future. You can follow the below guide directly or first configure your [recording](4-configure-recording-settings.md) and [camera](5-configure-camera-settings.md).
{: .fs-6 .fw-300 }

## Table of contents
{: .no_toc .text-delta .fs-4 .fw-300 }

1. TOC
{:toc}
---

## Recording
To start your recordings, first import pirecorder, start your instance with the right configuration file, and use the `record` function:

```
import pirecorder
rec = pirecorder.PiRecorder()
rec.record()
```

This will use all recording and camera settings as detailed in your configuration file. It is possible to run recordings immideatealy without any configuration. Then it will just use the default (`configfile = "pirecorder.conf"`) and use the automatic mode to dynamically set the right shutterspeed and white balance. You may wish to set the `rectype` and related parameters though to get the recording that you want. Follow the documentation [here](4-configure-recording-settings.md).

It is also possible to run recordings straight from the terminal without requiring any further user input using the `record` command, which makes it very easy to run controlled recordings without requiring any user input. It will use the custom settings as provided in the configuration file, which you can change with the `--configfile` parameter:

```
record --configfile "custom.conf"
```

## Schedule recordings
Besides starting recordings directly, it is possible to schedule recordings to start recordings (repeatedly) in the future. For this there is the `schedule` function, which creates unique recording jobs (`jobname`) with specific `timeplan`s. An overview with a concise description of all parameters can be found at the bottom of this page.

When using the schedule function make sure you don't have multiple recording jobs at the same time as the camera can ofcourse only deal with a single recording at a time. Also scheduling is not possible with the "vidseq" rectype as that option waits for user input between videos.

### Set the timeplan for your future recordings
The `timeplan` parameter expects a code string that is build on [CRON](https://en.wikipedia.org/wiki/Cron) and should consists of the following parts:

```
* * * * *
- - - - -
| | | | |
| | | | +----- day of week (0 - 7) (sunday = 0 or 7)
| | | +---------- month (1 - 12)
| | +--------------- day of month (1 - 31)
| +-------------------- hour (0 - 23)
+------------------------- min (0 - 59)
```

Each of these parts supports wildcards (\*), ranges (2-5), and lists (2,5,6,11). For example, if you want to schedule a recording at 22:00, every workday of the week, enter the code `0 22 * * 1-5`. The minimum possible time between subsequent scheduled recordings is one minute. Smaller intervals between recordings is of course possible for images with the imgseq command with the `Record` method.

It is important to make sure that the PiRecorder configuration timing settings are within the timespan between subsequent scheduled recordings based on the provided timeplan. For example, a video duration of 20 min and a scheduled recording every 15 min between 13:00-16:00 (`*/15 13-16 * * *`) will fail. This will be checked automatically.

### Test your timeplan
To test a timeplan before linking it to a job, simply set the `test` parameter to `True`. For example,

```
rec.schedule(timeplan = "*/10 */2 10-15 * *", test = True)
```

will state "Your timeplan will run Every 10 minutes, every 2 hours, between day 10 and 15 of the month".

### Plan a recording job
When you have a correct timeplan that works as desired, you can link it to a new or existing job with the `jobname` parameter. Note that by default when creating a new job it won't be enabled immediately. For example, to create a new job named "rec1" :

```python
rec.schedule(timeplan = "*/10 */2 10-15 * *", jobname = "rec1")
```

### Enable/disable a job
To enable/disable a job, enter the `jobname` parameter and set the `enable` parameter to either `True` or `False` (the default). For example, to enable an existing job named "rec1":

```
rec.schedule(jobname = "rec1", enable = True)
```

### Show all jobs
It is easy to see all existing jobs and if they are disabled or when the next recording will start. To show this information, simply set the `showjobs` parameter to `True`:

```
rec.schedule(showjobs = True)
```

would for example show:

```
Job       Timeplan             Next recording
---------------------------------------------
rec1      */10 */2 10-15 *     disabled
rec2      * 3 * *              2020-06-01 03:00:00
```


### Remove jobs
Using the `schedule` function it is also easy to remove jobs. For example, to remove a specific recording job named "rec1" enter:

```
rec.schedule(jobname = "rec1", clear = "job")
```

And to remove all jobs:

```
rec.schedule(jobname = "rec1", clear = "all")
```

### Schedule recordings from the command line
Like for the other modules it is also possible to directly schedule recordings from the command line! You can enter all parameters like explained above by adding to the `schedule` command in terminal. For example:

```
schedule --timeplan "20 8 * * *" --test True
schedule --jobname "rec1" --timeplan "20 8 * * *" --enable False
schedule --jobname "rec1" --enable True
schedule --showjobs True
```

Entering just `schedule` without any additional parameters will just show an overview of all current jobs and their status.

---
Schedule module documentation
{: .text-delta .fs-5}
```
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
delete : [None, "job", "all"], default = None
    If a specific job ('job'), all jobs ('all') or no jobs (None)
    should be cleared from the scheduler.
test : bool; default = False
    Determine if the timeplan is valid and how often it will run the
    record command.
configfile : str, default = "pirecorder.conf"
    The name of the configuration file to be used for the scheduled
    recordings. Make sure the file exists, otherwise the default
    configuration settings will be used.

Note: Make sure Recorder configuration timing settings are within the
timespan between subsequent scheduled recordings based on the provided
timeplan. For example, a video duration of 20 min and a scheduled
recording every 15 min between 13:00-16:00 (*/15 13-16 * * *) will fail.
This will be checked automatically.
```
