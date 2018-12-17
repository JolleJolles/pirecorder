#! /usr/bin/env python
#
# Copyright (C) 2015-2018 Jolle Jolles <j.w.jolles@gmail.com>

from __future__ import print_function
from setuptools import setup
from animrec.__version__ import __version__


DESCRIPTION = 'AnimRec: controlled media recording with the RPi'
LONG_DESCRIPTION = """\
AnimRec is a python package designed to help facilitate automated
recording using the RPi, specifically with easy, customized, repeated
image and video recording for behavioural scientists in mind.
"""

def check_dependencies():
    install_requires = []

    # Make sure dependencies exist
#    try:
#        import picamera
#    except ImportError:
#        install_requires.append('picamera')
    try:
        import pathos
    except ImportError:
        install_requires.append('pathos')
    try:
        import socket
    except ImportError:
        install_requires.append('socket')
    try:
        import yaml
    except ImportError:
        install_requires.append('pyyaml')
    try:
        import localconfig
    except ImportError:
        install_requires.append('localconfig==0.4.2')
    try:
        import animlab
    except ImportError:
        print("Package animlab is required. To install development version:")
        print("pip install git+https://github.com/JolleJolles/animlab.git")

    return install_requires


if __name__ == "__main__":

    install_requires = check_dependencies()

    setup(name='animrec',
          author='Jolle Jolles',
          author_email='j.w.jolles@gmail.com',
          description=DESCRIPTION,
          long_description=LONG_DESCRIPTION,
          url='http://jollejolles.com',
          download_url='https://github.com/jolleslab/AnimRec',
          version=__version__,
          install_requires=install_requires,
          packages=['animrec'])
