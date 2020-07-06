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
Controlled and automated image and video recording is a fundamental component of research across the natural and social sciences for the collection of accurate, consistent, and significant amounts of data. While many commercial products exist for the recording of high-quality images and video, the Raspberry Pi, a small single-board computer built on open-source principles, is increasingly being used by the scientific community due to its low cost and high customizability [@Fletcher2019]. For example, the raspberry pi is being used for sub-micron resolution microscopy [@Aidukas2019], deep sea video recording [@Phillips2019], motion-triggered camera trapping [@Prinz2016; @nazir2017], high-throughput and real-time profiling of behaviour [@Geissmann2017; @Todd2017; @Jolles2019], and automated monitoring of animal groups [@Jolles2018; @Alarcon-Nieto2018].

The majority of existing research uses custom-build solutions that use the native software that comes with the Raspberry Pi, specifically, `raspistill` and `raspivid` to take still photographs and vides from the command line, and `picamera` [@Jones2018] to control the Raspberry Pi camera module from within Python. Also software exists to monitor video streams and run motion-triggered recordings ([Motion](https://motion-project.github.io)). However, so far an easy-to-use solution for image and video recording with the Raspberry Pi had been lacking, especially with the consistency and control that is often required in the natural sciences. `pirecorder` aims to fill this gap.

\autoref{fig: Figure1}![Caption for example figure.\label{fig:Figure1}](figure1.jpg)

`pirecorder` is a Python package build on the picamera [@Jones2018] and OpenCV [@Bradski2000] libraries that consists of the main `PiRecorder` module to configure and run recordings, a live `stream` module with user interface to calibrate the raspberry pi camera position, focus, and potential region of interest, a `camconfig` module to dynamically configure the camera settings using a live video stream, a `schedule` module for scheduling future recordings, and a `convert` module for the easy converting of (folders of) recorded images and videos with the option to resize, add timestamps, and monitor folders for automatic conversion.

`pirecorder` makes it very easy to record single images and videos, timelapses, and standardized sequences of videos with automatic filenaming. It is possible to set a wide range of camera and recording settings that are then automatically used for future recordings without further user input. Multiple configuration files can be created and called for specific recordings and easily edited directly or interactively via a live video stream. Recordings can thereby be easily initated remotely such as via an SSH connection to the Raspberry Pi, or scheduled to start automatically at specific times in the future using simple-to-use monitoring commands.

Some other specific solutions for media recording with the Raspberry Pi for scientific research have been described in the literature [@Geissmann2017; @Singh2019]. The key contribution of `pirecorder` is that it provides a complete and simple-to-use solution for controlled and automated image and video recording. All modules work from Python and the command line and require very little previous coding experience, with interactive streaming modes making it easy to set up and configure the camera. `pirecorder` also comes with a dedicated website with detailed documentation and tutorials ([jollejolles.github.io/pirecorder](https://jollejolles.github.io/pirecorder/)), and includes a set of annotated [Jupyter Notebooks](https://github.com/JolleJolles/pirecorder/tree/master/notebooks).

`pirecorder` has already been used successfully for the controlled and high-throughput recording of individuals and groups of fish [@Jolles2018; @Jolles2019], and facilitated the autonomous recording of 24 fish tanks every day for a 4+ month period without any user input. I hope that the `pirecorder` package helps put control for media recording back in the hands of the scientist and provide a low-cost solution for use of the raspberry pi.


# Acknowledgements
This work was made possible by a postdoctoral fellowship from the Alexander von Humboldt-Stiftung, a postdoctoral fellowship from the Zukunfstkolleg, Institute for Advanced Study, and a research grant from the Dr. J.L. Dobberke Foundation.

# References
