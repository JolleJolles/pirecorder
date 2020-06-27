---
layout: page
title: 5 Configure camera settings
nav_order: 7
---

# Configure camera settings
{: .no_toc }

When you have pirecorder running and are happy with the recording settings, you may want to further configure the camera settings to get your optimal recordings. Below I explain the various ways in which you can do that very easily with pirecorder.
{: .fs-6 .fw-300 }

## Table of contents
{: .no_toc .text-delta .fs-4 .fw-300 }

1. TOC
{:toc}
---

## Camera settings
It is possible to set a large number of camera settings with pirecorder: `rotation`, `gains`, `brightness`, `contrast`, `saturation`, `iso`, `sharpness`, `compensation`, and `shutterspeed`. A concise description all these parameters can be found at the bottom of this page. Below I go through the details of how to use the different parameters. As explained on the [configure recording settings page](4-configure-recording-settings.md), you can set them manually by editing your configuration file or when in Python and having a PiRecorder instance with the `settings` function.

To change the orientation of the camera set the `rotation` parameter either to `0` (normal) or `180` (upside down); to change the white balance set the `gains` parameter. This should be a tuple of blue and red gains values between 0 and 8, e.g. `(1.5, 1.85)`; to film in black and white set `saturation` to `-100`; to change the differences in luminance and color and get a more contrasting image increase the `contrast` parameter; to increase the sharpness of your recordings increase the `sharpness` parameter from a value from `-100` to `100`.

To get the optimal brightness level for your recordings you can tweak a number of parameters. For example, to get a brighter image, you could increase the `compensation`, increase the `brightness`, increase the `iso` or set a longer `shutterspeed`. Changing the compensation and iso values will change the amount of light that is allowed to enter the camera before recordings, which will affect the noise in the image. Brightness on the other hand is done in the post processing by stretching/compressing the range of values.

It is best to set `iso` to a low value and `compensation` to `0` to reduce image noise and keep `brightness` at its default intermediate value. Then if the image is too dark and image noise is not a problem for you, then first increase the `iso` and `compensation` before increasing the `brightness` parameter.

The `shutterspeed` parameter is important to get consistent images and can therefore be manually set. In many cases it may be desirable to not get motion blur in the image. In that case it is important to first determine the required shutterspeed, and then adjust the amount of light available, such as for experiments. If that is not possible, then start tweaking the other parameters as explained above. In some cases a very long shutterspeed may be needed (e.g. >1s), which may result in very blurry images but still allows objects to be detected and tracked for example.

## Automatic shutterspeed and whitebalance
By default, PiRecorder automatically sets the shutterspeed and white balance dynamically for and during each recording (`automode = True`). However, to get consistent recordings, it may be preferable to set the shutterspeed and white balance at a fixed value. This can be done both automatically and interactively (explained below) with pirecorder.

To get the optimal shutterspeed and white balance for the current conditions automatically you can use the `autoconfig` function, which will directly update the configuration file. This function will use the framerate provided in the configuration file for calibration, so make sure that is set properly. Then to run autoconfig, simply enter:

```
rec.autoconfig()
```

## Change the camera settings interactively
pirecorder also comes with a very handy interactive tool (`camconfig`) that enables you to set the camera settings dynamically. `camconfig` opens a live video stream and a separate window with a trackbar for each of the camera settings. You can slide your parameters of interest between the possible values and see live how the resulting recording will look like. To run camconfig and store the values automatically in your configuration file, use the function linked to your PiRecorder instance:

```
rec.camconfig()
```

You can exit the stream without saving with the `esc`-key and with saving with the `s`-key.

An important setting is the `automatic` mode. By default this is set to `True` such that it automatically gets the optimal shutterspeed and white balance (blue and red gains), which is visible by the respective trackbars sliding automatically to their optimal values. When you are relatively happy with these values it is a good time to use the non-automatic mode as then you are able to further tweak these values to your wishes.

`camconfig` will use the framerate as provided in the configuration file, but you can also dynamically update the framerate while the video stream is open, which in turn will influence the range of shutterspeeds possible (see above). It is also possible to use camconfig stand alone without a PiRecorder instance. Simply import pirecorder and run the function:

```
import pirecorder
pirecorder.Camconfig()
```

Then when the `s`-key is pressed it will output a dictionary of all values.

## Correct for raspberry-pi specific brightness
In some cases you may want to use multiple raspberry pi's to record the same scene. Due to small differences in the hardware or camera positioning there may be slight differences in the brightness of the recordings of the raspberry pi's. To correct for those you can use the `brighttune` parameter. Each raspberry pi will use the `brightness` parameter as default, so it can be easily set consistently across all raspberry pi's, but then for each specific raspberry pi you can tweak this value from -10 to +10.

---
Camera settings documentation
{: .text-delta .fs-5}
```
Parameters
---------------
rotation : int, default = 0
    Custom rotation specific to the Raspberry Pi, should be either 0 or 180.
gains : tuple, default = (1.0, 2.5)
    Sets the blue and red gains to acquire the desired white balance.
    Expects a tuple of floating values (e.g. "(1.5, 1.85)"). Can be
    automatically set with the autoconfig() function and interactively with the
    camconfig() function using a live video stream.
brightness : int, default = 45
    Sets the brightness level of the camera. Expects an integer value
    between 0 and 100. Higher values result in brighter images.
contrast : int, default = 20
    Sets the contrast for the recording. Expects an integer value between 0
    and 100. Higher values result in images with higher contrast.
saturation : int, default 0
    Sets the saturation level for the recording. Expects an integer value
    between -100 and 100.
iso : int, default = 200
    Sets the camera ISO value. Should be one of the following values:
    [100, 200, 320, 400, 500, 640, 800]. Higher values result in brighter
    images but with higher gain.
sharpness : int, default = 50
    Sets the sharpness of the camera. Expects an integer value between -100
    and 100. Higher values result in sharper images.
compensation : int, default = 0
    Adjusts the camera’s exposure compensation level before recording.
    Expects a value between -25 and 25, with each increment representing
    1/6th of a stop and thereby a brighter image.
shutterspeed : int, detault = 10000
    Sets the shutter speed of the camera in microseconds, i.e. a value of
    10000 would indicate a shutterspeed of 1/100th of a second. A longer
    shutterspeed will result in a brighter image but more motion blur.
    Important to consider is that the framerate of the camera will be
    adjusted based on the shutterspeed. At low shutterspeeds (i.e. above
    ~ 0.2s) the required waiting time between images increases considerably
    due to the raspberry pi hardware. To control for this, automatically a
    standard `imgwait` time should be chosen that is at least 6x the
    shutterspeed. For example, for a shutterspeed of 300000 imgwait should
    be > 1.8s.
brighttune : int, default = 0
    A rpi-specific brightness compensation factor to standardize light
    levels across multiple rpi"s, an integer between -10 and 10.    
```
