# Clonal molley rpi set-up
Last updated: 27 November 2017<br/>
*Jolle W Jolles*

### Overview

#### Experimental tanks
The set-up consists of 24 square tanks (56 x 56 x 24.4 cm) set-up at ~ 1 m height in two long rows of 12 with some space between them. A subset of 12 tanks is further divided into four compartments, each of 27.1 x 27.1 cm. A raspberrypi and camera are carefully positioned exactly above the centre of each tank, 52 cm from the tank edge. 

<img src="https://github.com/jolleslab/molly/blob/master/images/rpi-overview.png" width="100%" height="100%"></img>

#### Network
All raspberrypi’s are connected via ethernet cable and have their own static ip address, all on the same subnet ```192.168.10``` . Each group of four tanks has the number 1-6 left-to-right and each rpi in each group of four tanks has 1, 2, 3 or 4 added for left bottom, left top, right bottom, right top (see image above), e.g. tank top right from the second group of four tanks gets ip address ```192.168.10.24```. 

All raspberrypi’s are connected via a network hub that is linked to the broader IGB network and the internet beyond. This makes it possible to connect to the raspberrypi’s from anywhere on the internet. However, to connect to the rpi's one either needs to be within the same subnet or use a VPN.

#### Storage
The IGB has allocated storage space on their servers and provided the right credentials for us to directly connect to the server from the rpi's.

Each rpi is now set-up in such a way that the our server folder is automatically mounted in the folder SERVER. This root folder on the server contains the key recording script and a separate folder for each rpi (e.g. pi11, pi12 etc):

<center><img src="https://github.com/jolleslab/molly/blob/master/images/server-via-terminal.png"  width="742px" height="221px"></img></center>

#### Automated recording
In short, each rpi will take an image every 5 seconds during the light period of each day (07:00 - 19:00), 7 days a week, from a predefined starting date until a predefined ending date. 

The masters image recording script *imgrec.py* is stored in the root folder of the server and can thereby be easily worked with, rather than having separate copies on each rpi. This script will take images with predefined settings to get optimal images. This includes only storing the tank area within the image, taking images in black and white, using the right exp


### Conneting to the rpi's
To be able to connect to the rpi's when not on the same network one needs a VPN and get the right credentials from the IT department at the IGB. When connected to the same network (either directly or via VPN) the rpi's can be controlled A) directly via terminal and SSH or B) by VNC viewer.

##### A) Connecting via ssh

Open a new terminal window and now enter ```ssh pi@RPI_IPADDRESS``` replacing RPI_IPADDRESS for the respective ip address (e.g. ```192.168.10.11```). Next you are asked for the password. This is set at ```1gbm0llyp0wer```. **Keep this password safe!** An easier way to connect to multiple rpi's at once is to use *csshX*. To enable this:

- Download the file from [here](https://www.dropbox.com/s/93fly1bx83onwa9/csshX?dl=1) to your computer.
- Open a terminal window and drag the csshX file into the terminal.
- After a space enter `pi@192.168.10.[11,12,13,14,21,22,23,24,31,32,33,34,41,42,43,44,51,52,53,54,61,62,63,64]` and press *Enter*.
- In the bottom red window type in `clear`
- Everything you type in the red window will appear in the terminal window for each rpi.

<center><img src="https://github.com/jolleslab/molly/blob/master/images/rpi-connected-ssh.png"  width="680px" height="380px"></img></center>

##### B) Connecting via vnc viewer

Download the free software [here](https://www.realvnc.com/en/connect/download/viewer/) and install it. Now open a new instance of VNC viewer and type in the ip-address of the respective rpi in the address bar and press Enter. Now similarly as for ssh enter the right username (pi) and password (1gbm0llyp0wer). When succesfull you will now see the linux destkop from that respective rpi. This is particularly helpful to live stream the camera (explained below). 

<center><img src="https://github.com/jolleslab/molly/blob/master/images/vncviewer-connected.jpg" width="600px" height="497px"></img></center>

