
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
import cPickle
gains = []

# Open camera stream to get the right gains
with picamera.PiCamera() as camera:
    camera.resolution = (1280, 720)
    camera.awb_mode = 'off'
    
    # Start off with ridiculously low gains
    rg, bg = (0.5, 0.5)
    camera.awb_gains = (rg, bg)
    with picamera.array.PiRGBArray(camera, size=(128, 72)) as output:
        
        # Allow 50 attempts to fix AWB
        for i in range(50):
            
            # Capture a tiny resized image in RGB format, and extract the
            # average R, G, and B values
            camera.capture(output, format='rgb', resize=(128, 72), use_video_port=True)
            r, g, b = (np.mean(output.array[..., i]) for i in range(3))
            print('R:%5.2f, B:%5.2f = (%5.2f, %5.2f, %5.2f)' % (
                rg, bg, r, g, b))
            
            # Adjust R and B relative to G, but only if they're significantly
            # different (delta +/- 2)
            if abs(r - g) > 2:
                if r > g:
                    rg -= 0.1
                else:
                    rg += 0.1
            if abs(b - g) > 1:
                if b > g:
                    bg -= 0.1
                else:
                    bg += 0.1
            
            # Show output
            camera.awb_gains = (rg, bg)
            output.seek(0)
            output.truncate()

# Store gains
gains = [(rg, bg)]
with open("setup/gains.yml", 'w') as f:
    yaml.safe_dump(gains, f, default_flow_style=False)
print "Gains:", gains, "stored..!"

