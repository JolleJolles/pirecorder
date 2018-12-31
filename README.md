# AnimRec
**A python module for controlled image and video recording for the Rasperry Pi**

![logo](https://github.com/JolleJolles/animrec/blob/master/animrec-logo.jpg)

*AnimRec* is a python package build to help facilitate automated recording using the RPi, with easy, customized, repeated image and video recording. It is specifically designed with the Behavioural Scientist in mind and easily installed and usable for people with limited knowledge of coding. 

*AnimRec* consists of a main recorder module and a number of [helper methods](#othmethods) that facilitate setting-up the Raspberry Pi camera, configuring the camera, scheduling recordings, and converting recorded media.

Citing
------------
This software is created with the Behavioural Scientist in mind but should be of interested to the broader academic community and the general code-minded public. 

If you use AnimRec, please let me know. I would love to hear how you like and it. Also please cite AnimRec using the following DOI:

*Jolles, J. W. (2018) AnimRec: A python module for controlled image and video recording for the Rasperry Pi v1.0.0. Zenodo. https://doi.org/10.5281/zenodo.2529516*

[![DOI](https://zenodo.org/badge/163422997.svg)](https://zenodo.org/badge/latestdoi/163422997)



<a name="install"></a> Quick install
------------
To install AnimRec, open a terminal window and enter:
```bash
pip install git+https://github.com/JolleJolles/animrec.git
```

Dependencies
------------

- [Python 2.7 or 3.x](http://www.python.org)

- [AnimLab](https://github.com/JolleJolles/animlab)

- [picamera](http://picamera.readthedocs.io/)

- [numpy](http://www.numpy.org/)

- [pyyaml](https://pyyaml.org)

- [python-crontab](https://pypi.org/project/python-crontab/)

- [ffmpeg](https://www.ffmpeg.org)

- [OpenCV](http://opencv.org/)

*AnimRec* is written in [Python](http://www.python.org). It builds strongly on the [picamera](http://picamera.readthedocs.io/) package and makes use of various utility functions of the associated [AnimLab](https://github.com/joljols/animlab) package. Scheduling makes use of CronTab and the associated [python-crontab](https://pypi.org/project/python-crontab/) package. Converting requires [ffmpeg](https://www.ffmpeg.org) and [OpenCV](http://opencv.org/). AnimRec is created specifically for automated recording with the Raspberry Pi, but its functionality is easily adaptable to a broader range of possible instances.

For installing python with OpenCV on Mac/Ubunto/Raspberry Pi follow the tutorial in the documentation of the linked [AnimLab](https://github.com/JolleJolles/animlab) package [here](https://github.com/JolleJolles/animlab/tree/master/docs/install-opencv.md).

For installing ffmpeg with h264 support on Raspberry Pi, follow the tutorial [here](https://github.com/JolleJolles/animlab/tree/master/docs/install-ffmpeg-with-h264.md).


Overview
------------

### Recorder class
The main functionality of *AnimRec* is the `Recorder` class. This class initiates a Recorder instance that sets up the Raspberry Pi to record either a single image, a sequence of images, or a loop of videos. There are many custom configurations that can be set with the animrec.Recorder class, which are divided into 1) general user recording parameters, 2) camera settings, 3) specific video and 4) specific image recording settings, and 5) custom settings linked to the specific rpi being used. For a detailed overview and description of these settings, read the documentation: `print(animrec.__doc__)`.

When the `Recorder` is run for the first time, it creates a `setup` directory in the user's home directory to store all relevant setup files. This directory also contains a log file *animrec.log* that will store all terminal output from when the *AnimRec* package is used to keep track of your recording history. 

In addition, a default configuration file *animrec.conf* is created. *AnimRec* is set up in such a way that it is very easy to set and save custom settings that are then automatically used without further user imput. The configuration file can be updated from the command line with the `set_config()` method but also edited with any text editor.

### <a name="othmethods"></a>Other methods
In addition to the main recording module, AnimRec contains a number of other modules to facilitate setting-up the Raspberry Pi camera, configuring the camera, scheduling recordings, and converting recorded media:

1. `setgains()`: Method that automatically determines the optimal white balance for the current camera position and lighting conditions.
2. `setroi()`: Method that lets the user draw a rectangle on a live stream of the rpi camera to create the region of interest to be used for recording.
3. `schedule()`: Method that enables the scheduling of automated image and video recording jobs. Please see the specific documentation: `print(animrec.schedule.__doc__)`.
4. `Converter()`: Class that enables converting videos to `.mp4` format with the option to resize them and print a frame number in the top left corner. Uses multiprocessing so multiple videos can be converted simultaneously.

### Recording modes
AnimRec has three recording modes: `img`, `imgseq`, and `vid`. Files are automatically stored in the configured directory (`recdir`), by default a directory called `recordings`, and are automatically named according to the provided `label`, the computer name, the date and time, and the session number or image sequence nr (see examples below).

1. `img` mode: This mode records a single image with the custom settings and then quits. Example of filename: "pilot\_180312\_PI13\_101300.jpg".
2. `imgseq` mode: This mode creates a controlled sequence of images based on either a set duration (setting `imgtime`) or total number of images to be recorded (setting `imgnr`) with a certain delay between images (setting `imgwait`). The minimum of imgnr and the calculated number of images based on `imgwait` and `imgtime` will be selected. For example, if one wishes to specifically record 100 images 10.0s after one another, one would use the settings:`imgwait=10` `imgnr=100` and `imgtime=9999`, or if one wishes to record images every 0.5s for 10 hours irrespective of their total number one would use: `imgwait=0.5` `imgnr=999999` `imgtime=36000`. Example of filename: "pilot\_180312\_PI13\_img00231_101300.jpg".
3. `vid` mode: This mode records a loop of standardized videos based on the custom settings. After each reording has finished, the user is asked if a new recording should be started or the recorder should exit. Specific settings that can be set for this mode are `vidfps`, the framerate of the video; `vidduration`, the duration of the video; and `viddelay`, extra recording time in seconds that will be added to vidduration, for example to film acclimatisation time for observations but that will be automatically ignored in later tracking of the video. Example of filename: "pilot\_180312\_PI13\_S01\_101300.h264".


### Record in low light

To record in low light conditions, the `shutterspeed` parameter should be set (in microseconds). When recording something that moves at a considerable speed, motion blur becomes clearly visible when a shutter speed is used of above 50000. Tracking might still be possible in some cases, such as when blob detection is used. However, tracking barcodes or other methods that use details of the object, motion blur will likely result in failure. 

It is important to note that the frames recorded each second (FPS) will be automatically adapted to accomodate the shutter speed. For example, a shutter speed of 200000 is equivalent to 1/5th of a second and so a maximum fps of 5 would be possible and will therefore be set automatically.

### Storage location
It is default that images and videos are stored in a folder `recordings` in the home directory of the RPi. If you want to store in a different folder instead just add the foldername for the parameter `recdir`. If the folder does not exist yet it will automatically create one (make sure not to have spaces in the foldername). If `recdir` is left empty it will store videos in the home directory. 

It is also possible to store recordings on a NAS drive connected to the network. Simply add "NAS" to the `recdir` parameter. *AnimRec* will automatically check if the folder is linked to a mounted drive and if not store in the home directory. Make sure that the NAS drive has been correctly mounted.


Workflow
--------
1. Install the latest version of [Raspbian](https://www.raspberrypi.org/downloads/raspbian/) and make sure it is fully up to date and has python installed: `sudo apt-get update && sudo apt-get upgrade`.
2. Set up the Raspberry Pi with an (IR) camera and position it in such a way that it records the zone of interest (using the `raspistill -t 0 -k` command).
3. Install *AnimRec* by following the steps [above](#install) and make sure all dependencies are also installed.
4. Carefully read the animrec documentation to understsand the large range of possible settings (`print(animrec.__doc__)`.
5. Run the `animrec.Recorder()` class for the first time to create the default setup directory and configuration settings.
6. Create the ideal light settings for the camera. This is easiest done by creating a single test image and changing the settings until satisfied with the light levels. Camera light levels depend on the following parameters: `brightness`,`iso`,`contrast`, and `compensation`. See the code below for an example how to set the light levels.
7. Now set the other configuration settings for the recording, such as the `resolution`, `duration`, `saturation` etc. To see all potential parameters enter: `print(animrec.__doc__)`.
8. When wanting to record coloured images or video, make sure you set the right white balance. The best fitting white balance can automatically determined with the `set_gains()` method. Make sure that a white background is provided in the Camera when running this method.
9. Now optionally run the `set_roi()` method to get the right region of interest to be used for recording, linked to the resolution set with the Recorder class. If not used the full camera screen will be used.
10. Now you are ready to run recordings with the `Record()` method. It is also possible to schedule recordings in the future! To so so use the `schedule()` method after reading its documentation: `print(schedule.__doc__)`.
11. After finishing your recordings you can now potentially convert your media, either folders of images or .h264 files, to .mp4 files with the `convert()` method.

For examples, please see the code below, use one of the [sample scripts](https://github.com/jolleslab/AnimRec/tree/master/scripts), or work with the tutorial jupyter notebooks provided [here](https://github.com/jolleslab/AnimRec/tree/master/notebooks).


<a name="examples"></a>Running AnimRec
--------
To run AnimRec recordings from a script it is important that AnimRec is initiated at least once and has the right configuration settings. To do so, the simplest way is to open an instance of Python and run the following commands:

```python
# Import the package
import animrec

# Initiate the recorder instance
AR = animrec.Recorder()

# Create 3 test images for getting the right light levels
AR.set_config(label="test", rectype="img", iso=200, compensation=0, contrast=20)
AR.set_config(brightness=45)
AR.record()
AR.set_config(brightness=50)
AR.record()
AR.set_config(brightness=55)
AR.record()

# Config for videos
AR.set_config(viddims = (1640, 1232), vidfps = 24, vidduration = 5, viddelay = 2)

# Dynamically set the Gains
AR.set_gains()

# Draw the region of interest
AR.set_roi()
```

Now the required AnimRec setup files are created and the configuation is as required, we can simply run the Record function to start recording. One way to do this is to create a very simple script like `rec.py`:

```python
import animrec
AR = animrec.Recorder()
AR.record()
```

and run that from the terminal:

```python rec.py```

You could also immideately run the code in terminal:

```python -c import animrec; AR=animrec.Recorder(); AR.record()```


### Alias
To make running *AnimRec* even easier, we can create an alias for our recording script with a custom command. For this we need to open the `.bashrc` file in our root directory:

`sudo nano ~/.bashrc`

and add the following to the bottom of the file:

`alias rec='sudo rpirec.py'`

Now all you need to enter in terminal to start Animrec is ```rec```, and AnimRec automatically starts with your custom settings.

### Jupyter
A nice alternative is to make use of [Jupyter](http://jupyter.org/install.html). This is an open-source web application that allows you to create python scripts (among many other coding languages) that contain live code, equations, and visualizations that can be executed on a cell-by-cell basis. Jupyter is a great way to sequentually run parts of your code and problem solve it.

To install Jupyter type in:

`python -m pip install jupyter`

Then to simply start jupyter type `jupyter notebook` in Terminal. An alternative way is to use nteract, a free software package for Mac. You can find it [here](nteract.io). 

Tutorial notebooks for working with AnimRec are provided in the [notebooks](https://github.com/jolleslab/AnimRec/tree/master/notebooks) folder of the package.


Development
--------
For an overview of version changes see the [CHANGELOG](https://github.com/JolleJolles/animrec/blob/master/CHANGELOG) and for detailed changes see the [commits page](https://github.com/JolleJolles/animrec/commits/). Please submit bugs or feature requests to the GitHub issue tracker [here](https://github.com/JolleJolles/animrec/issues).

License
--------
Released under a Apache 2.0 License. See [LICENSE](https://github.com/JolleJolles/animrec/blob/master/LICENSE) for details.