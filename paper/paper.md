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
 - name: Zukunftskolleg, Institute of Advanced Science, University of Konstanz, Germany
   index: 2
date: 25 June 2020
bibliography: paper.bib
---

# Summary
*Begin your paper with a summary of the high-level functionality of your software for a non-specialist reader. Avoid jargon in this section.*

*some sentences that explain the software functionality and domain of use to a non-specialist reader.*

*Explain the research applications of the software. what problems the software is designed to solve and who the target audience is.*

*A clear Statement of Need that illustrates the research purpose of the software.*

*describe how this software compares to other commonly-used packages*

*Mention (if applicable) a representative set of past or ongoing research projects using the software and recent scholarly publications enabled by it.*

Builds heavily on the picamera package [@Jones]

For example Aidukas et al [@Aidukas:2019] captured raw 10-bit Bayer images using the picamera package for sub-micron resolution microscopy.


[detailed documentation](https://jollejolles.github.io/pirecorder/), pirecorder includes a set of Jupyter Notebooks with examples.

Used successfully for the controlled and repeated video recording of individually housed fish over multi-week period [@Jolles2019] as well as groups of fish [@Jolles2018], which enabled the subsequent tracking of individual identities. Also more recently we filmed 24 tanks of fish every day for 4+ months from dawn till dusk.

```python
import pirecorder

# Initiate the recorder class
rec = pirecorder.PiRecorder(configfile = "myconfig.conf")

# Position and calibrate the camera; add region of interest
rec.stream()

# Dynamically set the camera settings
rec.camconfig()

# Set configuration manually
rec.settings(recdir = "pirecorder/recordings", subdirs = False, label = "test", \
             rectype = "img", rotation = 0, brighttune = 0, roi = None, \
             cameratype = None, imgdims = (2592,1944), imgquality = 50, \
             imgwait = 5.0, imgnr = 12, imgtime = 60, viddims = (1640,1232), \
             vidduration = 10, viddelay = 10, vidfps=24, vidquality = 11, \
             automode = True, gains = (1.0,2.5), iso = 200, compensation = 0,  \
             brightness = 45, contrast = 10, saturation = 0, sharpness = 0,
             shutterspeed = 8000)

# Run a recording
rec.record()

# Schedule a recording
rec.schedule(timeplan = "*/10 */2 10-15 * *", jobname = "rec1")

# Convert recordings
picamera.Convert(indir = "pirecorder/recordings")
```


# Acknowledgements
I acknowledge financial support from the Alexander von Humboldt-Stiftung (postdoctoral fellowship to JWJ), the Zukunfstkolleg, Institute for Advanced Study (postdoctoral fellowship to JWJ), and the Dr. J.L. Dobberke Foundation (research grant to JWJ),

# References
