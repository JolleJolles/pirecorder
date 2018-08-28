#! /usr/bin/env python
#
# Copyright (C) 2015-2018 Jolle Jolles <j.w.jolles@gmail.com>

from setuptools import setup
from animrec.version import __version__

def check_dependencies():
    install_requires = []

    # Make sure dependencies exist
    try:
        import picamera
    except ImportError:
        print "Package picamera is required to run animrec as this package was",
        print "designed for the RaspberryPi. To install manually: pip install",
        print "picamera"
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
        print "Package animlab is required. To install development version:"
        print "pip install git+https://github.com/joljols/animlab.git"

    return install_requires


if __name__ == "__main__":

    install_requires = check_dependencies()

    setup(name='animrec',
          author='Jolle Jolles',
          author_email='j.w.jolles@gmail.com',
          description='AnimRec: controlled video recording',
          url='http://jollejolles.com',
          download_url='https://github.com/jolleslab/AnimRec',
          version=__version__,
          install_requires=install_requires,
          packages=['animrec'])
