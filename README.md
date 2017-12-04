# Clonal molley rpi set-up
Last updated: December 1st 2017<br/>
*Jolle W Jolles*

### Overview

#### Experimental tanks
The experimental set-up consists of 24 square tanks (56 cm x 56 cm x 24.4 cm) set-up at ~ 1 m height from the floor in two long rows of 12, with space between the tanks. A subset of 14 tanks is further divided into four compartments, each of 27.1 x 27.1 cm. A raspberrypi and camera are carefully positioned exactly above the centre of each tank, 52 cm from the tank edge. 

<img src="https://github.com/jolleslab/molly/blob/master/images/rpi-overview.png" width="100%" height="100%"></img>

#### Network
All raspberrypi’s are connected to each other via a local ethernet network and have their own static ip address. Their subnet is set at ```192.168.10```, which means that only computers within that subnet can communicate with the raspberrypi's. 

Each group of four tanks/rpi's has the number 1-6 left-to-right and each rpi in each group of four tanks has 1, 2, 3 or 4 added for left bottom, left top, right bottom, right top (see image above), e.g. tank top right from the second group of four tanks gets ip address ```192.168.10.24```. 

All raspberrypi’s are connected via a network hub that is linked to the broader IGB network and the internet beyond. This makes it also possible to connect to the rpi's from anywhere on the internet, but for which you will need to make use of a VPN server (see below).

#### Storage
The IGB has allocated storage space on their servers and provided the right credentials for us to directly connect to the server from the rpi's.

Each rpi is now set-up in such a way that the the server folder for this specific project is automatically mounted in the location /home/pi/SERVER, i.e. in the folder SERVER in the main directory. The server folder contains associated folders with each rpi to keep the data output separated per device (e.g. SERVER/pi11, SERVER/pi12 etc):

<center><img src="https://github.com/jolleslab/molly/blob/master/images/server-via-terminal.png"  width="742px" height="221px"></img></center>

#### Automated recording
The rpi's are currently set-up in such a way to easily record long sequences of standardized images according to specified timeschedules. The main functionality comes from my github AnimRec repository that is cloned on each rpi. The two main files in this repository that are used for recording are *imgrec.py* and *imgtask.py*. The benefit of using the github repository is that the recording scripts can be very easily updated on all rpi's simultaneously.

The imgrec script is where all settings for the camera are set and that takes the actual images, while the imgtask script enables scheduling the recording tasks. With the imgrec script it is possible to record for many days on end but the scripts are set-up in such a way that they are best used by running one recording session per day.

It is easy to update the script with the parameters one wishes without requiring any coding knowledge, which is explained below. The following parameters can be set: the time delay between subsequent images, the total nr of images to take per session, the total time to record per session, the timing schedule of recording sessions (e.g. once per day at 7am; every week on monday at noon; every 10, 20th and 30th of the month; etc), the camera resolution, shutterspeed, iso, brightness, sharpness, contrast, saturation, and quality. 

Image settings should ideally only be set once and will be optimal for the final recording set-up. This includes the optimal image quality for tracking purposes and storage space in mind. Jolle will take main care of this.

The storage location of the images is currently automatically set based on the rpi. So rpi 62 will record images to folder SERVER/pi62 and rpi 14 to folder SERVER/pi14 without the user needing to provide this. If wished for custom writing locations this could become implemented in future version of the scripts as an additional user setting.

### Working with the recording system
#### Connect to the rpi network
To be able to communicate with the rpi's one either needs to be hardwired in the network or use a VPN. For the former you need to be in the lab, connect an ethernet cable between the network switch and your computer, and make sure you set-up your ethernet connection with a static ip address within the subnet of the rpi's and with a different ip address than any of the rpi's. For example ```192.168.10.5``` or ```192.168.10.17``` . To use VPN you will need to ask the IT department for the right credentials and download their suggested VPN client, likely Tunnelblick. Then to connect to the rpi network you simply click connect in the VPN client and you can communicate with the rpi's as if hardwired in the same network.

#### Connect to the rpi's

When you are on the rpi network there are two ways to control the rpi's. This can be done either by SSH directly via terminal or by using VNC viewer. The former is better to do something quickly using the command line and to control multiple rpi's at once while the latter enables one to see the rpi camera stream.

##### A) Connecting via ssh

To connect to a single rpi simply open up a terminal window, enter ```ssh pi@RPI_IPADDRESS```, replacing RPI_IPADDRESS for the respective ip address (e.g. ```192.168.10.11```), and enter the password, set at ```1gbm0llyp0wer```. When successful you will see a welcome message and then ```pi@piNR:~$``` at the start of each line. You are now inside the rpi.

