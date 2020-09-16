---
layout: page
title: 4 Configure recording settings
nav_order: 6
---
# Configure recording settings
{: .no_toc }

When you have pirecorder running and have positioned your camera, the next thing you may want to do is change the default recording settings. Below I guide you through the various options.
{: .fs-6 .fw-300 }

## Table of contents
{: .no_toc .text-delta .fs-4 .fw-300 }

1. TOC
{:toc}
---

## Working with the configuration file
As is explained in the [pirecorder package page](pirecorder-package.md), one of the main features of PiRecorder is that it works with a simple-to-use configuration file to set all your camera and recording settings to easily run repeated and automated recordings.

The configuration file can be set with the `configfile` parameter when initiating the PiRecorder instance, which defaults to "pirecorder.conf". For example, to work with a special config file for infrared recordings, you can run:

```
import pirecorder
rec = pirecorder.PiRecorder(configfile = "irsettings.conf")
```

The configuration files can be simply changed manually with any text editor or with your favorite terminal editor (e.g. `nano pirecorder/pirecorder.conf`). You can also easily update the configuration via the `settings` function and only add the parameters you want to change. For example:

```
rec.settings(label="test", rectype="img")
```

An overview of all the recording parameters with concise description that are possible to set is provided at the bottom of this page and can also be called directly in Python:

```
print(rec.settings.__doc__)
```

To see your current configuration settings, simply type in:

```
print(rec.config)
```

## Where and what to record
Two important configurations to set are the `recdir` and `rectype` parameters. By default PiRecorder will store all media in a recordings folder inside the pirecorder folder (`pirecorder/recordings`). You can change this to any folder name that you like. If no name is provided, the files will be directly stored in the users' home directory. If you want to store media on a mounted media, name the mounted folder "NAS" and use `recdir = "NAS"`, then it will automatically check if it is mounted and otherwise record in the default location.

With PiRecorder you can record single images (`rectype = img`), a sequence/timelapse of images (`rectype = imgseq`), a single video (`rectype = vid`), or multiple sessions of videos (`rectype = vidseq`). The "vidseq" recording type will record multiple videos with the same recording settings but wait after each finished recording for user input to continue with the next recording or exit. Each new video will be treated as a new "session" and have a corresponding session number in its filename (e.g. "S01", "S02" etc). The benefit of this recording option is that it is even quicker to record multiple videos one after the other with the same parameters and to have a simple automatic filenaming system that keeps those videos together.

## Automatic naming of files
The naming of the (folders of) recorded images and videos is all done automatically. Each filename will include a user-provided label that can be set with the `label` parameter, the host computer name, the date, the time and potentially the session number or count nr. For example, single images will have a filename like `test_200601_pi13_101300.jpg`, image sequences `test_200601_pi13_img00231_101300.jpg` and videos `test_180312_pi3_S01_101300.h264`.

The `subdirs` parameter makes it possible to automatically store the files of each separate recording in its own folder with a unique filename. This is especially helpful when recording image sequences of video sequences, such that those files are all stored together in their own folder.

## Settings for image recording
To set the resolution for images you can use the `imgdims` parameter, which defaults to the maximum resolution for the v1.5 camera model (2592, 1944). The v2 model has a max resolution of 3280 x 2464 pixels, and the hq camera 4056 x 3040 pixels. The `imgquality` parameter specifies the quality that the jpeg encoder should attempt to maintain. Use values between 1 and 100, where higher values are higher quality. Playing with this setting can help to considerably reduce the file size of your recordings while keeping the same quality.

