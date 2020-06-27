---
layout: page
title: Install opencv
parent: Other guides
nav_order: 10
---

# Installing opencv on raspberry pi, ubuntu, and Mac OS X
{: .no_toc }

Installing [OpenCV](https://opencv.org) has never been very simple, especially when it could only be build from source. This was especially painful when wanting to run it on a Raspberry Pi as building and installing OpenCV took such a lot of time, especially on the older models. Luckily as of last year it is possible to [install OpenCV with pip](https://pypi.org/project/opencv-python)!

Below I guide you through the basic steps necessary to get OpenCV to wor on Mac, Ubuntu and Raspberry Pi. If you want more background information, see the excellent article [here](https://www.pyimagesearch.com/2018/09/19/pip-install-opencv/) by Adrian Rosebrock from [pyimagesearch.com](http://PyImageSearch.com).

## Table of contents
{: .no_toc .text-delta .fs-4 .fw-300 }

1. TOC
{:toc}
---

## Install pip
Pip is the main package manager for python that we will also use to install OpenCV. Pip should already be installed on your system (see [here](https://pip.pypa.io/en/stable/installing/)), but if it's not, we can install it with wget. Open a Terminal window and enter:

```
wget https://bootstrap.pypa.io/get-pip.py
```

Now to install pip for Python 3 enter:

```
sudo python3 get-pip.py
```

## Install prerequisites
Next, for some versions of Raspbian we may need to install some additional packages. First make sure `apt-get` is fully up-to-date by entering the following in Terminal:

```
sudo apt-get update
```

Now install the prerequisites:

```
sudo apt-get install libhdf5-dev libhdf5-serial-dev -y
sudo apt-get install libqtwebkit4 libqt4-test -y
sudo apt-get install libatlas-base-dev libatlas3-base libjasper-dev libqtgui4 python3-pyqt5 -y
```

## Install OpenCV with pip
Finally, we can enter install OpenCV very simply with the command:

```
pip install opencv-contrib-python
```

However, before running above command, it is important to note that the latest version of opencv may not always be fully functional on the Raspberry Pi. Therefore I recommend to run the below command that installs the latest known working version:

```
pip install opencv-contrib-python==4.1.0.25
```

If you still get an error message such as <em>Could not find a version that satisfies the requirement opencv-contrib-python (from versions: ) No matching distribution found for opencv-contrib-python</em>, try the alternative to use apt-get instead of pip:

```
sudo apt-get install python-opencv
```

## Testing
Now let's just make sure that OpenCV is working. Open a terminal window and enter `python3` to start Python. Now to make sure you have installed OpenCV correctly enter:

```
import cv2
cv2.__version__
```

Your terminal window should look like:

```
$ python3
Python 3.7.3 (default, Dec 20 2019, 18:57:59)
[GCC 8.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import cv2
>>> cv2.__version__
'4.1.0'
```

You are done!

Note: an alternative to getting to run the latest version of opencv on Raspberry Pi is to run the following command rather than `python3`: `LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1 python3`.
