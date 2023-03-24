[![Downloads](https://pepy.tech/badge/pirecorder)](https://pepy.tech/project/pirecorder)

# pirecorder
**A Python package for controlled and automated image and video recording with the raspberry pi**

*pirecorder* is a Python package, built on the [picamera](http://picamera.readthedocs.io/) and [OpenCV](https://opencv.org/) libraries, that provides a flexible solution for the collection of consistent image and video data with the raspberry pi. It was developed to overcome the need for a complete solution to help researchers, especially those with limited coding skills, to easily set up and configure their raspberry pi to run large numbers of controlled and automated image and video recordings using optimal settings.

A paper accompanying this package is published in the Journal of Open Source Software:

*Jolles, J.W. (2020). pirecorder: controlled and automated image and video recording with the raspberry pi. J. Open Source Softw. 5, 2584. doi: [10.21105/joss.02584](http://doi.org/10.21105/joss.02584).*

<p align="center"><img src="https://github.com/jollejolles/pirecorder/blob/master/images/pirecorder-logo-large.jpg"></p>

## Key Features
* **Controlled recording using custom, easy-to-edit configuration files**
* **Record single images and videos, timelapses, and sequences of videos**
* **Configure camera settings interactively via a live camera stream**
* **Dynamically draw the region of interest for your recordings**
* **Automatic naming of files and folders with relevant and custom labels**
* **Easy scheduling and automating recordings in the future**
* **Direct control of all modules via simple terminal commands**
* **Convert (folders of) images and videos with resize, monitor, and label options**
* **Dedicated documentation website with detailed guides and tutorials**
* **Jupyter notebook tutorial files**

## An overview
<p align="center"><a href="https://www.youtube.com/watch?v=pcVHpijd6wc" title="A quick overview of the pirecorder package" target="_blank"><img src="https://github.com/jollejolles/pirecorder/blob/master/images/pirecorder-video.jpg" width="400" height="298"></a></p>

## Modules
*pirecorder* consists of a main `PiRecorder` module to run image and video recordings, `stream` and `camconfig` modules with interactive user interfaces for help setting up, calibrating, and configuring the camera, a `schedule` module for scheduling future recordings, and a `convert` module for the easy converting of (folders of) recorded images and videos.

## Install
**Note:** ! pirecorder relies on picamera, which is not properly integrated in the latest Raspberry Pi OS (Bullseye). Therefore it is highly recommended to use the previous OS Buster to use pirecorder and picamera. It still works but there may be issues with dependencies. You can download Buster OS [here](https://downloads.raspberrypi.org/raspios_armhf/images/raspios_armhf-2021-05-28/) and find more information from the Raspberry Pi foundation about the issue [here](https://www.raspberrypi.com/news/bullseye-camera-system/). I hope to be able to update pirecorder later this year to work easier with bullseye.

To install the latest release of pirecorder, simply open a terminal window and enter:

```
pip install pirecorder
```

To install the latest development version, enter:

```
pip install git+https://github.com/jollejolles/pirecorder.git --upgrade
```

## Dependencies
*pirecorder* builds strongly on the [picamera](http://picamera.readthedocs.io/) package. As some users want to use pirecorder on computers other than a raspberry pi, the picamera package is not set as a dependency. Therefore when using pirecorder for any other functionality it needs to be installed: `pip install "picamera[array]"`.
*pirecorder* also uses [numpy](http://www.numpy.org/) and [pyyaml](https://pyyaml.org), and relies on various utility functions of the accompanying [pythutils](https://github.com/jolle/pythutils) package. Scheduling functionality is based on *CronTab* and the associated [python-crontab](https://pypi.org/project/python-crontab/) package. All these ependencies are automatically installed with *pirecorder*.
* *OpenCV*: has to be manually installed due to its various dependencies on raspberry pi. Click [here](https://raspberrypi-guide.github.io/programming/install-opencv) for my quick install guide.
* *FFmpeg*: is only needed for the convert functionality of *pirecorder*. Click [here](https://raspberrypi-guide.github.io/other/convert-h264-ffmpegs) and [here](https://github.com/JolleJolles/pirecorder/tree/master/docs/other/install-ffmpeg-osx.md) for guides to install on raspberry pi and OS X respectively.

## Documentation
For detailed documentation and tutorials about *pirecorder* and all its functionalities, see the dedicated website [jollejolles.github.io/pirecorder/](http://jollejolles.github.io/pirecorder/).
1. [quick guide ](https://jollejolles.github.io/pirecorder/quick-guide.html)
2. [the pirecorder package](https://jollejolles.github.io/pirecorder/pirecorder-package.html)
3. [setting up your raspberry pi](https://jollejolles.github.io/pirecorder/1-setting-up-raspberry-pi.html)
4. [installing pirecorder](https://jollejolles.github.io/pirecorder/2-installing-pirecorder.html)
5. [position and calibrate the camera](https://jollejolles.github.io/pirecorder/3-position-and-calibrate-camera.html)
6. [configure recording settings](https://jollejolles.github.io/pirecorder/4-configure-recording-settings.html)
7. [configure camera settings](https://jollejolles.github.io/pirecorder/5-configure-camera-settings.html)
8. [record and schedule recordings](https://jollejolles.github.io/pirecorder/6-recording-and-scheduling.html)
9. [converting media](https://jollejolles.github.io/pirecorder/7-convert-media.html)
10. [run from the command line](https://jollejolles.github.io/pirecorder/8-run-from-commandline.html)

## Tests
To test all functionalities of the pirecorder package, run the `tests/test.py` file ([here](https://github.com/JolleJolles/pirecorder/tree/master/tests/test.py)), or alternatively run commands manually using the documented jupyter files [here](https://github.com/JolleJolles/pirecorder/tree/master/notebooks). Note that running the tests will require user input as some of the functionalities are interactive.

## Development
*pirecorder* is developed by Dr Jolle Jolles, a research fellow at the Max Planck Institute of Animal Behavior, and at the Zukunftskolleg, Institute of Advanced Study at the University of Konstanz.

For an overview of version changes see the [CHANGELOG](https://github.com/jollejolles/pirecorder/blob/master/CHANGELOG) and for detailed changes see the [commits page](https://github.com/jollejolles/pirecorder/commits/). Please submit bugs or feature requests to the GitHub issue tracker [here](https://github.com/jollejolles/pirecorder/issues).

Contributions to this package are welcomed via the usual pull request mechanism.

## Citing
If you use pirecorder in your research, please cite the accompanying paper:

```
@misc{Jolles2020,
      title = {pirecorder: controlled and automated image and video recording with the raspberry pi},
      author = {Jolles, Jolle W.},
      year = {2020},
      volume = {5},
      number = {54},
      pages = {2584},
      doi = {https://doi.org/10.21105/joss.02584}
}
```

## License
Released under a Apache 2.0 License. See [LICENSE](https://github.com/JolleJolles/pirecorder/blob/master/LICENSE) for details.