To control your image sequences you can set three parameters: `imgnr`, `imgtime`, and `imgwait`. PiRecorder will use the minimum of `imgnr` and the nr of images based on `imgwait` and `imgtime`. When the value provided for imgwait is too low relative to the provided shutterspeed it will be automatically set to the minimum value of 0.45s. With a fast enough shutterspeed it is possible to record multiple images per second, but depends on the model of raspberry pi you use. Also, when a delay is provided that is less than ~x5 the shutterspeed, the camera processing time will take more time than the provided imgwait parameter and so images are taken immediately one after the other. To take a sequence of images at the exact right delay interval the imgwait parameter should be at least 5x the shutterspeed (e.g. shutterspeed of 400ms needs imgwait of 2s.

For example, to record a sequence of 10 images at very high resolution at 1 image a minute:

```
rec.settings(imgwait = 1, imgnr = 10, imgtime = 15, imgwait = 60, imgquality = 90 \
             imgdims = (3280, 2464))
rec.record()
```

## Settings for video recording
For recording video you can set the `vidduration` and `viddelay` to get the right recording duration. The viddelay is extra recording time in seconds that will be added to vidduration. Its use is to add a standard amount of time to the video that can be easily cropped or skipped, such as for tracking, but still provides useful information.

To set the resolution for video recording use the `viddims` parameter. Note that the maximum video resolution for all currently existing raspberry pi camera's ("v1","v2" and "hq") is 1080p, but that it is also possible to record in a different format as long as the total number of pixels does not exceed that, such as 1640 x 1232.

To set the framerate of the video use the `vidfps` parameter. With smaller resolutions higher framerates are possible, see [this page](https://picamera.readthedocs.io/en/release-1.13/fov.html#camera-modes) for more information. 40fps with the max resolution of 1640 x 1232, and 90fps with 1280 x 720 is possible but may result in dropped frame, so it is safer to stay just slightly below that.

The `vidquality` parameter specifies the quality that the h264 encoder should attempt to maintain. Use values between 10 and 40, where 10 is extremely high quality, and 40 is extremely low.

For example, to take a single video for 10 minutes with 20s extra time, with a 1640x1232 resolution at 24fps, with a relatively low quality and thus file size:

```
rec.set_config(rectype = "vid", vidduration = 600, viddelay = 20, vidquality = 30 \
               viddims = (1640, 1232), vidfps = 24)
rec.record()
```

---
Recording settings documentation
{: .text-delta .fs-5}
```
Parameters
---------------
recdir : str, default = "pirecorder/recordings"
    The directory where media will be stored. Default is "recordings". If
    different, a folder with name corresponding to location will be created
    inside the home directory. If no name is provided (""), the files are
    stored in the home directory. If "NAS" is provided it will additionally
    check if the folder links to a mounted drive.
subdirs : bool, default = False
    If files of individual recordings should be stored in subdirectories
    or not, to keep all files of a single recording session together.
label : str, default = "test"
    Label that will be associated with the specific recording and stored in
    the filenames.
rectype : ["img", "imgseq", "vid", "vidseq"], default = "img"
    Recording type, either a single image or video or a sequence of images
    or videos.
cameratype : str, default = None
    The raspberry cameratype used. Can be either None, "v1", "v2", or "hq"
    to indicate the different models and will help set the maximum recording
    resolution.
imgdims : tuple, default = (2592, 1944)
    The resolution of the images to be taken in pixels. The default is the
    max resolution for the v1.5 model, the v2 model has a max resolution of
    3280 x 2464 pixels, and the hq camera 4056 x 3040 pixels.
viddims : tuple, default = (1640, 1232)
    The resolution of the videos to be taken in pixels. The default is the
    max resolution that does not return an error for this mode.
imgfps : int, default = 1
    The framerate for recording images. Will be set automatically based on
    the imgwait setting so should not be set by user.
vidfps : int, default = 24
    The framerate for recording video.
imgwait : float, default = 5.0
  The delay between subsequent images in seconds. When a delay is provided
    that is less than ~x5 the shutterspeed, the camera processing time will
    take more time than the provided imgwait parameter and so images are
    taken immideately one after the other. To take a sequence of images at
    the exact right delay interval the imgwait parameter should be at least
    5x the shutterspeed (e.g. shutterspeed of 400ms needs imgwait of 2s).
imgnr : int, default = 12
    The number of images that should be taken. When this number is reached,
    the recorder will automatically terminate.
imgtime : integer, default = 60
    The time in seconds during which images should be taken. The minimum of
    a) imgnr and b) nr of images based on imgwait and imgtime will be used.
imgquality : int, default = 50
    Specifies the quality that the jpeg encoder should attempt to maintain.
    Use values between 1 and 100, where higher values are higher quality.
vidduration : int, default = 10
    Duration of video recording in seconds.
viddelay : int, default = 0
    Extra recording time in seconds that will be added to vidduration. Its
    use is to add a standard amount of time to the video that can be easily
    cropped or skipped, such as for tracking, but still provides useful
    information, such as behaviour during acclimation.
vidquality : int, default = 11
    Specifies the quality that the h264 encoder should attempt to maintain.
    Use values between 10 and 40, where 10 is extremely high quality, and
    40 is extremely low.
```
