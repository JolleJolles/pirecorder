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

The Raspberry Pi is a single-board, low-cost micro-computer built on open-source principles. This low-cost computer, developed by the Raspberry Pi Foundation, a UK charity that aims to educate people in coding and computing, is currently the most popular micro-computer available. The Raspberry Pi is also increasingly taken up by the scientific community [@Fletcher2019] and used as a central component in research projects across a range of fields. One of the foremost uses of the Raspberry Pi is image and video recording. 

Read barcodes on animals. [@Alarcon-Nieto2018] used multiple Raspberry Pi's as part of a long-term, automated monitoring system of birds housed in outdoor aviaries and were able to track individuals based small barcoded backpacks.

Builds heavily on the picamera package [@Jones2018], and uses OpenCV [@Bradski2000] for user-interfaces to dynamically control the raspberry pi camera settings.

For example @Aidukas2019 captured raw 10-bit Bayer images using the picamera package for sub-micron resolution microscopy.

Here is a figure:
\autoref{fig:example}
![Caption for example figure.\label{fig:example}](testfigure.jpg)

[detailed documentation](https://jollejolles.github.io/pirecorder/), pirecorder includes a set of Jupyter Notebooks with examples.

Used successfully for the controlled and repeated video recording of individually housed fish over multi-week period [@Jolles2019] as well as groups of fish [@Jolles2018], which enabled the subsequent tracking of individual identities. Also more recently we filmed 24 tanks of fish every day for 4+ months from dawn till dusk.




# Acknowledgements
This research was made possible by a postdoctoral fellowship from the the Alexander von Humboldt-Stiftung, a postdoctoral fellowship from the Zukunfstkolleg, Institute for Advanced Study, and a research grant from the Dr. J.L. Dobberke Foundation.

# References
