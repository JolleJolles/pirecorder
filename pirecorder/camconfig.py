#! /usr/bin/env python
"""
Copyright (c) 2020-2023 Jolle Jolles <j.w.jolles@gmail.com>

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

import cv2
import time
import argparse

from pythutils.mediautils import picamconv
from pythutils.mathutils import maxrect
from pythutils.sysutils import checkfrac, isrpi, lineprint

def Camconfig(cam = None, auto = None, iso = 200, framerate = 20,
              res = (1640, 1232), vidsize = 0.4):

    """
    Opens a video stream to configure a wide array of camera parameters
    Note: A screen resolution of at least 800x600 is strongly recommended
    """

    if not isrpi():
        lineprint("PiRecorder only works on a raspberry pi. Exiting..")
        return

    import picamera
    import picamera.array

    def nothing(x):
        pass

    if cam == None:
        cam = picamera.PiCamera()
        cam.resolution = res
        cam.iso = iso
        cam.framerate = framerate
        time.sleep(2)
    if cam == None or (auto == None or auto == True):
        cam.exposure_mode = "auto"
        set_auto = 1
    else:
        set_auto = 0

    res = (cam.resolution[0]*vidsize, cam.resolution[1]*vidsize)
    res = (int(res[0]*cam.zoom[2]),int(res[1]*cam.zoom[3]))
    if (res[0]*res[1])>=(1640*1232):
        res = maxrect(dims, maxdims = (1640,1232), decimals = 0)
    cam.resolution = picamconv(res)

    cv2.namedWindow("Stream", cv2.WND_PROP_FULLSCREEN)
    cv2.namedWindow("Config", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Stream", cv2.WND_PROP_AUTOSIZE, cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Stream", cam.resolution[0], cam.resolution[1])

    config = []
    isos = [100,200,320,400,500,640,800]

    set_rot  = cam.rotation*180
    set_fps  = int(cam.framerate)
    set_iso  = [i for i,j in enumerate(isos) if j==cam.iso][0]
    set_comp = cam.exposure_compensation+25
    set_shut = cam.shutter_speed
    set_red  = int(float(cam.awb_gains[0])*10)
    set_blue = int(float(cam.awb_gains[1])*10)
    set_bri  = cam.brightness
    set_con  = cam.contrast+100
    set_sat  = cam.saturation+100
    set_shar = cam.sharpness+100

    cv2.createTrackbar("rotation (0deg/180deg)", "Config", set_rot, 1, nothing)
    cv2.createTrackbar("framerate", "Config", set_fps, 40, nothing)
    cv2.createTrackbar("automatic (off/on)", "Config", set_auto, 1, nothing)
    cv2.createTrackbar("iso", "Config", set_iso, 6, nothing)
    cv2.createTrackbar("compensation", "Config", set_comp, 50, nothing)
    cv2.createTrackbar("shutterspeed (ms)", "Config", set_shut, 99999, nothing)
    cv2.createTrackbar("red gain", "Config", set_red, 80, nothing)
    cv2.createTrackbar("blue gain", "Config", set_blue, 80, nothing)
    cv2.createTrackbar("brightness", "Config", set_bri, 100, nothing)
    cv2.createTrackbar("contrast", "Config", set_con, 200, nothing)
    cv2.createTrackbar("saturation", "Config", set_sat, 200, nothing)
    cv2.createTrackbar("sharpness", "Config", set_shar, 200, nothing)

    rawCapture = picamera.array.PiRGBArray(cam, size=cam.resolution)
    lineprint("Streaming interactive video..")
    with rawCapture as stream:
        while True:
            cam.capture(stream, format="bgr", use_video_port=True)
            image = stream.array

            rot  = cv2.getTrackbarPos("rotation (0deg/180deg)", "Config")
            fps  = cv2.getTrackbarPos("framerate", "Config")
            auto = cv2.getTrackbarPos("automatic (off/on)", "Config")
            iso  = cv2.getTrackbarPos("iso", "Config")
            comp = cv2.getTrackbarPos("compensation", "Config")
            shut = cv2.getTrackbarPos("shutterspeed (ms)", "Config")
            red  = cv2.getTrackbarPos("red gain", "Config")
            blue = cv2.getTrackbarPos("blue gain", "Config")
            bri  = cv2.getTrackbarPos("brightness", "Config")
            con  = cv2.getTrackbarPos("contrast", "Config")
            sat  = cv2.getTrackbarPos("saturation", "Config")
            shar = cv2.getTrackbarPos("sharpness", "Config")

            cam.rotation = [0,180][rot]
            cam.framerate = max(fps,1)
            cam.exposure_mode = ["off","auto"][auto]
            cam.iso = isos[iso]
            cam.exposure_compensation = comp-25
            cam.awb_mode = cam.exposure_mode

            if cam.exposure_mode == "off":
                cam.shutter_speed = shut
                maxshut = int(float(1/cam.framerate)*1000000)
                if shut > maxshut:
                    cv2.setTrackbarPos("shutterspeed (ms)","Config", maxshut)
                cam.awb_gains = (red/10, blue/10)

            if cam.exposure_mode == "auto":
                cam.shutter_speed = 0
                shut = cam.exposure_speed
                red, blue = [int(float(i)*10) for i in cam.awb_gains]
                cv2.setTrackbarPos("shutterspeed (ms)", "Config", shut)
                cv2.setTrackbarPos("red gain", "Config", red)
                cv2.setTrackbarPos("blue gain", "Config", blue)

            cam.brightness = bri
            cam.contrast = con-100
            cam.saturation = sat-100
            cam.sharpness = shar-100

            cv2.imshow("Stream", image)
            stream.truncate(0)

            k = cv2.waitKey(10) & 0xFF
            if k == ord("s"):
                if cam.shutter_speed == 0:
                    shutterspeed = cam.exposure_speed
                else:
                    shutterspeed = cam.shutter_speed
                gains = tuple([round(float(i),2) for i in cam.awb_gains])
                config = {"automode": [False,True][auto],
                          "vidfps": cam.framerate,
                          "rotation": cam.rotation,
                          "gains": gains,
                          "brightness": cam.brightness,
                          "contrast": cam.contrast,
                          "saturation": cam.saturation,
                          "iso":cam.iso,
                          "sharpness": cam.sharpness,
                          "compensation": cam.exposure_compensation,
                          "shutterspeed": shutterspeed}
                break
            if k == 27:
                lineprint("User exited..")
                break

        rawCapture.close()
        cam.close()
        cv2.destroyAllWindows()
        cv2.waitKey(1)

        return config


def config():

    """To run the camconfig function from the command line"""

    parser = argparse.ArgumentParser(prog="Camconfig",
             description=Camconfig.__doc__,
             formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("-a","--auto", default=None, type=str, metavar="")
    parser.add_argument("-i","--iso", default=200, type=int, metavar="")
    parser.add_argument("-f","--framerate", default=20, type=int, metavar="")
    parser.add_argument("-r","--res", default=(1640,1232), metavar="")
    parser.add_argument("-v","--vidsize", default=0.4, type=float, metavar="")

    args = parser.parse_args()
    res = tuple(args.res)
    Camconfig(auto = args.auto, iso = args.iso, framerate = args.framerate,
              res = res, vidsize = args.vidsize)
