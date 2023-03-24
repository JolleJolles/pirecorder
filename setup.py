#! /usr/bin/env python
"""
Copyright (c) 2015 - 2023 Jolle Jolles <j.w.jolles@gmail.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at:

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from setuptools import setup, find_packages
import sys

exec(open("pirecorder/__version__.py").read())

DESCRIPTION="""A python package for controlled and automated image and video \
recording with the raspberry pi"""

DISTNAME="pirecorder"
MAINTAINER="Jolle Jolles"
MAINTAINER_EMAIL="j.w.jolles@gmail.com"
URL="https://github.com/jollejolles"
DOWNLOAD_URL="https://github.com/jollejolles/pirecorder/archive/v3.4.0.tar.gz"

with open("README.md") as f:
    readme = f.read()

if __name__ == "__main__":

    setup(name=DISTNAME,
          author=MAINTAINER,
          author_email=MAINTAINER_EMAIL,
          maintainer=MAINTAINER,
          maintainer_email=MAINTAINER_EMAIL,
          description=DESCRIPTION,
          long_description=readme,
          long_description_content_type="text/markdown",
          url=URL,
          install_requires=["pythutils",
                            "multiprocess",
                            "python-crontab",
                            "croniter",
                            "cron-descriptor",
                            "pyyaml",
                            "future",
                            "numpy==1.16.5; python_version>='2' and python_version<'3'",
                            "numpy; python_version>='3'",
                            "localconfig==0.4.2; python_version>='2' and python_version<'3'",
                            "localconfig==1.1.1; python_version>='3'"],
          entry_points={"console_scripts": [
                            "stream = pirecorder.stream:strm",
                            "camconfig = pirecorder.camconfig:config",
                            "record = pirecorder.pirecorder:rec",
                            "schedule = pirecorder.schedule:sch",
                            "convert = pirecorder.convert:conv"],},
          download_url=DOWNLOAD_URL,
          version=__version__,
          license="License :: OSI Approved :: Apache Software License",
          platforms=["Windows", "Linux", "Mac OS-X"],
          packages=find_packages(),
          include_package_data=True,
          classifiers=[
                     "Intended Audience :: Science/Research",
                     "Programming Language :: Python :: 2.7",
                     "Programming Language :: Python :: 3",
                     "License :: OSI Approved :: Apache Software License",
                     "Topic :: Scientific/Engineering :: Visualization",
                     "Topic :: Scientific/Engineering :: Image Recognition",
                     "Topic :: Scientific/Engineering :: Information Analysis",
                     "Topic :: Multimedia :: Video",
                     "Operating System :: POSIX",
                     "Operating System :: Unix",
                     "Operating System :: MacOS"],
          )
