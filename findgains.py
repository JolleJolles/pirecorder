
# coding: utf-8

# In[ ]:


# Script to automatically find gains on a rpi<
# Author: JW Jolles
# Version 2.0
# Last updated: 12 Apr 2018
# Script written based on tips from Dave Jones.

# Latest changes
# 2.0 Updated function to be part of Animrec, new name, better comments
# 1.2 Prepared script for integration with github jolpi project
# 1.1 file now stores best gains in file

# Set workspace
import picamera
import picamera.array
import numpy as np
import yaml
import os

# Open camera stream to get the right gains
with picamera.PiCamera() as camera:
    camera.resolution = (1280, 720)
    camera.awb_mode = 'off'
    
    # set custom brightness
    camera.brightness = 45
    brightfile = "setup/cusbright.yml"
    if os.path.exists(brightfile):
        with open(brightfile) as f:
            camera.brightness += yaml.load(f)
    
    # Start off with ridiculously low gains
    rg, bg = (0.5, 0.5)
    camera.awb_gains = (rg, bg)
    with picamera.array.PiRGBArray(camera, size=(128, 72)) as output:
        
        # Allow 100 attempts to fix AWB
        for i in range(100):
            
            # Capture a tiny resized image in RGB format, and extract the
            # average R, G, and B values
            camera.capture(output, format='rgb', resize=(128, 80), use_video_port=True)
            r, g, b = (np.mean(output.array[..., i]) for i in range(3))
            print('R:%5.2f, B:%5.2f = (%5.2f, %5.2f, %5.2f)' % (
                rg, bg, r, g, b))
            
            # Adjust R and B relative to G, but only if they're significantly
            # different (delta +/- 2)
            if abs(r - g) > 2:
                if r > g:
                    rg -= 0.05
                else:
                    rg += 0.05
            if abs(b - g) > 1:
                if b > g:
                    bg -= 0.05
                else:
                    bg += 0.05
            
            # Show output
            camera.awb_gains = (rg, bg)
            output.seek(0)
            output.truncate()

# Store gains
gains = str((round(rg,2), round(bg,2)))
with open("setup/cusgains.yml", 'w') as f:
    yaml.safe_dump(gains, f, default_flow_style=False)
print "Gains:", gains, "stored..!"

