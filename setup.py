#! /usr/bin/env python
#
# Copyright (C) 2015-2018 Jolle Jolles <j.w.jolles@gmail.com>

from setuptools import setup

def check_dependencies():
    install_requires = []

    # Make sure dependencies exist
    try:
        import picamera
    except ImportError:
        install_requires.append('picamera')
    try:
        import socket
    except ImportError:
        install_requires.append('socket')
    try:
        import yaml
    except ImportError:
        install_requires.append('yaml')
    try:
        import localconfig
    except ImportError:
        install_requires.append('localconfig==0.4.2')

    return install_requires


if __name__ == "__main__":

    install_requires = check_dependencies()

    setup(name='animrec',
          author='Jolle Jolles',
          author_email='j.w.jolles@gmail.com',
          description='AnimRec: controlled video recording',
          url='http://jollejolles.com',
          download_url='https://github.com/jolleslab/AnimRec',
          version="1.0.0",
          install_requires=install_requires,
          dependency_links=['git+ssh://git@github.com/joljols/animlab.git'],
          packages=['animrec'])
