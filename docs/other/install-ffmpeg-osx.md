---
layout: page
title: Install ffmpeg on OSX
parent: Other guides
nav_order: 12
---

# Installing ffmpeg on Mac OS X
FFmpeg is a great program that you can run from the command line to help convert more or less any media format. This short guide will help you install ffmpeg on Mac.

The easiest way to install ffmpeg is to use [HomeBrew](https://brew.sh) a package manager for Mac. If you don’t have homebrew installed on your mac already, run the following command using terminal:

```
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

Once you have Homebrew installed, you can now simply install ffmpeg from terminal with the following command:

```
brew install ffmpeg
```

To install ffmpeg with specifical modules, instead of running the above command run below command or remove those modules you do not need:

```
brew install ffmpeg --with-chromaprint --with-fdk-aac --with-fontconfig --with-freetype --with-frei0r --with-game-music-emu --with-libass --with-libbluray --with-libbs2b --with-libcaca --with-libgsm --with-libmodplug --with-librsvg --with-libsoxr --with-libssh --with-libvidstab --with-libvorbis --with-libvpx --with-opencore-amr --with-openh264 --with-openjpeg --with-openssl --with-opus --with-rtmpdump --with-rubberband --with-sdl2 --with-snappy --with-speex --with-tesseract --with-theora --with-tools --with-two-lame --with-wavpack --with-webp --with-x265 --with-xz --with-zeromq --with-zim
```
