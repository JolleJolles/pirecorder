#! /usr/bin/env python
#
# Controlled media recording library for the Rasperry-Pi
# Copyright (c) 2018 Jolle Jolles <j.w.jolles@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
from setuptools import setup
from __version__ import __version__


DESCRIPTION = 'AnimRec: Controlled media recording library for the Rasperry-Pi'
LONG_DESCRIPTION = """\
AnimRec is a python package designed to help facilitate automated
recording using the RPi, specifically with easy, customized, repeated
image and video recording for behavioural scientists in mind.
"""

def check_dependencies():
    install_requires = []

    # Make sure dependencies exist
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
