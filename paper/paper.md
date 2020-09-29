---
title: 'pirecorder: Controlled and automated image and video recording with the raspberry pi'
tags:
  - Python
  - raspberry pi
  - camera
  - recording
  - video
  - automation
authors:
  - name: Jolle W. Jolles
    orcid: 0000-0003-0872-7098
    affiliation: "1, 2"
affiliations:
 - name: Department of Collective Behaviour, Max Planck Institute of Animal Behaviour, Konstanz, Germany
   index: 1
 - name: Zukunftskolleg, Institute of Advanced Study, University of Konstanz, Germany
   index: 2
date: 6 Jul 2020
bibliography: paper.bib
---

# Summary
A fundamental component of empirical research is the acquisition of accurate, consistent, and often significant amounts of data. Specifically, researchers often require large numbers of controlled and often parallel image and video recordings. For this the raspberry pi, a small, single-board computer that brings together open-source principles with sensor and controller interfaces, and highly customisable programming capabilities, provides a great, low cost solution. Indeed, in recent years, the raspberry pi has been increasingly taken up by the scientific community [@Fletcher2019] and used in a wide range of projects that required the collection of high quality image data, from sub-micron resolution microscopy [@Aidukas2019], and deep sea video recordings [@Phillips2019], to motion-triggered camera trapping [@Nazir2017; @Prinz2016], high-throughput behavioural assessments [@Geissmann2017; @Todd2017; @Jolles2019], long-term home cage monitoring [@Singh2019], and the automated tracking of animal groups [@Alarcon-Nieto2018; @Jolles2018; @Jolles2020].

# Statement of need
So far, researchers have often relied on writing their own recordings scripts to take still photographs and videos from the command line (using `raspistill` and `raspivid`), control the camera module with `picamera` in Python [@Jones2017], or trigger recordings by motion-detection  ([Motion](https://motion-project.github.io)). Also some specific solutions exist, such as a web-based interface to run recordings [@Singh2019] and advanced software that converts the raspberry pi in a dedicated behavioural profiling machine [@Geissmann2017]. However, there is still a need for a complete solution that helps researchers, especially those with limited coding skills, to easily set up and configure their raspberry pi and run large numbers of controlled and automated image and video recordings. Here I present `pirecorder` to overcome this need.

# Functionality
`pirecorder` is a Python package, built on the picamera [@Jones2017] and OpenCV [@Bradski2000] libraries, that provides a flexible solution for the collection of consistent image and video data. It consists of a number of interconnected modules to facilitate key aspects of media recording: 1) setting-up and configuring the camera, 2) recording images, videos, time-lapses, and standardised video sequences with automatic file-naming, 3) easy scheduling of future recordings, and 4) converting of recorded media with resize, timestamp, and monitoring options. All functionalities are designed to make it very straightforward, even for users with limited coding experience, to configure, initiate, schedule, and convert recordings. In particular, `pirecorder` offers interactive streaming functionalities to facilitate users in positioning and focusing the camera, selecting the desired white-balance and other image parameters using trackbars, and set the ideal camera shutter speed. Furthermore, `pirecorder` comes with a dedicated documentation website with detailed information and tutorials ([jollejolles.github.io/pirecorder](https://jollejolles.github.io/pirecorder/)) as well as a set of annotated [Jupyter Notebooks](https://github.com/JolleJolles/pirecorder/tree/master/notebooks) to help users integrate the raspberry pi and `pirecorder` in their work.

![Screenshots of pirecorder in action, from configuring the camera with the interactive video stream, running recordings, testing and scheduling future recordings, and converting recorded media.](Figure1.jpg)

A core functionality of `pirecorder` is that it works with configuration files. These files make it possible to store a wide range of camera and recording settings that are then automatically used for recordings without requiring further user input. Furthermore, multiple configuration files can be stored and used, such as to easily start recordings for different experimental contexts or treatments. Configuration files can be edited directly, or parameters can be set in python or using the interactive video stream functionalities. Recordings can be easily initiated remotely, such as via an SSH connection, and scheduled to automatically start and stop at specific times in the future. By its use of configuration files and the automatic naming of files, `pirecorder` also makes it possible to start controlled recordings on multiple raspberry pi's simultaneously, such as with [csshX](https://github.com/brockgr/csshx), which sends the same command to multiple computers at once.  

# Use cases
`pirecorder` has already been used successfully in a number of studies, such as to facilitate the high-throughput recording of large numbers of individuals and shoals of fish [@Jolles2018; @Jolles2019, @Jolles2020] and more recently, the autonomous long-term recording of fish each day, every day, for the first four-month of their life (in prep). By facilitating and streamlining controlled and automated image and video recordings, I hope `pirecorder` will increasingly help scientists simplify and improve the collection of high quality data and thereby ultimately enhance their research.

# Acknowledgements
This work was made possible by an Alexander von Humboldt Postdoctoral Fellowship, a Zukunftskolleg Postdoctoral Fellowship, and a research grant from the Dr. J.L. Dobberke Foundation. I would also like to thank Lucas Koerner and Jan Heuschele for helpful feedback on the paper and the package.

# References
