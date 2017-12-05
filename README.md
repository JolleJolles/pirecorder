# Clonal molley rpi set-up
Last updated: December 1st 2017, JW Jolles

### 1. Overview
<img src="https://www.dropbox.com/s/le6ddulbbx4i513/rpi-overview.png?dl=1" width="100%" height="100%"></img>

#### 1.1 Experimental tanks
The experimental set-up consists of 24 square white perspex tanks (56 cm x 56 cm x 24.4 cm) set-up at hip height in two long rows of 12, with some space between the tanks. A subset of 14 tanks is further divided into four compartments, each of 27.1 x 27.1 cm. A raspberrypi computer and camera are carefully positioned exactly above the centre of each tank, 52 cm from the tank edge. 

<center><img src="https://www.dropbox.com/s/b1qwkns5ssyq6vn/rpi-set-up-overview.jpg?dl=1" width="500px" height="325px"></img></center>

#### 1.2 Network
All raspberrypi’s are connected to each other via a local ethernet network with subnet ```192.168.10.``` and have their own static ip address, based on the group of four rpi's it is in (.1x - .6x left to right) and its position in that group (.x1, .x2, .x3 or .x4 for left bottom, left top, right bottom, right top). Only computers within the same subnet can communicate with the rpi's. The network hub is connected to the broader IGB network and the internet beyond. This makes it also possible to connect to the rpi's from anywhere on the internet, but for which you will need to make use of a VPN server to get past all the safety restrictions of the institute.   

#### 1.3 Storage
The IGB has allocated storage space on their servers and provided the right credentials to directly connect to the server from the rpi's. Each rpi is now set-up in such a way that the the server folder for this specific project is automatically mounted in the location /home/pi/SERVER, i.e. in the folder SERVER in the main directory. The server folder contains associated folders with each rpi to keep the data output separated per computer (e.g. SERVER/pi11, SERVER/pi12 etc). In total 5TB is currently available. This means that with the current camera settings and planned recording schedule a total of 330k images can be stored.

<center><img src="https://www.dropbox.com/s/9fgofqmcg8c9jp7/server-via-terminal.png?dl=1"  width="742px" height="220px"></img></center>

#### 1.4 Automated recording
The rpi's are set-up in such a way that it is easy to record long sessions of standardized image recordings according to specific time schedules. The main functionality comes from a combination of custom scripts and libraries that are easily updated from GitHub. In short, there is one main file that is used to set all the parameters of the camera and to run individual sessions, and another main file that is used to schedule those sessions (explained in detail below). Image settings should be set before the start of the experiments and finalised with piloting such that they are optimal for the final recording set-up. This is mostly done by Jolle. The storage location of the images is currently automatically set based on the rpi. So rpi 62 will record images to folder SERVER/pi62 and rpi 14 to folder SERVER/pi14 without the user needing to provide this, with further subfolders dividing the images further by date.

### 2. Working with the recording system!
#### 2.1 Connect to the rpi network
To be able to communicate with the rpi's one either needs to be hardwired in the network or use a VPN. For the former you need to be in the lab, connect an ethernet cable between the network switch and your computer, and make sure you set up your ethernet connection with a static ip address within the subnet of the rpi's and with a different ip address than any of the rpi's. For example ```192.168.10.5``` or ```192.168.10.17``` . 

<center><img src="https://www.dropbox.com/s/49vv0owgk541kzt/ethernet-connection.png?dl=1" width="400px" height="212px"></img></center>

To use VPN you will need to ask the IT department for the right credentials and download their suggested VPN client, likely Tunnelblick. Then to connect to the rpi network you simply click connect in the VPN client and you can communicate with the rpi's as if hardwired in the same network.

#### 2.2 Connect to the rpi's
When you are on the rpi network there are two ways to control the rpi's. This can be done either by SSH directly via terminal or by using VNC viewer. The former is better to do something quickly using the command line and to control multiple rpi's at once while the latter enables one to see the rpi camera stream.

##### 2.2.1 Connect to single rpi via ssh
To connect to a single rpi simply open up a terminal window, enter ```ssh pi@RPI_IPADDRESS```, replacing RPI_IPADDRESS for the respective ip address (e.g. ```192.168.10.11```), and enter the password, set at ```1gbm0llyp0wer```. When successful you will see a welcome message and then ```pi@piNR:~$``` at the start of each line. You are now inside the rpi:

<center><br/><img src="https://www.dropbox.com/s/8b9zqbpuxnzi2hk/rpi-connected-ssh.png?dl=1" width="537px" height="160px"></img></center>

##### 2.2.2 Connect to multiple rpi via csshX
In a similar way as connecting to one rpi you can connect to all rpi's at once. You will need to download a special ssh script called *csshX* (get it from Jolle's dropbox [here](https://www.dropbox.com/s/93fly1bx83onwa9/csshX?dl=1)). Now open a terminal window and drag the csshX file into the terminal. Enter a space and type in `pi@192.168.10.[11,12,13,14,21,22,23,24,31,32,33,34,41,42,43,44,51,52,53,54,61,62,63,64]` and press *Enter*. Now you can control all rpi's at once by typing in the red terminal window in the bottom.

<center><img src="https://www.dropbox.com/s/ol0cwn0w422qygh/csshx_windows.jpg?dl=1"></img></center>

##### 2.2.3 Connect via VNC viewer

Download the free VNC viewer software [here](https://www.realvnc.com/en/connect/download/viewer/) and install it. Now open an instance of VNC viewer, type in the ip-address of the respective rpi in the address bar, and press Enter. Now similarly as for ssh, enter the right username (pi) and password (1gbm0llyp0wer). When succesfull you will see the linux desktop from that respective rpi. 

<center><img src="https://www.dropbox.com/s/gb7i4pbr0xzi6um/vncviewer-connected.jpg?dl=1" width="600px" height="497px"></img></center>

#### 2.3 See the camera stream
To see the rpi camera stream you will need to connect with VNC viewer (or hardwire a screen into the rpi). Then open a terminal window on the desktop and type in ```raspistill -t 0 -k -p 100,100,600,600``` and press enter. You will now see what the rpi camera sees live at a couple frames per second. This can be especially helpful for aligning the camera and tank. To exit simply press ```ctrl+c``` in terminal.

#### 2.4 Set-up image recording
For setting-up image recording make first of all sure that you are connected to the rpi(s), either via SSH or VNC viewer, and have a terminal window open. Image recording consists of setting 1) the right image settings, 2) the right recording settings per session, and 3) the right schedule of recording multiple sessions.


