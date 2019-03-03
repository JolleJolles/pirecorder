# General setting-up guide

This guide provides a general guide for setting-up your rpi and installing *AnimRec*. It is mainly intended to provide an overview of the installation steps and the workflow for using animrec, with the former especially written with people with limited knowledge of Raspberry Pi (rpi) and/or Python in mind. It presumes you have a rpi that is powered on, connected to the internet, and that you have terminal access (future guides will help go through these steps as well).

A Jupyter notebook with all the commands that are used in the starting, configuring, and running animrec sections below can be found [here](https://github.com/JolleJolles/animrec/tree/master/notebooks/run-animrec.ipynb). To install Jupyter enter `python -m pip install jupyter`, and then simply type `jupyter notebook` in Terminal to start an instance of jupyter.

Setting up the rpi
--------
1. Let's first make sure that your rpi is fully up to date. Open a terminal window and enter:

    `sudo apt-get update && sudo apt-get upgrade`.

2. If you haven't set up your rpi camera yet, connect it to your rpi and position it in the right direction. Now open a video stream to further improve its positioning by entering `raspistill -t 0 -k` in a terminal window and when you are happy press `ctrl+c`. For this step you need to have video access to the pi, which is possible either via hdmi connection or with VNC viewer connection.

3. *AnimRec* is build in Python. Luckily rpi generally comes with python pre-installed. To check this simply enter in terminal: `python --version`. This command will show the python version. There are two major versions of python: 2.7 and 3.x. If you are new to Python it is easiest to just stick to the native Python on your rpi. However, we do need to update some python development tools. To do this simply open a terminal window and enter:

    `sudo apt-get install python-setuptools python-dev build-essential libpq-dev`

4. When you start working with Python, it is great practice to create isolated Python environments to work on your specific projects. The standard python environment is used by a large number of system scripts and therefore best to leave alone. I therefore strongly suggest to create a so-called virtual python environment. Follow my specific guide [here](https://github.com/JolleJolles/animlab/tree/master/docs/install-virtual-python-environments.md).


Installing AnimRec
--------
1. *AnimRec* makes use of the [Pandas](http://pandas.pydata.org) data analysis library. Although it would be automatically installed when you are installing *AnimRec*, it is best to install it manually with apt-get, replacing 'python-pandas' by 'python3-pandas' when using Python3:

    `sudo apt-get install python-pandas`

2. For some of its functionality, *AnimRec* makes use of the *OpenCV* image processing library. To install this dependency follow my simple guide [here](https://github.com/JolleJolles/animlab/tree/master/docs/install-opencv.md).

3. If you plan on wanting to convert the recorded videos (which are in .h264 format) to .mp4 format, *ffmpeg* with h264 support is required. Follow my guide for installing ffmpeg [here](https://github.com/JolleJolles/animlab/tree/master/docs/install-ffmpeg-with-h264.md) or if not required skip this step.

4. *AnimRec* makes use of a number of helper functions that are (currently) part of my *AnimLab* package. To install this enter:

    `pip install git+https://github.com/JolleJolles/animlab.git`

5. Now we are ready to install *AnimRec*. To do so simply enter (use pip for python2 and pip3 for python3):

    `pip install git+https://github.com/JolleJolles/animrec.git`

    With this step a number of additional python packages that are required for *AnimRec* to function will be automatically installed.


Starting with AnimRec
--------
1. To load *AnimRec*, simply start your python instance, such as by entering `python` in the terminal, and then within Python enter `import animrec`.

2. It is important to consider that the first time the `animrec.Recorder()` class is run, it will create a setup directory in the users home directory with the default configuration file. To do this, simply enter:

    `AR = animrec.Recorder()`

    Remember that the Recorder functionality is a class instance and therefore needs to be stored as a variable. I chose the variable name `AR` but any variable is possible.

3. All commands and output after creating your Recorder instance will be stored in a log file in the setup directory with a timestamp so it is easy to look back at the recordings you did back in time.

4. Before continuing first carefully read the Recorder documentation to understand the wide range of possible settings:

    `print(animrec.Recorder._doc_)`


Configuring AnimRec
--------
1. To start configuring the recording settings I suggest to first have a look at the defaults. You can do this either by opening the *animrec.conf* in the setup directory or by entering `print(AR.config)` within Python after starting a Recorder instance.

2. To change and store the recording parameters use the `set_config` method with any of the variables you wish to store. For the details of the parameters: `print(animrec.Recorder._doc_)`

3. The first parameter you may want to change is the recording directory. Default this is a folder called `recordings` in the home directory of the rpi. If you want to change this simply change the `recdir` parameter, such as `AR.set_config(recdir = "videos")`. If this directory does not exist yet it will be automatically created. Make sure not to have spaces in the folder name. When `recdir` is left empty recordings will be stored in the home directory.

    It is also possible to store recordings on an external drive or a NAS drive connected to the network of the rpi. To do so simply add the folder where the external drive is mounted to the `recdir` parameter. When this folder is named "NAS", *AnimRec* will automatically check if it is linked to a mounted drive and if not store in the home directory instead. Therefore make sure that your NAS drive has been correctly mounted.

4. The next potential parameters you may wish to change are the label used in the recording filenames (`label`) and the type of recording, i.e. a single image, a sequence of images, or a video (`rectype`). To for example change the label to "test, and the recording type to "video" we can simply run the command: `AR.set_config(label = "test", rectype = "vid")`.

5. One can change a wide variety of image and video parameters in a similar way using the `set_config` function, such as the `brightness`, `saturation`, `sharpness`, `dimensions`, `vidduration`, and `viddims` among many others. For an overview of the parameters that can be set, what they do, and how to set them see the Recorder documentation `print(animrec.Recorder._doc_)`.

4. Let's continue configuring your recordings by taking a single image to get the right light levels, color and file size for future recordings. We'll use the defaults but want to use "img" as the rectype and "testimg" for the label:

    `AR.set_config(label = "testimg", rectype = "img")`

    Camera light levels depend on the following parameters: `brightness`,`iso`,`contrast`, and `compensation`. So play with these until the image has the right light level.

    To set the saturation use the `saturation` parameter and enter a value between -100 and 100.

    You can also see if the size of the image is too small or large and further tweak this by playing with the `imgdims` and `imgquality` settings.

    If your recording is upside down simple change the `rotation` parameter from `0` to `180`.

    When you are happy with your chosen settings and have stored these with the `set_config` command, these settings will be used for any future recordings.

5. In many cases you may wish to record in color. To automatically set the white balance of the camera and store those parameters we can use the `set_gains` method. This function will open the camera for 10 seconds and automatically determine the optimal parameters to get a perfect color recording. To run this function simply enter:

    `AR.set_gains()`

    This is an optional setting and defaults will otherwise be used that should be okay in most cases or not used at all in the case of recording in black and white.

6. Next we can also optionally set the right region of interest of the camera that should be used for recording, such as when only wanting to film part of the field of view of the camera to save storage space. To do so simply run:

    `AR.set_roi()`

    This will open a video stream of the rpi camera linked to the resolution set with the Recorder class. Now drag a rectangular area around your region of interest and press `s` when happy to store these coordinates. If you made a mistake simply press `e` or to exit this function press `esc`.

7. When wanting to change the dimensions of the recording, i.e. by using `imgdims` or `viddims`, keep in mind the maximum resolutions capable of your rpi camera otherwise an error message will be shown.

8. When recording video (`rectype = "vid"`) make sure that the `vidduration` parameter is additionally set correctly (in seconds).

9. When recording an image sequence (`rectype = "imgseq"`) make sure that you set the time delay between subsequent images (`imgwait`, minimally 0.5s) and either the number of images that you wish to take (`imgnr`) or the total time duration over which you want to take images (`imgtime`).

    The minimum of imgnr and the calculated number of images based on `imgwait` and `imgtime` will be selected. For example, if one wishes to specifically record 100 images 10.0s after one another, one would use the settings:`imgwait=10` `imgnr=100` and `imgtime=9999`, or if one wishes to record images every 0.5s for 10 hours irrespective of their total number one would use: `imgwait=0.5` `imgnr=999999` `imgtime=36000`.

10. To record in low light conditions, the `shutterspeed` parameter should be set (in microseconds). When recording something that moves at a considerable speed, motion blur becomes clearly visible in the case a shutter speed of 50000+ is used. Tracking might still be possible in some cases, such as using blob detection. However, tracking barcodes or other methods that use details of the object, motion blur will likely result in failure.

    It is important to note that the frames recorded each second (FPS) will be automatically adapted to accomodate the shutter speed. For example, a shutter speed of 200000 is equivalent to 1/5th of a second and so a maximum fps of 5 would be possible and will therefore be set automatically.


Running AnimRec
--------
1. Now you are ready to run recordings with the `Record` method. This is as simple as running:

    `AR.record()`

    When recording video, after each video recording has ended the user is automatically asked to record another video and a sequence number is added to the video. This makes it very easy to run multiple video recordings after another, such as when filming trials of a behavioural experiment. To just run a single video recording enter instead:

    `AR.record(singlevid = True)`

2. You can run your animrec recordings in a number of different ways. Following from the steps above, the easiest is simply interactively with python running in the terminal. Thus, open an instance of python:

    `python`

    Import animrec and set-up the Recorder instance:

    `import animrec`
    `AR = animrec.Recorder()`

    And run record:

    `AR.record()`.

    You could even run the code directly from the terminal:

    `python -c import animrec; AR=animrec.Recorder(); AR.record()`

3. The second way is to create a simple python file with the code to run a recording. For example, you could create the file `recim.py` with the following code:

    ```
    # Import the package
    import animrec

    # Initiate the recorder instance
    AR = animrec.Recorder()

    # Update the configuration
    AR.set_config(label="test", rectype="img", iso=200, contrast=20)
    AR.record()
    ```

    and run that from the terminal:

    `python recim.py`

    To make running this even easier, we can create an alias for our recording script with a custom command. For this we need to open the `.bashrc` file in our root directory:

    `sudo nano ~/.bashrc`

    and add the following to the bottom of the file:

    `alias rec='sudo python recim.py'`

    Now all you need to enter in terminal to start your recordings is `rec`, and AnimRec automatically starts with the right custom settings.

    Note: Do not call your file like the package, i.e. `animrec.py`, as then the code will not be run properly.


3. A third way is to store your code in a jupyter file, like the tutorial file [here](https://github.com/JolleJolles/animlab/tree/master/docs/install-virtual-python-environments.md), with the option to have many different cells with different parameters or calls and only run those cells that you want.

Scheduling recordings
--------
1. Besides starting recordings directly, it is also possible to schedule recordings for the future. This is done with the `schedule` method for which timeplans can be set with different jobnames. Read the full documentation by entering `print(AR.schedule.__doc__)`.

2. The timeplan consists of a code string that is build on CRON and should consists of the following parts:

    ```
     * * * * *
	 - - - - -
	 | | | | |
	 | | | | +----- day of week (0 - 7) (sunday = 0 or 7)
	 | | | +---------- month (1 - 12)
	 | | +--------------- day of month (1 - 31)
	 | +-------------------- hour (0 - 23)
	 +------------------------- min (0 - 59)
	```

	Each of these parts supports wildcards (*), ranges (2-5), and lists
	(2,5,6,11).

	For example, if you want to schedule a recording at
	22:00, every workday of the week, enter the code '0 22 * * 1-5'

	Note that the minimum time between subsequent scheduled recordings is 1 minute. Smaller intervals between recordings is ofcourse possible for images with the imgseq command with the `Record` method.

2. It is important to make sure that Recorder configuration timing settings are within the timespan between subsequent scheduled recordings based on the provided timeplan. For example, a vid duration of 20 min and a scheduled recording every 15 min between 13:00-16:00 (`*/15 13-16 * * *`) will fail.

   To test your timeplan, simple add `test = True`. If you need further help, [crontab.guru](http://crontab.guru) is a great website for checking your timeplan.

3. To disable a specific job that you previously created and set enter:

    `AR.schedule(jobname = "rec1", enable = False)`

    Or to clear the job completely:

    `AR.schedule(jobname = "rec1", clear = "job")`


Converting video recordings
--------
1. It is very tricky to record to compressed formats like `.mp4` directly with the rpi and therefore *AnimRec* stores, like *picamera* and other packages, videos in the `.h264` format. These videos are very hard to open (I only know of VLC player to make it work partly) but luckily we can easily convert them with the `Converter` class of the package.

2. To import the Convert class enter:

   `from animrec import Converter`

   and to read the documentation enter:

   `print(Converter.__doc__)`

3. To start recording you can set the `dir_in` parameter to the directory of videos you would like to convert. If nothing is provided it will attempt to convert videos from the  location at which you initiated python.

4. The `Converter` class makes it possible to simply convert a folder of videos directly  or to also add a running framenumber in the top left corner, such as to facilitate the behavioural observations of video recordings. While the former uses `ffmpeg` and is considerably faster, the latter uses `opencv`, with both making use of multiprocessing such that multiple videos can be converted simultaneously. Converting without frame is default (`conv_type = "standard"`). To convert videos with the frame number displayed enter:

   `Converter(conv_type = "withframe")`

5. It is also possible to resize videos. Simply ad the resize value to `resizeval` with which the video should be resized. For example, to make the video half the dimensions of what it was enter:

   `Converter(resizeval = 0.5)`