In a similar way you can connect to all rpi's at once. You will need to download a special ssh script called *csshX* from my dropbox [here](https://www.dropbox.com/s/93fly1bx83onwa9/csshX?dl=1). Now open a terminal window and drag the csshX file into the terminal. Enter a space and type in `pi@192.168.10.[11,12,13,14,21,22,23,24,31,32,33,34,41,42,43,44,51,52,53,54,61,62,63,64]` and press *Enter*. Now you can control all rpi's at once by typing in the red terminal window in the bottom.

<center><img src="https://github.com/jolleslab/molly/blob/master/images/rpi-connected-ssh.png"  width="680px" height="380px"></img></center>

##### B) Connecting via VNC viewer

Download the free VNC viewer software [here](https://www.realvnc.com/en/connect/download/viewer/) and install it. Now open an instance of VNC viewer, type in the ip-address of the respective rpi in the address bar, and press Enter. Now similarly as for ssh enter the right username (pi) and password (1gbm0llyp0wer). When succesfull you will now see the linux destkop from that respective rpi. 

<center><img src="https://github.com/jolleslab/molly/blob/master/images/vncviewer-connected.jpg" width="600px" height="497px"></img></center>

#### See the camera stream
To see the rpi camera stream you will need to connect with VNC viewer. Then open a terminal window on the desktop and type in ```raspistill -t 0 -k -p 100,100,600,600``` and press enter. You will now see what the rpi camera seems live, which is helpful for aligning the camera and tank for example. To exit press ```ctrl+c```.

#### Set-up image recording
For setting-up image recording make first of all sure that you are connected to the rpi(s), either via SSH or VNC viewer, with a terminal window open.

##### A) Image settings
To run one session of image recording type in ```img record```. It is important to make sure that the image record parameters are appropriate for the experiment to be done and storage space available. This is done by Jolle. 

To see what can be changed (currently 13), type in ```img -d record```. To change the settings of the recording script with new parameters, simply add these after a colon after the main command, making sure to have no spaces between subsequent parameters. For example, to set the image saturation to -50 the final code would be ```img record:saturation=-50```. To get the right parameters make sure to also set imgnr to some low value. Now check the recorded image and change the values accordingly until you are happy with the result. These sessions can now be used in this way for single sessions, but to use the image parameters in the recording schedule this needs to be set by Jolle (or modified manually in the file AnimRec/imgrec.py).

#### CHANGE TO WORK WITH --LOCATion etc

In each rpi home folder there is a file called ```roifile.txt```. This file is used for the automated image recording script to get the right roi to crop the image output before storing. This file can be edited directly. Setting the roi is important as it it will enable us to store much smaller images by focusing only on that section of the image that we are interested in. This is done by Jolle. 

When you are happy with the image properties, these should ideally not be touched again and as the scheduling script also enables setting the img nr, delay and time it is not needed anymore to run the ```img record``` command directly.

##### B) Scheduling image recording tasks

The scheduling of image recordings consists of two components: 1) how many images should be taking and at what delay for each recording SESSION, and 2) when exactly recording sessions should be run and until when that should continue. Both of these should be set using the scheduling script by typing in ```schedule plan```.

When running the schedule command and nothing else is added it will plan an automatic schedule of image recording using the standard settings. To see what these standard settings are and what parameters can be set manually, type in ```schedule -d plan```. This will provide an overview of the different parameters, with their default values and a brief explanation.

So (based on the defaults) when you run the imgtask script without entering anything else it will schedule image recording to start at 7AM every day forever (under the schedule name *molly*) where a total of 100 images are taken with 5 seconds delay between them. Both imgtime and imgnr can be provided. The script will select the minimum of those based on the imgdelay. 

To set custom parameters, simply add these after a colon after the main command, making sure to have no spaces between subsequent parameters. An example. Let's say you want to take images with 17.5s delay between them for a total of 6 hours per session. This means imgwait=17.5 and imgtime=6*60. As the script automatically takes the minimum of imgtime and imgnr, also the latter needs to be set to some high value. You want to use the standard schedule and show the task. The code you will need to enter in terminal will therefore be:
```schedule plan:imgwait=17.5,imgnr=999999,imgtime=360,taskshow=True```

The taskcode command is to set the specific schedule of the recording script. This is based on CRON scheduling. It is a nice and simple way to provide any possible schedule, although a bit more difficult to use when wanting very specific schedules. [This](http://www.nncron.ru/help/EN/working/cron-format.htm) is a great place to learn more about this format. To see if your taskcode does what you want you can try it out on [this website](http://cron.schlitt.info).

A scheduling example. Say you additionally want to change the schedule to start the recording script at 22:00 on every day of the week only and continuously throughout the year. The first character in the taskcode is minutes, so that should be `0`. The second character is hour so that should be `22`. The third character is day of the month so that should be `*`. The fourth is month so that should also be `*`. The fifth is day of the week so that should be `1-5`. So the code you will have to add to the command above is: ```,"0 22 * * 1-5```.

A log of all recording is stored in the home folder on each rpi in the file *imglog.txt* with details of the exact time and name of each image.

