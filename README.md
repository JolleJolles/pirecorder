# AnimRec
A python module for automated image and video recording on the RaspberryPi (rpi).

![logo](https://github.com/jolleslab/AnimRec/blob/master/images/AnimRec-logo.jpg)

<a name="install"></a> Installation
------------
To install, open a terminal window and enter:
```bash
pip install git+https://github.com/jolleslab/animrec.git
```

When AnimRec is already installed, make sure to update to the latest version:
```bash
pip install --update git+https://github.com/jolleslab/animrec.git
```

Dependencies
------------
AnimRec depends on [Python 2.7](http://www.python.org) and the [picamera](http://picamera.readthedocs.io/) package and makes use of various utility functions of the associated [AnimLab](https://github.com/joljols/animlab) package. AnimRec is created specifically for automated recording with the RaspberryPi, but is adaptable to broader possible instances.

Overview
------------
*AnimRec* is a python package designed to help facilitate automated recording using the RPi, specifically with easy, customized, repeated image and video recording for scientists in mind. *AnimRec* is (still) currently a private package on [GitHub](https://github.com/jolleslab/AnimRec) that can be easily installed from github with the right credentials ([see above](#install)).

The main functionality of *AnimRec* is the `Recorder` class in the `animrec` module. This class initiates a Recorder instance that sets up the pi to record either a single image, a sequence of images, or a loop of videos. AnimRec creates a [setup] directory in the users' home directory to store all relevant setup files. In additional AnimRec automatically creates a log file [animrec.log] file that stores all output of the terminal while using the module.

AnimRec has a lot of custom settings to facilitate controlled and automated recording. When AnimRec is initiated for the first time a specific configuration file [animrec.conf] is created and stored in the setup folder. The settings that can be stored are divided into 1) general user recording parameters, 2) camera settings, specific 3) video and 4) image recording settings, and 5) custom settings that are specific to the rpi. For a detailed overview and description of these settings ([see below](#settings)). 

<center>![conf file](https://github.com/jolleslab/AnimRec/blob/master/images/animrec-conffile-screenshot.jpg)

AnimRec is set up in such a way that it is very easy to set and save custom settings: A) the setup/animrec.conf file is directly editable 


<a name="settings"></a>Settings
--------

    Parameters
    ----------
    recdir : str, default = "NAS"
        The directory where media will be stored. Default is "NAS", which is the
        automatically mounted NAS drive. If different, a folder with name
        corresponding to location will be created inside the home directory.
        Providing no name stores in home directory.
    setupdir : str, default = "setup"
        The directory where setup files are stored relative to home directory.
    Label : str, default = "test"
        Label for associating with the recording and stored in the filenames.
    rectype : ["img", "imgseq", "vid"], default = "img"
        Recording type, either a single image, a sequence of images, or a video.

    Config settings
    ---------------
    rotation : [0, 180], default = 0
        Custom rotation specific to the RPi.
    brighttune : [-10,10], default = 0
        Custom brightness tuning specific to the RPi.
    gains : tuple, default = (1.0, 2.5)
        Custom gains specific to the RPi to have a 'normal' colorspace.

    brightness : int, default = 45
        The brightness level of the camera, an integer value between 0 and 100.
    contrast : int, default = 20
        The image contrast, an integer value between 0 and 100.
    saturation : int, default -100
        The color saturation level of the image, an integer value between -100
        and 100.
    iso : int, default = 200
        The camera ISO value, an integer value in sequence [200,400,800,1600].
        Higher values are more light sensitive but have higher gain.
    sharpness : int, default = 50
        The sharpness of the camera, an integer value between -100 and 100.
    compensation : int, default = 0
        Camera lighting compensation. Ranges between 0 and 20. Compensation
        artificially adds extra light to the image.
    shutterspeed : int, detault = 10000
        Shutter speed of the camera in microseconds, i.e. the default of 10000
        is equivalent to 1/100th of a second. A longer shutterspeed will result
        in a brighter image but more motion blur. Important: the framerate of
        the camera will be adjusted based on the shutterspeed. At shutter-
        speeds above ~ 0.2s this results in increasingly longer waiting times
        between images so a standard imgwait time should be chosen that is 6+
        times more than the shutterspeed. For example, for a shutterspeed of
        300000 imgwait should be > 1.8s.
    quality : int, default = 11
        Specifies the quality that the encoder should attempt to maintain. Valid
        values are between 10 and 40, where 10 is extremely high quality, and 40
        is extremely low.
    imgdims : tuple, default = (3280,2464)
        The resolution of the images to be taken in pixels.
    viddims : tuple, default = (1640,1232)
        The resolution of the videos to be taken in pixels.
    imgfps : int, default = 1
        The framerate for recording images. Will be set automatically based on
        the imgwait setting.
    vidfps : int, default = 24
        The framerate for recording video.
    imgwait : float, default = 1.0
        *Image parameter only*. The delay between subsequent images in seconds.
        When a delay is provided that is less than ~0.5s (shutterspeed +
        processingtime) it will be automatically set to 0 and images thus taken
        immideately one after the other.
    imgnr : int, default = 60
        *Image parameter only*. The number of images that should be taken. When
        this number is reached, the script will automatically terminate.
    imgtime : integer, default = 60
        *Image parameter only*. The time in seconds during which images should
        be taken. The minimum of a) imgnr and b) nr of images based on imgwait
        and imgtime will be selected.
    vidduration : int, default = 10
        Duration of video recording in seconds.
    viddelay : int, default = 0
        Extra recording time in seconds that will be added to vidduration. Its
        use is for filming acclimatisation time that can then easily be cropped
        for tracking.

    Output
    -------
    Either one or multiple .h264 or .jpg files depending on the filetype and
    single input. All files are automatically named according to the label,
    the host name, date, time and potentially session number or count nr, e.g.
    - single image: 'pilot_180312_PI13_101300.jpg
    - multiple images: 'pilot_180312_PI13_img00231_101300.jpg
    - video: 'pilot_180312_PI13_S01_101300.h264

    Returns
    -------
    self : class
        Recorder class instance        

Using AnimRec
--------
To use utility functions, e.g.:
```python
from animlab.utils import listfiles
from animlab.imutils import crop
from animlab.mathutils import points_to_angle
```
