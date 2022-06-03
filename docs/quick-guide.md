---
layout: page
title: Quick usage guide
nav_order: 1
---

# Quick usage guide
{: .no_toc }

This guide is meant to get you up and running and using pirecorder in no time. We will go through all the steps from setting up your raspberry pi, installing pirecorder, configuring pirecorder, recording, scheduling, and finally converting your recorded media.
{: .fs-6 .fw-300 }

## Table of contents
{: .no_toc .text-delta .fs-4 .fw-300 }

1. TOC
{:toc}

## Setting up your raspberry pi
1. Connect a camera with ribbon cable to the raspberry pi and roughly position it where you need it
2. Connect your raspberry pi to power to turn it on and either have direct control or VNC access
3. Open a terminal window and make sure your raspberry pi is fully up to date:
```
sudo apt-get update && sudo apt-get upgrade -y
```
4. Also make sure your firmware is fully up to date to get the latest drivers to work with the picamera
```
sudo apt-get dist-upgrade -y
```
5. Make sure the camera is enabled
```
sudo raspi-config
```
go to `5 Interfacing options`, then `P1 Camera`, and click `yes`. Now reboot your raspberry pi.

6. Make sure the camera is properly connected:
```
raspistill -t 0 -k
```
To exit again, press `ctrl+c`

## Install pirecorder
1. install pirecorder (and most dependencies) with pip:
```
pip install pirecorder
```
2. install picamera:
```
sudo pip install "picamera[array]"
```
3. install dependencies for OpenCV:
```
sudo apt-get install libhdf5-dev libhdf5-serial-dev libatlas-base-dev libatlas3-base libjasper-dev python3-pyqt5 -y
```
4. Install OpenCV with pip:
```
pip install opencv-contrib-python==4.5.3.56
```
Note: we use a specific version as the latest version may not always work properly on raspberry pi yet.

## Use pirecorder for the first time
1. Start python (`python`) and import the pirecorder package
```
import pirecorder
```
2. Initiate a recording instance, which will automatically create the `/home/pi/pirecorder` folder and default configuration file:
```
rec = pirecorder.PiRecorder()
```
Note: the variable to store the `PiRecorder` instance can be any name, here `rec` is chosen as an example.

## Optionally: Correctly position the camera and adjust its focus
1. Open a stream instance:
```
rec.stream()
```
2. Change the position of the camera until satisfied. Optionally press the `c`-key to show a diagonal cross, which can help with positioning.
3. Drag with the mouse to create a rectangular area of a region you want to use to adjust the camera focus. Press the `z`-key to show this region zoomed in. Now adjust the focus by slightly turning the camera lens, press the `n`-key to refresh the image, and continue with these steps until you are satisfied. Press the `esc`-key to exit the zoomed in window.

## Optionally: Store the region of interest
Still in the stream instance, use the mouse again to draw a rectangle that encompasses the region of the camera stream that should be recorded. When satisfied with the region press the `s`-key to store the coordinates in the configuration file. Press the `esc`-key to exit the stream.

## Set the recording settings
Configure your recording settings with the `settings` function. Key is the `rectype` parameter, which can be `img` (a single image), `vid` (a single video), `imgseq` (a timelape), `vidseq` (a sequence of videos). By default it will record with the maximal resolution, which can be altered with `imgdims` and `viddims`. Videos are recorded with 24fps, which can be changed with the `vidfps` parameter. The `label` parameter will help identify your recorded files. Other relevant parameters are `vidduration`, `viddelay`, `imgnr`, `imgtime`, `imgwait`, `imgquality`, `vidquality`, `maxviddur`, and `maxvidsize`. For example, to set the `rectype`, `vidduration`, and `label` for your recordings:
```
rec.settings(rectype = "vid", vidduration = 60, label = "test")
```

## Optionally: set the camera settings
When you have pirecorder running and are happy with the recording settings, you may want to further configure the camera settings to get your optimal recordings. A large number of parameters can be set. Have a look at the detailed documentation [here](6-configure-camera-settings.md). Very handy is the `camconfig` function with which it is possible to open an interactive video stream and adjust the camera settings with trackbars:
```
rec.camconfig()
```

## Start a recording
Now you are happy with your settings you can simply start a recording with the `record` function:
```
rec.record()
```

## Schedule a recording
To schedule recordings in the future you need to set a `timeplan` (build on CRON) and create jobs with unique `jobname`. These jobs can then be enabled or disable with the `enable` parameter and removed completely with the `delete` parameter (either enter the jobname or "all"). It is also possible to test timeplans with the `test` parameter.

An example. If your recording configuration is set to record a 15min video and you want to record a new video every half an hour between 07.00 and 17.00 on each week day:

```
rec.schedule(timeplan = "0/30 7-17 * * 1-5", jobname = "weekjob", enable = True)
```

## Convert media
Finally, when you have your recorded media you may want to convert it. Videos are automatically recorded in the `.h264` format and may need converting to `.mp4` to be easily viewable. If you have recorded a timelapse of images you may also want to convert that to a video. Or maybe you want to add framenumbers to the frames of a video to later accurately determine certain events. You can use the `convert` module for all these commands, which also works on non-raspberry pi systems and can be run straight from the terminal. For example, to convert a folder of videos:

```
convert --indir VIDEOS --outdir VIDEOS/CONVERTED
```
