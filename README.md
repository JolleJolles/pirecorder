[![PyPI version](https://badge.fury.io/py/pirecorder.svg)](https://badge.fury.io/py/pirecorder) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.2529515.svg)](https://doi.org/10.5281/zenodo.2529515)

# pirecorder
**A python module for controlled and automated image and video recording with the raspberry pi**

*pirecorder* is a package to facilitate controlled and automated image and video recording for the Raspberry Pi (rpi), specifically developed with the Behavioural Scientist in mind.

<p align="center"><img src="https://github.com/JolleJolles/pirecorder/blob/master/images/pirecorder-logo.jpg"></p>

*pirecorder* consists of a main `PiRecorder` class and a number of additional [submodules](#submodules) that facilitate setting up the Raspberry Pi camera, configuring the camera, scheduling future recordings, and converting recorded media. It helps get optimal recording settings and stores these such that they can be easily updated by the user via python or a text file. Subsequently, these settings can be used to make standardised recordings by user command or via a user-set schedule of recordings.

*pirecorder* is build to make controlled and automated recordings as simple as possible. It is fully usable by simple terminal commands without needing to go into python (via `calibrate`,`record`, `schedule`, and `convert`). The package also comes with detailed documentation and tutorials that are continuously updated with the aim to help people with limited coding knowledge to set up their rpi and make controlled and automated image and video recordings. See the detailed [wiki](https://github.com/JolleJolles/pirecorder/wiki).


## <a name="install"></a>Install

PiRecorder is easy to install. Simply open a terminal window and enter:

```bash
pip install pirecorder
```

All dependencies (see below) will be automatically installed with *pirecorder* except for:

- *picamera*: To enable *pirecorder* to be installable on non-rpi systems such as to use the convert functionality
- *opencv*: Opencv has to be manually installed due to various dependencies. Click [here](https://github.com/JolleJolles/pirecorder/wiki/Install-OpenCV-for-Python-on-Mac,-Ubuntu,-Raspberry-Pi) for my opencv installation guide.
- *ffmpeg*: ffmpeg is needed only for using the convert functionality of *pirecorder* and needs to be installed manually. Click [here](https://github.com/JolleJolles/pirecorder/wiki/Installing-ffmpeg-on-Mac-OS-X) for my guide to install on OS X and [here](https://github.com/JolleJolles/pirecorder/wiki/Installing-ffmpeg-on-Raspberry-Pi-with-h264-support) for my guide to install on raspberry pi.

**See the [pirecorder wiki](https://github.com/JolleJolles/pirecorder/wiki) for a detailed guide for setting up your raspberry pi and installing and working with pirecorder.**

## Dependencies
*pirecorder* is both Python 2.7 and 3 compatible. It builds strongly on the [picamera](http://picamera.readthedocs.io/) package, uses [numpy](http://www.numpy.org/), [pyyaml](https://pyyaml.org), and [opencv](http://opencv.org) for some of its core functionality, and relies on various utility functions of my [pythutils](https://github.com/JolleJolles/pythutils) package. The scheduling functionality is baded on *CronTab* and the associated [python-crontab](https://pypi.org/project/python-crontab/) package.

## Module overview

### Recorder class
The main functionality of *pirecorder* is the `PiRecorder` class. This class initiates a Recorder instance that sets up the Raspberry Pi to record either A) a single image, b) a sequence of images, C) a single video, or D) sessions of video recordings.

There are many custom recording parameters that can be set with the `PiRecorder` class, which are divided into 1) general user recording parameters, 2) camera settings, 3) video recording settings, 4) image recording settings, and 5) custom settings linked to the specific rpi being used. A detailed overview and description of all these settings can be found by calling `print(pirecorder.PiRecorder.__doc__)`.

When the `PiRecorder` is run for the first time, it creates a `pirecorder` setup directory in the user's home folder to store all relevant setup files. Central is the default configuration file `pirecorder.conf`. *PiRecorder* is set up in such a way that it is very easy to set and save custom settings that are then automatically used for future use without further user input.

Multiple configuration files can be created and called for specific recording settings and the configuration file(s) can be easily edited with any text editor as well as updated from the command line with the `set_config()` method. In addition the setup directory will contain a log file *pirecorder.log* that will store all terminal output when *PiRecorder* is used to help keep a history log of your recordings.

### Recording modes
`PiRecorder` has four recording modes (set with `rectype`):

1. `img`: Records a single image with the custom settings and then quits.
2. `imgseq`: Creates a controlled sequence of images based on either a set duration (setting `imgtime`) or total number of images to be recorded (setting `imgnr`) with a certain delay between images (setting `imgwait`).
3. `vid` : Records a single video. Specific settings that can be set for this mode are `vidfps`, the framerate of the video; `vidduration`, the duration of the video; and `viddelay`, extra recording time in seconds that will be added to vidduration.
4. `vidseq`: Starts a series of standardized videos using the custom settings. After each recording has finished, the user is asked with a keypress if a new recording should be started or exit.

Files are automatically stored in the configured directory (`recdir`), by default a directory called `recordings` in the pirecorder directory, and are automatically named according to the provided `label`, the computer name, the date and time, and potentially the session number or image sequence nr.

### <a name="submodules"></a>Submodules
In addition to the main recording module, *pirecorder* contains a number of modules to facilitate setting-up the Raspberry Pi camera, configuring the camera, and schedule future recordings, with more functionalities to be integrated in the future, see the planned enhancements [here](https://github.com/JolleJolles/pirecorder/labels/enhancement).

- `calibrate()`: Opens a live video stream with user interface to calibrate the raspberry pi camera in terms of its position, focus, and region of interest (roi).
- `set_gains()`: Function to calibrate the red and blue color balance either automatically or dynamically using a live video stream with user interface.
- `record`: Start a recording using the stored configuration settings. If initiated for the first time, the default configuration file will be created (`pirecorder/pirecorder.conf`). This file can be simply updated with a text editor (e.g. via `sudo nano`).
- `schedule()`: Automatically start image and video recording in the future according to custom recording schedules.
- `convert`: Convert images or videos to (resized) videos (with timestamps)

## Development
*pirecorder* is developed by [Dr Jolle Jolles](http://jollejolles.com) at the Max Planck Institute of Animal Behavior, Konstanz, Germany.

For an overview of version changes see the [CHANGELOG](https://github.com/JolleJolles/pirecorder/blob/master/CHANGELOG) and for detailed changes see the [commits page](https://github.com/JolleJolles/pirecorder/commits/). Please submit bugs or feature requests to the GitHub issue tracker [here](https://github.com/JolleJolles/pirecorder/issues).

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
Released under a Apache 2.0 License. See [LICENSE](https://github.com/JolleJolles/pirecorder/blob/master/LICENSE) for details.
