# AnimRec
**A python module for controlled image and video recording for the Rasperry Pi**

![logo](https://github.com/JolleJolles/animrec/blob/master/animrec-logo.jpg)

*AnimRec* is a package to facilitate controlled and automated video recording using raspberry pi (rpi). It was specifically designed with the Behavioural Scientist in mind or like-minded people that have a wish for easy automed recording but may not have the required knowledge or coding skills at hand.

*AnimRec* consists of a main recorder class and a number of [helper methods](#othmethods) that facilitate setting-up the Raspberry Pi camera, configuring the camera, scheduling future recordings, and converting recorded media. *AnimRec* also contains detailed documentation and tutorials that are continuously updated with the aim to help people with very limited coding knowledge to set-up their rpi, install the required packaged, and get working with *AnimRec*.

**[Click here](https://github.com/JolleJolles/animrec/tree/master/animrec-guide.md) for a detailed and an easy-to-follow guide to start setting-up your rpi and installing AnimRec, with detailed explanation of all its functionalities.**

Dependencies
------------
*AnimRec* is written in [Python](http://www.python.org) and is both Python 2.7 and 3 compatible. It builds strongly on the [picamera](http://picamera.readthedocs.io/) package and makes use of various utility functions of my [AnimLab](https://github.com/JolleJolles/animlab) package. The scheduling functionality is baded on *CronTab* and the associated [python-crontab](https://pypi.org/project/python-crontab/) package. Converting requires [ffmpeg](https://www.ffmpeg.org) and [OpenCV](http://opencv.org/). For detailed steps to get these dependencies, follow the setting-up guide [here](https://github.com/JolleJolles/animrec/tree/master/animrec-guide.md). 

- [Python 2.7 or 3.x](http://www.python.org)

- [picamera](http://picamera.readthedocs.io/)

- [AnimLab](https://github.com/JolleJolles/animlab)

- [numpy](http://www.numpy.org/)

- [pandas](http://pandas.pydata.org)

- [pyyaml](https://pyyaml.org)

- [OpenCV](http://opencv.org/)

- [python-crontab](https://pypi.org/project/python-crontab/)

- [ffmpeg](https://www.ffmpeg.org)

Citing
------------
*AnimRec* should be of interest to the broader academic community and the general code-minded public. If you use *AnimRec*, do let me know, I'd love to hear how you like and use it. Also please cite the software using the following DOI:

*Jolles, J. W. (2019) AnimRec: A python module for controlled image and video recording for the Rasperry Pi v1.1.0. Zenodo. https://doi.org/10.5281/zenodo.2529515*

[![DOI](https://zenodo.org/badge/163422997.svg)](https://zenodo.org/badge/latestdoi/163422997)


<a name="install"></a>Quick install
------------

Open a terminal window and enter:

```bash
pip install git+https://github.com/JolleJolles/animrec.git
```

*Note: please keep in mind its dependencies. If you are relatively new to working with Python or raspberry pi, please follow the setting-up guide [here](https://github.com/JolleJolles/animrec/tree/master/notebooks/setting-up.ipynb).*


AnimRec overview
------------

### Recorder class
The main functionality of *AnimRec* is the `Recorder` class. This class initiates a Recorder instance that sets up the Raspberry Pi to record either A) a single image, b) a sequence of images, or C) a loop of videos. There are many custom recording parameters that can be set with the animrec.Recorder class, which are divided into 1) general user recording parameters, 2) camera settings, 3) specific video and 4) specific image recording settings, and 5) custom settings linked to the specific rpi being used. A detailed overview and description of all these settings can be found by importing the animrec class and then calling `print(animrec.Recorder._doc_)`.

When the `Recorder` is run for the first time, it creates a `setup` directory in the user's home directory to store all relevant setup files. Central is the default configuration file *animrec.conf*. *AnimRec* is set up in such a way that it is very easy to set and save custom settings that are then automatically used for future use without further user input. Multiple configuration files can be created and called for specifics recording settings and the configuration file(s) can be easily edited with any text editor as well as updated from the command line with the `set_config()` method. In addition the setup directory will contain a log file *animrec.log* that will store all terminal output when *AnimRec* is used to help keep a history log of your recordings.

### <a name="othmethods"></a>Other methods
In addition to the main recording module, AnimRec contains a number of other modules to facilitate setting-up the Raspberry Pi camera, configuring the camera, scheduling recordings, and converting recorded media:

1. `setgains()`: Method that automatically determines the optimal white balance for the current camera position and lighting conditions. Stores details of the white balance with the configuration so it is loaded automatically.
2. `setroi()`: Method that lets the user draw a rectangular region on a live video stream of the rpi camera and select the region of interest to be used for recording. Again roi settings are automatically stored and called from the configuration file.
3. `schedule()`: Method that enables the future scheduling of automated image and video recording jobs. To read the detailed documentation import the animrec package and call: `print(animrec.schedule.__doc__)`.
4. `Converter()`: Class that enables converting videos to `.mp4` format with the option to resize them as well as print a frame number in the top left corner. Makes use of multiprocessing such that multiple videos can be converted simultaneously.

### Recording modes
AnimRec has three recording modes: `img`, `imgseq`, and `vid`. Files are automatically stored in the configured directory (`recdir`), by default a directory called `recordings` in the home directory, and are automatically named according to the provided `label`, the computer name, the date and time, and the session number or image sequence nr (e.g. "pilot\_180312\_PI13\_101300.jpg", "pilot\_180312\_PI13\_img00231_101300.jpg", and "pilot\_180312\_PI13\_S01\_101300.h264").

1. `img` mode: This mode records a single image with the custom settings and then quits.
2. `imgseq` mode: This mode creates a controlled sequence of images based on either a set duration (setting `imgtime`) or total number of images to be recorded (setting `imgnr`) with a certain delay between images (setting `imgwait`). 
3. `vid` mode: This mode records a loop of standardized videos based on the custom settings. After each recording has finished, the user is asked if a new recording should be started or the recorder should exit. Specific settings that can be set for this mode are `vidfps`, the framerate of the video; `vidduration`, the duration of the video; and `viddelay`, extra recording time in seconds that will be added to vidduration.

**See the [animrec guide](https://github.com/JolleJolles/animrec/tree/master/animrec-guide.md) for a more detailed explanation of all the functionalities of *AnimRec*.**

Development
--------
For an overview of version changes see the [CHANGELOG](https://github.com/JolleJolles/animrec/blob/master/CHANGELOG) and for detailed changes see the [commits page](https://github.com/JolleJolles/animrec/commits/). Please submit bugs or feature requests to the GitHub issue tracker [here](https://github.com/JolleJolles/animrec/issues).

License
--------
Released under a Apache 2.0 License. See [LICENSE](https://github.com/JolleJolles/animrec/blob/master/LICENSE) for details.
