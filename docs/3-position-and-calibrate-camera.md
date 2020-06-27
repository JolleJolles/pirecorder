---
layout: page
title: 3 Position and calibrate the camera
nav_order: 5
---

# Calibrate the camera
{: .no_toc }

If pirecorder is successfully installed on your raspberry pi, the next thing you may want to do is properly position and calibrate your camera. This page will explain the various ways in which pirecorder can help with that. Note that the stream functionality also works on non-raspberry pi systems.
{: .fs-6 .fw-300 }

## Table of contents
{: .no_toc .text-delta .fs-4 .fw-300 }

1. TOC
{:toc}
---

## Overview of the pirecorder stream functionality
pirecorder comes with a `stream` module that displays an interactive live video stream on the desktop to help position the raspberry pi camera and objects in the camera view, draw a region of interest to be used for recordings, and zoom in on part of the video. It records the clicks and movements of the mouse and responds to the following keypresses:

- `f`-key: Display the stream fullscreen/display the stream in a window
- `c`-key: Display/hide a diagonal cross across the screen
- `s`-key: Save the coordinates of the rectangular area when drawn
- `e`-key: Erase the rectangular area when drawn
- `z`-key: Show a zoomed-in section of the video inside the rectangular area in maximum resolution
- `n`-key: Refresh the zoom-in image
- `o`-key: If the potential overlay image should be shown or not
- `[`- and `]`-keys: Decrease or increase the relative opacity of the potential overlay image with 5%
- `esc`-key: Exit the the zoom window as well as the calibrate function completely

The `stream` module can be run independently:
```
import pirecorder
pirecorder.Stream()
```

as part of a `PiRecorder` instance:
```
import pirecorder
rec = pirecorder.PiRecorder()
rec.stream()
```

and directly from the command line:
```
stream
```

If using the `stream` module to store the region of interest it needs to be run as part of a `PiRecorder` instance.

## Adjust the stream settings
There are a 5 parameters you can set for the video stream:
- `cameratype`: By providing this parameter the maximum resolution of the raspberry pi camera will be automatically determined. The default is "v2". Other possible values are "v1" and "hq".
- `vidsize`: Sets the size of the stream display window proportional to the maximum resolution of the provided camera type. The smaller the vidsize parameter, the more likely the video stream will run smoothly.
- `framerate`: By default the video stream will have a framerate of 8fps. A lower framerate may be desirable on older raspberry pi models. The maximum possible framerate is 5 when using an image overlay.
- `rotation`: This parameter enables showing the video stream in normal orientation (`0`) or up-side-down (`180`).
- `imgoverlay`: This parameter makes it possible to show an image overlay on the live video stream, which is further detailed below.

For example, to show a video stream in a relatively small window at a framerate of 15fps up-side down for a raspberry pi with a "v1" camera connected:

```
pirecorder.Stream(cameratype="v1", vidsize=0.2, framerate=15, rotation=180)
```

## Overlay an image on the video stream
It is also possible to overlay an image on the video stream. This can be highly beneficial to help position the camera exactly like in a previous recording or arrange objects in the field of view of the camera exactly like before, such as a custom maze for behavioural experiments.

To overlay an image, simply add the path to the image file to the `imgoverlay` parameter. The image will be stretched to have the same dimensions as the video stream. By default it will be shown with an opacity of 0.5 (range 0-1). The opacity can be reduced and increased interactively with the `[` and `]` keys.

## Positioning the camera
The stream function comes with the option to display a simple diagonal white cross, which can help to accurately position the camera or objects of interest below the camera. Simple toggle the cross with the `c`-key.

## Setting the region of interest
Clicking and drawing the mouse will draw a rectangular area. This can be used directly to store the coordinates of the region of interest that should be used for recordings, i.e. to only record the region inside the rectangular area.

Simply draw and redraw the rectangular area until you are happy and press the `s`-key. Now the coordinates of the region of interest will be displayed and, if running the `stream` functionality from a `PiRecorder` instance, stored automatically in the configuration file (e.g. `rec.config.cus.roi`). If you stored the region of interest accidentally or want to remove the drawn rectangle simple enter the `e`-key. To exit press the `esc`-key.

## Show a zoomed-in region at full resolution
Besides drawing the rectangular area for creating a region of interest for recordings, it can also be used to zoom-in on part of the video at the maximum image resolution. This can be very helpful to help you improve the focus of the raspberry pi camera. To do so, simply draw a rectangular area around the region you want to zoom-in to with the mouse and when satisfied press the `z`-key. Now a second window will open that will show the zoomed-in region of the video as an image.

As this is at the maximum image resolution, which is a lot higher than the maximum video resolution, it will only show a static image, but thus with much more detail than the video stream. You can refresh the image by pressing the `n`-key. To exit, press the `esc`-key.

---
Stream module documentation
{: .text-delta .fs-5}

```
Opens a video stream with user interface to help position and
adjust the camera

parameters
-----------
system : str, default = "auto"
    If the system should be automatically determined. Should detect if
    the computer is a raspberry pi or not. If this somehow fails, set
    to "rpi" manually.
framerate : int, default = 8
    The framerate of the displayed video stream. Lower framerates take
    longer to start up. When using an image overlay, maximum possible
    framerate is 5, to avoid getting shutter effects
vidsize : float, default = 0.2
    The relative size of the video window to the maximum resolution of
    the raspberry pi camera type.
rotation : int, default = 180
    If the camera should be rotated or not. 0 and 180 are valid values.
cameratype : str, default = "v2"
    The raspberry camera type used. Should be either "v1", "v2", or "hq"
imgoverlay : str, default = None
    The path to an image that will be overlaid on the video stream. This
    can be helpful for accurate positioning of the camera in line with
    previous recordings or setups.

interface
-----------
This interactive module stores mouse position and clicks and responds to
the following keypresses:
f-key : display the stream fullscreen/display the stream in a window
c-key : display/hide a diagonal cross across the screen
s-key : save the coordinates of the rectangular area when drawn
e-key : erase the rectangular area when drawn
z-key : show a zoomed-in section of the video inside the rectangular
    area in maximum resolution
n-key : refresh the zoom-in image
o-key : if the potential overlay image should be shown or not
[- and ]-keys : decrease or increase the relative opacity of the
    potential overlay image with 5%
esc-key : exit the the zoom window; exit the calibrate function
```
