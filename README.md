# AnimRec
A python module for automated image and video recording on the RaspberryPi.

![logo](https://github.com/jolleslab/AnimRec/blob/master/images/AnimRec-logo.jpg)

Overview
------------



Installation
------------

Install:
```bash
pip install git+https://github.com/jolleslab/animrec.git
```

Dependencies
------------

AnimRec depends on [Python 2.7](http://www.python.org) and the [picamera](http://picamera.readthedocs.io/) package and makes use of various utility functions of the associated [AnimLab](https://github.com/joljols/animlab) package. AnimRec is created specifically for automated recording with the RaspberryPi, but is adaptable to broader possible instances.


Using AnimRec
--------
To use utility functions, e.g.:
```python
from animlab.utils import listfiles
from animlab.imutils import crop
from animlab.mathutils import points_to_angle
```
