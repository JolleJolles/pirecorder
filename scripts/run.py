import animrec

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

# Run recorded
AT.record()
