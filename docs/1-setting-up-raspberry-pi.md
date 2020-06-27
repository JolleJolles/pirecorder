---
layout: page
title: 1 Setting up your RPi
nav_order: 3
---

# Setting up your raspberry pi
{: .no_toc }

The below steps will guide you through some basic settings to get your raspberry pi set up for working with *pirecorder*. Most users may not need to follow these steps, but they are shown for completeness.
{: .fs-6 .fw-300 }

## Table of contents
{: .no_toc .text-delta .fs-4 .fw-300 }

1. TOC
{:toc}
---

## Start up your raspberry pi
This guide presumes you have a raspberry pi with working version of Raspbian that is powered on with direct access (screen+keyboard+mouse) or VNC. SSH is also an option but then no direct view of the camera is possible and so is only recommended after initial setting up and calibration of the camera.

## Update your raspberry pi

Make sure that your raspberry pi is fully up to date. Open a terminal window and enter:

```
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get autoremove -y
```

## Enable and test the camera

To be able to use the camera we need to enable it in the configuration menu. Enter:

```
sudo raspi-config
```

go to `5 Interfacing options`, then `P1 Camera`, and click `yes`. Alternatively you can go to the main menu and use the Raspberry Pi Configuration tool there. Now reboot your pi if you have already set up your raspberry pi camera. If not, turn of your raspberry pi and now connect one part of the ribbon cable to the camera and the other end to the raspberry pi by pulling up the edges of the plastic clip of the camera module port and sliding in the ribbon cable, making sure the cable is the right way around.

You can test the camera quickly by entering the command `raspistill -t 0 -k` in a terminal window. To exit again, press `ctrl+c`. If you get an error message, then double check the cable is properly connected to the raspberry pi and the camera and try restarting.

## Setup python for working with the camera

*pirecorder* uses Python, which comes pre-installed with Raspbian on any raspberry pi. However, we need to update some python development tools for the raspberry pi camera to work properly. To do this simply open a terminal window and enter:

```
sudo apt-get install python-setuptools python-dev build-essential libpq-dev
```

## Optional: Enable filesharing
For easy transfering of files with your raspberry pi it may be good to enable filesharing. There are various ways to share files, depending on your system. I recommend to use netatalk:

```
sudo apt-get install netatalk -y
```

Add the home directory to be shared:
```
sudo nano /etc/netatalk/afp.conf
```
And add the following text to the bottom of the file

```
[Homes]
  basedir regex = /home
```

Now restart the service:

```
sudo systemctl restart netatalk
```
