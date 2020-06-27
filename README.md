[![PyPI version](https://badge.fury.io/py/pirecorder.svg)](https://badge.fury.io/py/pirecorder) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.2529515.svg)](https://doi.org/10.5281/zenodo.2529515)

# pirecorder
**A Python package for controlled and automated image and video recording with the raspberry pi**

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

## Modules
*pirecorder* consists of a main `PiRecorder` module to run image and video recordings, `stream` and `camconfig` modules with interactive user interfaces for help setting up, calibrating, and configuring the camera, a `schedule` module for scheduling future recordings, and a `convert` module for the easy converting of (folders of) recorded images and videos.

## Install
To install the latest release, simply open a terminal window and enter:

```
pip install pirecorder
```

To install the latest development version, enter:

```
pip install git+https://github.com/jollejolles/pirecorder.git --upgrade
```

## Dependencies
*pirecorder* builds strongly on the [picamera](http://picamera.readthedocs.io/) package, uses [numpy](http://www.numpy.org/), [pyyaml](https://pyyaml.org), and [opencv](http://opencv.org) for some of its core functionality, and relies on various utility functions of the accompanying [pythutils](https://github.com/jolle/pythutils) package. Scheduling functionality is based on *CronTab* and the associated [python-crontab](https://pypi.org/project/python-crontab/) package. All dependencies are automatically installed with *pirecorder* except for:
* *OpenCV*: has to be manually installed due to its various dependencies on raspberry pi. Click [here](https://github.com/JolleJolles/pirecorder/tree/master/docs/other/install-opencv.md) for a quick install guide.
* *FFmpeg*: is only needed for the convert functionality of *pirecorder*. Click [here](https://github.com/JolleJolles/pirecorder/tree/master/docs/other/install-ffmpeg-raspberry-pi.md) and [here](https://github.com/JolleJolles/pirecorder/tree/master/docs/other/install-ffmpeg-osx.md) for guides to install on raspberry pi and OS X respectively.

## Documentation
For detailed documentation and tutorials about *pirecorder* and all its functionalities, see the dedicated website [jollejolles.github.io/pirecorder/](http://jollejolles.github.io/pirecorder/).
1. [quick guide ](https://github.com/jollejolles/pirecorder/tree/master/docs/quick-guide.md)
2. [the pirecorder package](https://github.com/jollejolles/pirecorder/tree/master/docs/pirecorder-package.md)
3. [setting up your raspberry pi](https://github.com/jollejolles/pirecorder/tree/master/docs/1-setting-up-raspberry-pi.md)
4. [installing pirecorder](https://github.com/jollejolles/pirecorder/tree/master/docs/2-installing-pirecorder.md)
5. [position and calibrate the camera](https://github.com/jollejolles/pirecorder/tree/master/docs/3-position-and-calibrate-camera.md)
6. [configure recording settings](https://github.com/jollejolles/pirecorder/tree/master/docs/4-configure-recording-settings.md)
7. [configure camera settings](https://github.com/jollejolles/pirecorder/tree/master/docs/5-configure-camera-settings.md)
8. [record and schedule recordings](https://github.com/jollejolles/pirecorder/tree/master/docs/6-recording-and-scheduling.md)
9. [converting media](https://github.com/JolleJolles/jollejolles/tree/master/docs/7-convert-media.md)
10. [run from the command line](https://github.com/jollejolles/pirecorder/tree/master/docs/8-run-from-commandline.md)

## Development
*pirecorder* is developed by Dr Jolle Jolles, a research fellow at the Max Planck Institute of Animal Behavior, and at the Zukunftskolleg, Institute of Advanced Study at the University of Konstanz.

For an overview of version changes see the [CHANGELOG](https://github.com/jollejolles/pirecorder/blob/master/CHANGELOG) and for detailed changes see the [commits page](https://github.com/jollejolles/pirecorder/commits/). Please submit bugs or feature requests to the GitHub issue tracker [here](https://github.com/jollejolles/pirecorder/issues).

## Citing
pirecorder was originally developed with the Biological Sciences in mind. If you use pirecorder in your research, please cite it as follows:

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
