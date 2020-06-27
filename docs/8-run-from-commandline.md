---
layout: page
title: 8 Run from command line
nav_order: 10
---
# Run pirecorder from command line

When pirecorder is installed, it comes with a added functionality to run of all modules straight from the command line for ease of use.
{: .fs-6 .fw-300 }

All the same parameters can be set as when using pirecorder in Python, so see the respective documentation pages for a detailed explanation. Below just the bash commands are given with all parameters for the different modules.

### Camera stream
```
stream --cameratype "v2" --framerate 8 --vidsize 0.2 --rotation 0 \
       --imgoverlay "/home/pi/overlay.jpg"
```

### Camera configuration Stream
```
camconfig --auto True --framerate 20 --iso 200 --res (1640,1232) --vidsize 0.3
```

### Recording
```
record --configfile "pirecorder.conf"
```

### Scheduling
```
schedule --jobname None --timeplan "* * * * *" --enable True --showjobs False \
         --delete "job" --test True --configfile "pirecorder.conf"
```

### Converting
```
convert --indir VIDEOS --outdir CONVERTED --type ".h264" --withframe True \
        --pools 4 --resizeval 0.5 --sleeptime 5 --delete False
```
