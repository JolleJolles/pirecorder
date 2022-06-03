---
layout: page
title: 2 Installing pirecorder
nav_order: 4
---

# Installing pirecorder
{: .no_toc }

Okay, so you got your raspberry pi up and running and fully set up. Now it is time to install the pirecorder package.
{: .fs-6 .fw-300 }

The short explanation is very simple: just open a terminal window and enter `pip install pirecorder`. The more detailed explanation can be found below. Note also that pirecorder can be installed on non-raspberry pi systems, such as to use the `stream` and `convert` modules.

## Table of contents
{: .no_toc .text-delta .fs-4 .fw-300 }

1. TOC
{:toc}
---

## Creating a virtual environment

When you start working with Python, it is great practice to create isolated Python environments to work on your specific projects. The standard python environment is used by a large number of system scripts and therefore best to leave alone. I therefore strongly suggest to start by creating a virtual Python environment and install pirecorder there.  

To create virtual Python environments on your raspberry pi, first we need to install the virtual environment modules. I recommend to use `virtualenv`. To install this module and the helpful wrapper module type in:

```
sudo pip3 install virtualenv virtualenvwrapper
```

To get it to work easily on the command line, edit the file .bashrc (`nano ~/.bashrc`) and append the following lines to the bottom of the file:

```
#Virtualenvwrapper settings:
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
export WORKON_HOME=$HOME/.virtualenvs
export VIRTUALENVWRAPPER_VIRTUALENV=/usr/local/bin/virtualenv
source /usr/local/bin/virtualenvwrapper.sh
export VIRTUALENVWRAPPER_ENV_BIN_DIR=bin
```

Exit the file (`ctrl+x`, then `y`, and `Enter`). Now reload the file to make the changes come into effect:

```
source ~/.bashrc
```

Now we can simply create a new virtual environment with the command:

```
mkvirtualenv NAME
```

where NAME is the name you want to give to your virtual environment. Each virtual environment will have their own installed python packages, which can be checked with the command `pip freeze`.

## Installing pirecorder and dependencies

It is very easy to install pirecorder with pip. First make sure you are in the desired virtual environment if you have one (e.g. `workon MYENV`) and simply enter:

```
pip install pirecorder
```

This command will also install the majority of dependencies, which include `numpy` and my `pythutils` package [link](https://github.com/jollejolles/pythutils). One of the main dependencies, `picamera` should already be installed by default. If it is not, I recommend to install it with pip:

```sudo pip install "pirecorder[array]"

`OpenCV` is a dependency that needs to be manually installed. Follow my 5min guide on my raspberrypi-guide.github website [here](https://raspberrypi-guide.github.io/programming/install-opencv). And if you plan on using the converter functionality then you will additionally need to install `FFmpeg`. Click [here](other/install-ffmpeg-raspberry-pi.md) for my guide to install it on raspberry pi and [here](other/install-ffmpeg-osx.md) for my guide to install it on OS X.

You should now be fully set up and have pirecorder working. To test it, open a terminal window and type in `python3` to enter python, and then import the pirecorder module:

```
import pirecorder
```

If you don't get any message, pirecorder is installed succesfully!

## Running the PiRecorder module for the first time

The main functionality of the pirecorder package is the `PiRecorder` module. To use it, simply create a recorder instance:

```
rec = pirecorder.PiRecorder()
```

As the PiRecorder functionality is a class instance it needs to be stored as a variable. Above we used the variable name `Rec`, but any variable is fine as long as you are consistent in using it.

The first time the PiRecorder instance is run, automatically a `pirecorder` directory will be created in the user's home directory with a default configuration file (`pirecorder.conf`) that will be used as the basis for future recordings. To also make it is easy to see what recordings you did back in time, all commands and output created with the PiRecorder instance will be stored in a log file in the setup directory with a date and time stamp.

## Testing
It is  possible to test all the functionalities of the pirecorder package. Simply run the `tests/test.py` file ([here](https://github.com/JolleJolles/pirecorder/tree/master/tests/test.py)), or alternatively run the main functionalities manually using the documented jupyter notebook files [here](https://github.com/JolleJolles/pirecorder/tree/master/notebooks). Note that running the tests will require user input as some of the functionalities are interactive.

---
PiRecorder module documentation
{: .text-delta .fs-5}

```
Sets up the rpi with a pirecorder folder with configuration and log files
and initiates a recorder instance for controlled image and video recording

Parameters
----------
configfile : str, default = "pirecorder.conf"
    The name of the configuration file to be used for recordings. If the
    file does not exist yet, automatically a new file with default
    configuration values will be created.

Returns
-------
self : class
    PiRecorder class instance that can be used to set the configuration,
    start a video stream to calibrate and configure the camera, to set the
    shutterspeed and white balance automatically, to start recordings, and
    to schedule future recordings.
```
