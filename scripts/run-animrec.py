# Import the package
import animrec

# Run showcam function to optimize camera position
animrec.showcam(res = (640, 480), cross = False)

# Initiate the recorder instance
AR = animrec.Recorder()

# General config
AR.set_config(recdir = "", label = "test", rectype = "vid",
              brightness = 45, contrast = 10, saturation = -100, iso = 200,
              sharpness = 0, compensation = 0, shutterspeed = 8000,
              quality = 11, brighttune = 0)

# Config for videos
AR.set_config(viddims = (1640, 1232), vidfps = 24, vidduration = 5, viddelay = 2)

# Config for images
AR.set_config(imgdims = (3280, 2464), imgfps = 1, imgwait = 5.0, imgnr = 100,
              imgtime = 600)

# Draw the region of interest
AR.set_roi()

# Dynamically set the Gains
AR.set_gains()

# Run record function
AR.record()
