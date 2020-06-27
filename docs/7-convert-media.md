---
layout: page
title: 7 Converting media
nav_order: 9
---
# Convert image and video files
{: .no_toc }

The convert module of the *pirecorder* package facilitates the converting of recorded media, both of individual images and videos as well as directories of videos, with the ability to resize, add timestamps on each frame, and monitor folders for automatic conversion. It can be set to optimally use the number of computer cores available, can be run directly from the command line, and works across different operating systems.
{: .fs-6 .fw-300 }

## Table of contents
{: .no_toc .text-delta .fs-4 .fw-300 }

1. TOC
{:toc}
---

## Install dependencies

As dependencies both `FFmpeg` and `OpenCV` are needed to optimally convert the different media types. To help install FFmpeg on raspberry pi follow [this guide](other/install-ffmpeg-raspberry-pi.md), to install ffmpeg on os X follow [this guide](other/install-ffmpeg-osx.md), and to install OpenCV, follow [this guide](other/install-opencv.md).

## Convert a directory of videos
To convert a directory of videos, simply import and run the `Convert` module and provide the directory where the media files are located (`indir` parameter), and where you want to store them (`outdir` parameter). This conversion is very fast. By default it will look for files with filetype "h264", but this can be changed with the `type` parameter. For example, to convert all videos in a folder called `videos` and store them in a nested folder called `converted` run:

```
from pirecorder import Convert
Convert(indir = "videos", outdir = "videos/converted")
```

If the `outdir` does not exist it will be automatically created. By default, videos that are converted will not be overwritten (`overwrite=False`). Therefore, if some or all videos in the `indir` are already converted it will skip those automatically.

## Continuously monitor a folder for new files
With the `Convert` module it is also possible to continuously monitor a folder for new files with a set delay to wait between subsequent checks. This makes it easy to integrate with an automated media recording workflow. Simply add `sleeptime=XX` where `XX` is the time in seconds between subsequent checks.

## Convert images to video

Using the `Convert` module it is also easy to convert a directory of (timelapse) images to video. For this you need to set the `type` parameter to the image format you use, and set the `imgfps` parameter to the desired framerate of the video. For example, to create a video of 10fps:

```
Convert(indir = "media/vidimages", outdir = "media", type = ".png", imgfps = 10)
```

To then for example change the framerate to 30fps, simple run:

```
Convert(indir = "media/vidimages", outdir = "media", type = ".png", imgfps = 30, overwrite = True)
```

To convert a folder consisting of multiple image folders, you can use the `listfiles` function from my [pythutils package](https://github.com/jollejolles/pythutils), which is automatically installed with `pirecorder`, as follows:

```
imagedirs = listfiles(dir = "parentdir", type = "dir", keepdir = True)
for imagedir in imagedirs:
    Convert(indir = imagedir, outdir = "converted", type = ".png")
```

## Set number of converting pools
The `Convert` module can run multiple conversions at the same time. This works optimally when linked to the number of processing cores of the computer being used. By default it will presume a minimum of 4 cores are available. To change this, use the `pools` parameter, e.g. `pools = 6`. When running the convert functionality from python you can stop the converting by entering `ctrl+c`, and when running it in a jupyter notebook simply press the stop button in the menu bar.

## Delete originals
By default the original videos are not deleted. If you want this to be done automatically, such as when you incorporate the `Convert` module in your own automation functions, then add `delete = True`. Be careful to test your desired functionality first to not loose any unwanted data!

## Display frame number on each frame
To display the frame number on the top-left corner of each frame, simply add `withframe = True`. The conversion will now be a bit slower as it will go through each frame to draw the frame number, but due to the pooling should still work fine.

## Resize the video
By default the generated media will have the same dimensions as the originals. However, these dimensions can be decreased (as well as increased if needed), such as when wanting to reduce the file size. To do so use the `resizeval` parameter, which defaults to 1 to keep the same size. For example, to create a video with half the dimensions of the originals use `resizeval = 0.5`.

## Convert directly from the command line
When pirecorder is installed it is also possible to use the pirecorder convert functionality straight from the command line using the `convert` command, just like any other native command. You can use the same parameters as when running the `Convert` command in python, e.g.:

```
convert --indir VIDEOS --outdir CONVERTED --type ".h264" --withframe True /
--pools 4 --resizeval 0.5 --sleeptime 5 --delete False
```

---
Convert module documentation
{: .text-delta .fs-5}

```
Module to convert a directory of media files with potential to resize the
media, write the unique frame number on each frame, and continuously monitor
a folder for updated files. Multiple files can be converted simultaneously
with the pools parameter that optimally uses the computer's processing cores.

Parameters
-----------
indir : str, default = ""
    Directory containing the videos.
outdir : str, default = ""
    Directory where the converted videos should be stored. If the Directory
    does not exist yet it will be newly created.
type : str, default = ".h264"
    The filetype of the media to convert.
withframe : bool, default = False
    Type of conversion, either very fast conversion using FFmpeg or
    using OpenCV to draw the frame number on each video frame.
delete : bool, default = False
    If the original videos should be delete or not.
pools : int, default = 4
    Number of simultaneous converting processing that should be allowed.
    Works optimally when equal to the number of computer processing cores.
resizeval : float, default = 1
    Float value to which video should be resized.
imgfps : int, default = 25
    Framerate for conversion of images to video.
sleeptime : 2, default = None
    Time in seconds between subsequent checks of file folder. To not
    continuously monitor a folder set to None.
```
