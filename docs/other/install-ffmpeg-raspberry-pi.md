---
layout: page
title: Install ffmpeg on RPi
parent: Other guides
nav_order: 11
---

# Installing ffmpeg on raspberry pi with .h264 support
{: .no_toc }

The raspberry pi is great for recording video. One issue however is that the `.h264` container it records in is hard to work with. It is therefore often desirable to convert videos to widely applicable formats like `.mp4` to be able to view them properly and get the right meta information. For this I recommend the program `FFmpeg`.

The `pirecorder` package also comes with a special `Convert` class with a number of helpful functionalities to make it very easy to convert videos, folders of videos as well as images to video. See the guide [here](7-convert-media.md).

Installing [FFmpeg](https://www.ffmpeg.org) on a Raspberry Pi is not as simple as downloading an executable from the command line, but it is also not too difficult. Follow these steps:

## Table of contents
{: .no_toc .text-delta .fs-4 .fw-300 }

1. TOC
{:toc}
---

## Install h264 library
Open a terminal window on the raspberrypi (or via SSH connection) and type in the following commands:
* Download h264 library:
```
git clone --depth 1 https://code.videolan.org/videolan/x264
```
* Change directory to the x264 folder:
```
cd x264
```
* Configure installation:
```
./configure --host=arm-unknown-linux-gnueabi --enable-static --disable-opencl
```
* Create the installation:
```
make -j4
```

* Install h264 library on your system:
```
sudo make install
```

## Install ffmpeg with h264
* Change to home directory:
```
cd ~
```
* Download ffmpeg:
```
git clone git://source.ffmpeg.org/ffmpeg --depth=1
```
* Change to ffmpeg directory:
```
cd ffmpg
```
* Configure installation:
```
./configure --arch=armel --target-os=linux --enable-gpl --enable-libx264 --enable-nonfree
```
* Make the installation:
```
make -j4
```
*Note this step may take a long time!*
* Now finally run the installation:
```
sudo make install
```

There are many options available and many other ways to convert h264 videos with ffmpeg, but this command is the quickest of all methods that I tested.

Note: If you are working with an older model of the raspberrypi (&lt; 3 B+) then you may not have 4 cores available. You will then have to change `make -j4` to `make -j`.

## Convert (h264) video
Now you are ready to convert (h264) videos on your Raspberry Pi. To simply convert a single video:

```
ffmpeg -i USER_VIDEO.h264 -vcodec copy USER_VIDEO.mp4
```

The `Convert` class of the pirecorder package builds on ffmpeg and added a number of functionalities to make it easier to help you convert your media, especially as recorded with `pirecorder`. Read its documentation [here](https://github.com/JolleJolles/pirecorder/wiki/pirecorder-convert/).