##### 2.4.1 Image and recording settings
The following parameters can be set for the images that will be recorded: the resolution, shutterspeed, iso, brightness, sharpness, contrast, saturation, quality, region of interest, and storage location. These parameters should be carefully selected and tested and then ideally kept constant throughout the experimental period. Jolle has done this for the current experimental set-up already.

In addition to the image settings, for each recording session you can set a) the time delay between subsequent images, b) the total nr of images to take per session, and c) the total time to record for a session. The total nr of images that will be recorded per session will be (b) or, when less, the nr of images to record within the recording period divided by the time delay.

To run an image recording session, in terminal simply type in ```img record```. This will record a session with the standard parameter values. To see what parameters can be set with a brief explanation and the default value used type in ```img -d record```.

To change the settings of the recording script with new parameters, simply add these after a colon after the main command, making sure to have no spaces between subsequent parameters. For example, to set the image saturation to -50 the final code would be ```img record:saturation=-50```. 

Make sure to also set imgnr to some low value when trying to determine the right image settings, checking the images and adapting the parameter values until happy with the result. Write down the parameter values for future use. If wanting to make these values to be the new defaults contact Jolle (or manually edit the imgrec.py file).

By default (when location="pi"), the location where the images are stored is set to the folder on the server that corresponds to the rpi name. For example ```/home/pi/SERVER/pi41```. If a different *location* is provided, a folder with name corresponding to location will be created inside the home directory.

##### 2.4.2 Image roi
The rpi camera films a region that is much larger than the actual tank. To save storage space and facilitate in tracking a specific roi needs to be provided for each rpi. The scripts are set-up in such a way that they search for a ```roifile.txt``` file in the home directory. This file should contain on one line as "(x, y, w, h)" (with parentheses), with the four points ranging between 0.0 and 1.0. These values can be determined by running a raspistill command with VNC viewer and editing the *-roi* parameter. For example with the code: ```raspistill -w 500 -h 500 -k -p 50,50,500,500 -roi 0.31,0.31,0.45,0.45```. This will be done by Jolle.

##### 2.4.3 Recording scheduling
To schedule image recording sessions, type in ```schedule plan```. This command enables again the user to set how many images should be taking and at what delay for each recording session, but in addition  when exactly recording sessions should be run and until when that should continue, e.g. once per day at 7am; every week on monday at noon; every 10, 20th and 30th of the month; etc. When running the script it will provide some brief output of the scheduled tasks and when the next session will start based on the planning:

<center><img src="https://www.dropbox.com/s/b0lzdvf3euqclni/run-scheduler-example.png?dl=1" width="417px" height="101px"></img></center>

When running the schedule command and nothing else is added it will plan an automatic schedule of image recording using the standard settings. Similarly as for individual sessions, to see what these standard settings are and what parameters can be set manually, type in ```schedule -d plan```. This will provide an overview of the different parameters with explanation and their default value. So when running the scheduler with defaults (```schedule plan```) it will plan a schedule to start an image recording session to start at 7AM every day forever, with the schedule name *molly*, where a total of 100 images are taken with 5 seconds delay between them. To set custom parameters, simply add these after a colon after the main command, making sure to have no spaces between subsequent parameters. 

An example. Let's say you want to take images with 17.5s delay between them for a total of 6 hours per session and use the standard schedule command. This means imgwait=17.5 and imgtime=6*60. As the script automatically takes the minimum of imgtime and imgnr, also the latter needs to be set to some high value. So the code you will need to enter in terminal will be:
```schedule plan:imgwait=17.5,imgnr=999999,imgtime=360,taskshow=True```

To change the recording schedule you need to set the *taskcode* parameter. This parameter is based on CRON scheduling, a nice and simple way to provide any possible timing schedule, although a bit more difficult to use when wanting a very specific schedule. A great place to learn more about this format can be found on [this website](http://www.nncron.ru/help/EN/working/cron-format.htm). When wanting to try your taskcode before setting it up, try it out [here](http://cron.schlitt.info).

<center><img src="https://www.dropbox.com/s/kgpgumwmjf1841s/taskcode-explanation.png?dl=1" width="361px" height="134px"></img></center>

A scheduling example. Say you want to change the schedule to start the recording script at 22:00, every day of the week except the weekend, and let it run continuously throughout the year. The first character in the taskcode is minutes, so that should be `0`. The second character is hour so that should be `22`. The third character is day of the month so that should be `*`. The fourth is month so that should also be `*`. The fifth is day of the week so that should be `1-5`. So the code you will have to add to the taskcode parameter is: ```"0 22 * * 1-5```.

##### 2.4.4 Recording logs
For all recording schedules a detailed logfile is created with details of the exact time and name of each image. These logfiles are stored on the server in a folder called *imglogs*. Separate logs are created for each rpi and each day of recording.


