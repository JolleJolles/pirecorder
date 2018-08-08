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

    dependency_links = ['http://github.com/joljols/animlab/tarball/']

    return install_requires, dependency_links


if __name__ == "__main__":

    install_requires = check_dependencies()

    setup(name='animtrack',
          author='Jolle Jolles',
          author_email='j.w.jolles@gmail.com',
          description='AnimTrack: behavioural tracking of free-moving animals',
          url='http://jollejolles.com',
          download_url='https://github.com/jolleslab/AnimTrack',
          version=0.0.1,
          install_requires=install_requires,
          dependency_links=dependency_links,
          packages=['animtrack'])
