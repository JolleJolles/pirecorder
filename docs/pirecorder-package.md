---
layout: page
title: The pirecorder package
nav_order: 2
---
# The pirecorder package
{: .no_toc }

*pirecorder* is a Python package with a number of inter-connected modules, developed with the aim to facilitate running controlled and automatic image and video recordings using optimal settings with the raspberry pi.
{: .fs-6 .fw-300 }

The package consists of a main `PiRecorder` module to run recordings, `stream` and `camconfig` modules for help setting up, calibrating, and configuring the camera, a `schedule` module for scheduling future recordings, and a `convert` module for the easy converting of (folders of) recorded images and videos.

A core component of *pirecorder* is that it uses configuration files and timeplans that can be easily called, modified, and stored by the user, with automatic naming of files and folders. *pirecorder* also works directly from the terminal without the need to code in Python (see [this page](8-run-from-commandline.md) and comes with detailed documentation and tutorials (this website). This also has the aim to further help people with limited coding experience to set up their raspberry pi and make controlled and automated recordings.


## Table of contents
{: .no_toc .text-delta .fs-4 .fw-300 }

1. TOC
{:toc}
---

## Quick install

pirecorder can be easily installed with pip, which should already be automatically installed on your system. To install the latest release, simply open a terminal window and enter:

```
pip install pirecorder
```

To install the latest development version, enter:

```
pip install git+https://github.com/jollejolles/pirecorder.git --upgrade
```

See the [quick usage guide](quick-guide.md) for quickly getting you up and running or the [setting-up your raspberry pi](1-setting-up-raspberry-pi.md) and [installing pirecorder](2-installing-pirecorder.md) pages for more in-depth documentation and tutorials.

## Dependencies
*pirecorder* is both Python 2.7 and 3 compatible. It builds strongly on the [picamera](http://picamera.readthedocs.io/) package, uses [numpy](http://www.numpy.org/), [pyyaml](https://pyyaml.org), and [opencv](http://opencv.org) for some of its core functionality, and relies on various utility functions of my [pythutils](https://github.com/JolleJolles/pythutils) package. The scheduling functionality is based on *CronTab* and the associated [python-crontab](https://pypi.org/project/python-crontab/) package.

All dependencies are automatically installed with *pirecorder* except for:
* *OpenCV*: has to be manually installed due to various dependencies on the raspberry pi. Click [here](other/install-opencv.md) for a quick install guide.
* *FFmpeg*: is only needed for the convert functionality of *pirecorder*, so if you plan on using that functionality you should make sure it is installed. Click [here](other/install-ffmpeg-raspberry-pi.md) for my guide to install it on raspberry pi and [here](other/install-ffmpeg-osx.md) for my guide to install it on OS X.

## PiRecorder module
The main functionality of *pirecorder* is the `PiRecorder` module. This class initiates a PiRecorder instance that sets up the raspberry pi to record either A) a single image, b) a sequence of images, C) a single video, or D) a session of video recordings. When `PiRecorder` is run for the first time, it creates a "pirecorder" setup directory in the user's home folder to store all relevant setup files. This includes the default configuration file (*pirecorder.conf*) with all recording and camera settings as well as a log file (*pirecorder.log*) that will store all terminal output when `PiRecorder` is used to help keep a history log of your recordings.

### Configuration file
*PiRecorder* is set up in such a way that it is very easy to set and save custom recording and camera settings that are then automatically used for future recordings without further user input. Multiple configuration files can be created and called for specific recording settings and the configuration file(s) can be easily edited with any text editor as well as updated from the command line with the `settings` function.

A large number of custom recording parameters can be set, divided into 1) general user recording parameters, 2) camera settings, 3) video recording settings, 4) image recording settings, and 5) custom settings. A detailed overview and description of all the configuration settings can be found by calling `print(pirecorder.PiRecorder.settings.__doc__)` in Python and is explained in-depth in the [configure recording settings](4-configure-recording-settings.md) and the [configure camera settings](5-configure-camera-settings.md) guides.

### Recording modes
There are four recording modes, which can be set with the `rectype` parameter:

1. `img`: Records a single image with the custom settings.
2. `imgseq`: Creates a controlled sequence of images (i.e. timelapse) based on A) the set duration (`imgtime`) and B) the set total number of images to be recorded (`imgnr`) and the provided time delay between images (`imgwait`).
3. `vid`: Records a single video. Specific settings that can be set for this mode are `vidfps` (the framerate of the video), `vidduration` (the duration of the video), and `viddelay` (extra recording time in seconds that will be added to vidduration).
4. `vidseq`: Starts a series of standardized videos using the custom settings whereby, after each recording has ended, the user is asked if a new recording should be started or the program should exit.

### Automatic file naming
Files are automatically stored in the configured directory (`recdir`), by default a directory called `recordings` in the pirecorder directory, and named according to the provided `label`, the computer name, the date and time, and potentially the session number or image sequence number.

## Other modules
In addition to the main recording module, *pirecorder* contains a number of modules to facilitate setting-up and configuring the raspberry pi camera, schedule future recordings, and convert recorded media:

- `stream`: Opens a live video stream with user interface to calibrate the raspberry pi camera in terms of its position, focus, and region of interest (roi). For more detail, see the [calibrate camera page](3-position-and-calibrate-camera.md).
- `camconfig`: Opens a live video stream with user interface to dynamically, both manually and automatically, set the camera settings, including camera rotation, shutterspeed, whitebalance, iso, exposure compensation, brightness, contrast, saturation, and sharpness. For more detail, see the [configure camera settings page](5-configure-camera-settings.md)
- `schedule`: Automatically start image and video recording in the future according to custom recording schedules. For more detail, see the [schedule recordings page](6-recording-and-scheduling.md).
- `convert`: Convert (folders of) images or videos to videos with the option to resize, add timestamps on each frame, and monitor folders for automatic conversion. For more detail, see the [convert media page](7-convert-media.md).

## Development
*pirecorder* is developed by Dr Jolle Jolles, a research fellow at the Max Planck Institute of Animal Behavior, and at the Zukunftskolleg, Institute of Advanced Study at the University of Konstanz. For more information about his work, see his [academic website](http://jollejolles.com) or his [google scholar profile](https://scholar.google.nl/citations?user=VCZqbK4AAAAJ).

For an overview of version changes see the [CHANGELOG](https://github.com/jollejolles/pirecorder/blob/master/CHANGELOG) and for detailed changes see the [commits page](https://github.com/jollejolles/pirecorder/commits/).

Please submit bugs or feature requests to the GitHub issue tracker [here](https://github.com/jollejolles/pirecorder/issues).

## Citing
If you use pirecorder in your research, please cite it as follows:

```
@misc{Jolles2019,
      title = {pirecorder: controlled and automated image and video recording with the raspberry pi},
      author = {Jolles, Jolle W.},
      year = {2019}
      url = {http://doi.org/10.5281/zenodo.2529515},
      doi = {10.5281/zenodo.2529515}
}
```

## License
Released under a Apache 2.0 License. See [LICENSE](https://github.com/jollejolles/pirecorder/blob/master/LICENSE) for details.
