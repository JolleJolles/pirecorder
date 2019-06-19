"""
Copyright 2015-2018 Jacob M. Graving <jgraving@gmail.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Modified by Jolle W. Jolles <j.w.jolles@gmail.com>

All modifications are Copyright (C) 2016-2019 Jolle W. Jolles
"""

from __future__ import print_function

from glob import glob
import numpy as np
import cv2
import pickle
import os

def calibrate(userinput,  grid_size = (9,7), imshow = False,
              imstore = True, framestep = 10, delay = 500):

    """
    Calibrate camera using a video of a chessboard or a sequence of images

    Parameters
    ----------
    userinput : input video file or folder of images
    grid_size : internal corners of calibration grid
    imshow : show/do not show the calibration images
    imstore : store/do not store the calibration images
    framestep : use every nth frame in the video
    delay : Delay in msecs between each image for imshow

    Returns
    -------
    calib_params : dict of parameters for undistorting images.
    """

    # User input
    if '*' in userinput:
        source = glob(userinput)
    else:
        source = cv2.VideoCapture(userinput)

    # Termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # Prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((grid_size[1]*grid_size[0],3), np.float32)
    objp[:,:2] = np.mgrid[0:grid_size[0],0:grid_size[1]].T.reshape(-1,2)

    # Arrays to store object points and image points from all the images.
    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.

    # Make directory with analysed images
    if imstore == True:
        calibimgdir = userinput.split(".",1)[0]+"_calibrated_imgs"
        if not os.path.exists(calibimgdir):
            print("Directory made for calibrated images")
            os.makedirs(calibimgdir)
        else:
            print("Directory of calibrated images already exists")

    # Start loop over images/video frames
    i = -1
    while True:
        i += 1
        # Check if list of images of video
        if isinstance(source, list):
            # images
            if i == len(source):
                break
                img = cv2.imread(source[i])
        else:
            # video
            retval, img = source.read()
            if not retval:
                break
            if i % framestep != 0:
                continue

        # Search for chessboard
        print("Searching for chessboard in image/frame " + str(i+1) + "...",end='')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, grid_size, None, flags = (cv2.CALIB_CB_ADAPTIVE_THRESH))

        # If found, add object points, image points (after refining them)
        if ret == True:
            print("Corners found on image/frame " + str(i+1) + ".",end='')
            objpoints.append(objp)
            corners2 = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
            imgpoints.append(corners2)

            img = cv2.drawChessboardCorners(img, grid_size, corners2,ret)
            imgsmall = cv2.resize(img, None, fx = 0.5, fy = 0.5)

            # Draw and display the corners
            if imshow == True:
                cv2.imshow('img',imgsmall)
                cv2.waitKey(delay)
            if imstore == True:
                cv2.imwrite(os.path.join(calibimgdir, 'frame_%04d.png' % (i+1)), imgsmall)

    if imshow == True:
        cv2.destroyAllWindows()
        for i in range(5):
            cv2.waitKey(1)

    if len(objpoints) > 0 and len(imgpoints) > 0:
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
        calib_params = {"ret" : ret, "mtx" : mtx, "dist" : dist, "rvecs" : rvecs, "tvecs" : tvecs}

        total_error = 0
        for i in xrange(len(objpoints)):
            imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
            error = cv2.norm(imgpoints[i],imgpoints2, cv2.NORM_L2)/len(imgpoints2)
            total_error += error
        mean_error = total_error/len(objpoints)

        print("Calibration successful! Mean error: ", mean_error)

    else:
        print("No calibration points found!")
        calib_params = None

    return calib_params


def save_calib(filename, calib_params):

    """
    Saves calibration parameters as '.pkl' file.

    Parameters
    ----------
    filename : Path to save file, must be '.pkl' extension
    calib_params : Calibration parameters to save

    Returns
    -------
    saved : bool that states if saving was succesfully
    """

    if type(calib_params) != dict:
        raise TypeError("calib_params must be 'dict'")

    output = open(filename, 'wb')

    try:
        pickle.dump(calib_params, output)
    except:
        raise IOError("filename must be '.pkl' extension")

    output.close()

    saved = True

    return saved


def load_calib(filename):

    """
    Loads calibration parameters from '.pkl' file.

    Parameters
    ----------
    filename : str8; path to load file, must be '.pkl' extension

    Returns
    -------
    calib_params : dict; parameters for undistorting images.
    """

    pkl_file = open(filename, 'rb')

    try:
        calib_params = pickle.load(pkl_file)
    except:
        raise IOError("File must be '.pkl' extension")

    pkl_file.close()

    return calib_params


def undistort(image, calib_params, crop = True):

    """
    Returns undistorted image using calibration parameters.

    Parameters
    ----------
    image : image to be undistorted
    calib_params : calibration parameters from calibrate_camera() script
    crop : crop/do not crop image to the optimal region of interest

    Returns
    -------
    dst : numpy array of undistorted image.
    """

    try:
        ret = calib_params["ret"]
        mtx = calib_params["mtx"]
        dist = calib_params["dist"]
        rvecs = calib_params["rvecs"]
        tvecs = calib_params["tvecs"]
    except:
        raise TypeError("calib_params must be 'dict'")

    img = image
    h,  w = img.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))

    # undistort
    mapx, mapy = cv2.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (w,h), 5)
    dst = cv2.remap(img, mapx, mapy, cv2.INTER_LINEAR)

    # crop the image
    if crop:
        x,y,w,h = roi
        dst = dst[y:y+h, x:x+w]

    return dst
