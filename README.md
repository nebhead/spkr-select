# spkr-select

## Raspberry Pi based Speaker Selector using Python and Flask/Gunicorn/nginx (and optionally LIRC)
##### Also uses Bootstrap (http://getbootstrap.com/) w/jQuery and Popper support

***Note:*** *This project is continuously evolving, and thus this readme will likely be improved over time, as I find the inspiration to make adjustments.  That being said, I'm sure there will be many errors that I have overlooked or sections that I haven't updated.*

This project was inspired by David Liu and his excellent speaker selector project (http://iceboundflame.com/projects/multi-room-audio-control-with-rpi).  I encourage you to check it out and get a rough idea of how this all works.

This version of the speaker selector script is highly tuned to my particular setup.  I have only three sets of speakers, using the Niles SS4 speaker switch.  I've used relays that I purchased on Amazon.com (https://amzn.com/B00KTELP3I), which are great for this particular project.  If you want a fourth set of speakers to be added, you will need to add a couple relays to support this.    

Since my personal setup will use the living room speakers only, by default, 99% of the time I've set this up as "normally closed" on the relay.  The other three sets of relays can be normally open since they're more rarely used.  This will hopefully save the relays from getting worn out too quickly.

I've added an IR receiver (https://amzn.com/B005T960JC) so that I can also use my universal remote to control the speaker output.  This is likely optional, but a really convenient addition to the project.  The code uses LIRC and Python LIRC to accept input from the IR receiver.

Initially this project used Flask's native WSGI services without Gunicorn or nginx as a proxy.  However, I noticed that after some time, the app would become unresponsive.  After a little research, it appears that Flask's built in web server is for testing purposes only and shouldn't really be used in production.  With that said, I'm using Gunicorn and nginx to proxy web requests.  This is simple enough to configure and setup, however I had to redesign the application without the threading libraries, due to conflicts with Gunicorn.  Instead, I am using two processes running concurrently (control.py and app.py).  Control handles all of the RasPi GPIO interfaces, while App handles the web routes.  They communicate through a .dat file (using pickle to simplify the format).  

#### UPDATE: March 2018

With this update I've done a complete overhaul of the web UI with Bootstrap 4.  I feel that the aesthetics are even better than they were before. I've changed from using the TiTa-Toggle switches to just plain buttons that change their appearance (solid when on, outline white when off) dynamically when set.  

I've also updated the admin screen to include some system information, as well as improve the shutdown & restart buttons.  

I've also changed out the existing Raspberry Pi 2, for a Raspberry Pi Zero W instead.  My hope is that it will run a bit cooler than the RasPi2.  And frankly, the RasPi2 is pretty bulky.  I have added a USB Ethernet dongle to this project, however the wireless does appear to work inside the aluminum box.  

#### UPDATE: March 2019

More goodness added to the application including:

* Applications are now managed by supervisord instead of being launched with a CRON script
* Added ability to control application via an HTTPS API (using self-signed certificate and API key) which opens up the ability to use Google Assistant and/or IFTTT to control the speaker states
* Shameless plug for donations (see the admin > credits)

#### UPDATE: April 2019

* Updated the README.md to include more information on the hardware setup.  Hopefully this will demystify the hardware build so that people building this project at home will be able to recreate it.  
* Updated control.py to make the LIRC libraries optional (disable/enable flag).  I believe that others may have experienced issues with this project when lirc was not installed.  

## Screenshots

Here is a screenshot of the dashboard:

![Dashboard](documents/photos/Screenshot_Dashboard.jpg)

Here is a screenshot of the admin screen:

![Admin & Settings](documents/photos/Screenshot_Admin.jpg)

## Hardware Configuration

### The Parts List
The parts list and setup of this was heavily borrowed from the following guide here:
(http://iceboundflame.com/projects/multi-room-audio-control-with-rpi)

* **Raspberry Pi Zero W** - Technically any Raspberry Pi will do fine, but for this application a Raspberry Pi Zero W works really well and is the right price.
* **8-Channel Relay** - I use two relays per set of speakers (left and right channels), and currently don't use the fourth set of speakers. Thus I can use six of the relays for the three sets of speakers and two relays for the speaker protection on the output. [Amazon Link](https://www.amazon.com/dp/B0057OC5WK/ref=cm_sw_em_r_mt_dp_U_TktNCbPC5MVRB)
* **IR Reciever** - In this project, I've used the TSOP38238 because of the availability and the fact that there was good documentation / other pi projects that I was able to reference online. [Amazon Link](https://www.amazon.com/dp/B005T960JC/ref=cm_sw_em_r_mt_dp_U_Z.kTCbZZ3RN6F ) (Note that you may find cheaper options, but this is the one I ended up using)
* **Resistors** - (5x) I've sized 10k ohm resistors for my projects due to the brightness of my LEDS.  You may want to do some prototyping before soldering into your project.  Given this sits in my home theater cabinet, I wanted the LEDs to be dimmer.  
* **LEDs** - (5x) Again, these are personal preference, or whatever you might have laying around the house.  I've used clear white LEDs for the speaker selections, and a clear blue LED for the protection indicator.  My LED's are very bright, so as mentioned above, I have decided to go with a beefier resistor.   
* **Micro SD Card** - Greater than 4GB is probably good.  
* **MicroUSB Power Adapter** - At least 1 amp current recommended.  Make sure you have a place to plug this in near your garage door opener
* **Niles Speaker Selector** - The heart of this project is the Niles SS-4 Speaker Selector.  Still available on Amazon, but you may source this for cheaper elsewhere (like ebay).  [Amazon Link](https://www.amazon.com/dp/B00020H2MM/ref=cm_sw_em_r_mt_dp_U_illTCbDXW2641)

### Hardware Setup

**UPDATE 04/2019:** Now with 100% more schematics.

Niles SS-4 speaker switch opened up, and we see that the design is extremely simple:

![HW001](documents/photos/HW_001_Outside_View.jpg)

This is an overhead view of the board, and in particular the big resistors that provide short protection when more than two sets of speakers are enabled.  

![HW002](documents/photos/HW_002_Overhead.jpg)

Next up, the schematic for the relays.  I've tried closely approximate the switches inside the Niles box visually (hopefully you can forgive my artistry). You will note that the relays are wired in pairs, since the speakers have a left and right channel.  For the first pair, we've wired them up as normally closed, since these will be the default activated speakers.  Having these normally closed, will help prevent an early relay failure.  The rest of the relays are wired as normally open since they will be normally inactive in my case.  Again, you may choose to modify your wiring based on your scenario.  

The IN pins on the relay module will need to be paired as well, to cut down on the amount of GPIOs required.  What I did (and not pictured here), is flip the relay module over, and solder the IN pairs together (IN1&2, IN3&4, IN5&6, IN7&8) using a big blob of solder between the pairs.  Based on what I know of the module design, this should work fine with the raspberry pi zero sinking/driving two pins at once.  

Something else to note is that I'm using the switch four (4) to bus the negative/ground sides of the speakers together.  You can conceivably use any of the switches to connect to the negative side.  The Niles board connects all of the negative path together as well.   

![HW008](documents/photos/HW_008_Relay_Schematic.jpg)

This is a picture layout of the wiring for the relays before soldering to the switches.  From left to right.  The first and second relays are connected in a normally closed configuration, with the wire to the left most position looking at this picture.  The common position on all left speaker and right speaker relays are basically all bussed together.  Meaning that all left speakers would have a common ground and all right speakers have a common ground.  Shown here the black and white wires connecting the respective grounds.  The other relays in this picture are connected up with the normally open configuration because they are typically not enabled.  

Also note that you should probably use a thicker gauge wire for the relay wiring, given that you will be pumping some power through these.  

![HW007](documents/photos/HW_007_Relay_Wiring.jpg)

This is a view of the solder points on switch number four which is *only* the negative sides (for both left and right) since these are shared for ALL of the switches.  

![HW003](documents/photos/HW_003_Solder_Points_Protection_Switch.jpg)

This is the schematic of the front panel LEDs and the IR receiver.  Pretty standard LED / Resistor pair combination here.  I've gone with a larger resistor size to help dim the brightness of my LEDs.  Your mileage may vary though, and you may want to consider testing your resistor sizing before you solder anything into your system.  

Also note that on my design, I used 5V to power the IR receiver.  You should be able to also use the 3.3V with this device, as it should work with between 2.5V and 5.5V.  

![HW009](documents/photos/HW_009_LED_IR_Schematic.jpg)

A view of the front panel board with indicator LEDs and the front panel IR sensor, both hot glued to the front of the unit.  Note that I just used a regular drill bit and free-hand drill to drill through the front panel for the LEDs and the IR.  I managed to get some precision, but a drill press with careful measuring is recommended.  

![HW004](documents/photos/HW_004_Front_Panel_LEDs_IR.jpg)

What a rat's nest... from the left, you see the 8 relay board which provides the actual speaker switching.  I've added a bit of shielding to the large resistors int he center of the board.  ON the right you can see the Raspberry Pi Zero W, the brains of the operation.  Then on the far right, I have the USB Ethernet adapter which is completely optional.  

![HW005](documents/photos/HW_005_Rats_Nest_Wiring.jpg)

The finished product, all buttoned up and working in my home theater.  Tis a thing of beauty if I do say so myself.  

![HW006](documents/photos/HW_006_Finished_Product.jpg)

### Raspberry Pi GPIO Mapping

__Front Panel LED's (defined in control.py):__
* **GPIO17 LED 01** - Speakers 1, LED indicator (WHITE)
* **GPIO18 LED 02** - Speakers 2, LED indicator (WHITE)
* **GPIO19 LED 03** - Speakers 3, LED indicator (WHITE)
* **GPIO20 LED 04** - Not used / connected currently
* **GPIO21 LED 05** - Protection, LED indicator (BLUE)

__Front Panel IR Receiver (defined in /boot/config.txt, /etc/modules):__
* **GPIO02 IR Input** - Configured in LIRC setup

__Relay Control (defined in control.py):__
* **GPIO22 Relays (1 & 2)** - Speakers 1 (L/R), IN1&2 on the relay module
* **GPIO23 Relays (3 & 4)** - Speakers 2 (L/R), IN3&4 on the relay module
* **GPIO24 Relays (5 & 6)** - Speakers 3 (L/R), IN5&6 on the relay module
* **GPIO25 Relays (7 & 8)** - Protection (L/R), IN7&8 on the relay module


## Software Installation

### Raspberry Pi Zero Setup Headless (*from raspberrypi.org*)

Once you've burned/etched the Raspbian Stretch Lite image onto the microSD card, connect the card to your working PC and you'll see the card being mounted as "boot". Inside this "boot" directory, you need to make 2 new files. You can create the files using Atom code editor.

+ Step 1: Create an empty file. You can use Notepad on Windows or TextEdit to do so by creating a new file. Just name the file **ssh**. Save that empty file and dump it into boot partition (microSD).

+ Step 2: Create another file name wpa_supplicant.conf . This time you need to write a few lines of text for this file. For this file, you need to use the FULL VERSION of wpa_supplicant.conf. Meaning you must have the 3 lines of data namely country, ctrl_interface and update_config

```
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="your_real_wifi_ssid"
    scan_ssid=1
    psk="your_real_password"
    key_mgmt=WPA-PSK
}
```

#### Run RasPi-Config
```
ssh pi@192.168.1.xxx

sudo raspi-config
```
+ Set locales
+ Set timezone
+ Replace Hostname with a unique hostname ('i.e. spkr-select')

#### Install Git, Python PIP, Flask, Gunicorn, nginx, and supervisord
```
sudo apt update
sudo apt upgrade
sudo apt install python-pip nginx git gunicorn supervisor -y
sudo pip install flask
sudo pip install pickle
git clone https://github.com/nebhead/spkr-select
```

### Setup nginx to proxy to gunicorn

```
# Move into install directory
cd ~/spkr-select

# Delete default configuration
sudo rm /etc/nginx/sites-enabled/default

# Copy configuration file to nginx
sudo cp spkr-select.nginx /etc/nginx/sites-available/spkr-select

# Create link in sites-enabled
sudo ln -s /etc/nginx/sites-available/spkr-select /etc/nginx/sites-enabled

# Create certificates for SSL support
cd ~/spkr-select/certs
sudo .\generate.sh

# Restart nginx
sudo service nginx restart
```

### Setup Supervisor to Start Apps on Boot / Restart on Failures

```
# Move into garage-zero install directory
cd ~/spkr-select/supervisor

# Copy configuration files (control.conf, webapp.conf) to supervisor config directory
# NOTE: If you used a different directory for garage-zero then make sure you edit the *.conf files appropriately
sudo cp *.conf /etc/supervisor/conf.d/

# If supervisor isn't already running, startup Supervisor
sudo service supervisor start

# If supervisor is running already, just reload the config files
sudo supervisorctl reread
sudo supervisorctl update

# Or just reboot and supervisord should kick everything off
sudo reboot
```
Optionally, you can use supervisor's built in HTTP server to monitor the scripts.

Inside of /etc/supervisor/supervisord.conf, add this:

```
[inet_http_server]
port = 9001
username = user
password = pass
```
If we access our server in a web browser at port 9001, we'll see the web interface that shows the status of the two scripts (WebApp and Control).  This gives you a quick and easy way to monitor whether any of the scripts has stopped functioning.  

### LIRC Install and Configuration

Some configuration may be required for your IR remote control.  I chose an existing remote control schema that I could use with my Logitech Harmony remote.  If you would like to use the same configuration with your programmable remote (such as the Logitech Harmony), use the below steps to setup and install lirc, and the lirc python module.  I'm emulating the buttons on the [RF-Link AVS-411](https://www.amazon.com/RF-Link-AVS-41I-Selector-Terminals/dp/B000GAMTAS/) since it's something that is supported by the Harmony remote and it has a similar functionality to what I'm looking for.  

```
sudo apt-get install lirc python-lirc -y
echo "lirc_dev" >> /etc/modules
echo "lirc_rpi gpio_in_pin=02" >> /etc/modules
echo "dtoverlay=lirc-rpi,gpio_in_pin=02" >> /boot/config.txt  
```
Update the following lines in /etc/lirc/lirc_options.conf:
```
    driver    = default
    device    = /dev/lirc0
```
Copy LIRC configuration files to /etc/lirc (make sure to include these in the install directory)
```
sudo cp hardware.conf /etc/lirc/hardware.conf
sudo cp lircd.conf /etc/lirc/lircd.conf
sudo cp lircrc.txt /etc/lirc/.lircrc
sudo cp lircrc.txt .lircrc
sudo /etc/init.d/lirc stop
sudo /etc/init.d/lirc start
```

Finally, enable LIRC in the **control.py** file by changing the below line:

```
LIRC_Enabled = True # Set to True to enable Lirc / Remote Control Functions and False to disable
```

#### Use your own Remote Control

Conceivably you can also use your own custom remote control by generating your own lircd.conf file.  For more information about this setup, you can follow the same guide that I followed here: http://alexba.in/blog/2013/01/06/setting-up-lirc-on-the-raspberrypi/

To use your remote with this project, ensure that you have the following key names defined in **lircd.conf**. For example:
```
begin codes
    KEY_1                    0xEA15
    KEY_2                    0x1AE5
    KEY_3                    0x9A65
    KEY_4                    0x18E7
    KEY_POWER                0x807F
end codes
```

## Using Speaker Select
If you've configured the supervisord correctly, the application scripts should run upon a reboot.  Once the system is up and running, you should be able to access the WebUI via a browser on your smart phone, tablet or PC device.  

Simply navigate to the IP address of your device for example (you can usually find the IP address of your device from looking at your router's configuration/status pages). My router typically assigns IPs with prefixes of 192.168.1.XXX.  I'll use examples on my home network here, so you'll see URLs like: http://192.168.1.42  Yours may look different depending on your routers firmware/manufacturer (i.e. 10.10.0.XXX, etc.)

**Note:** It's highly recommended to set a static IP for your Pi in your router's configuration.  This will vary from manufacturer to manufacturer and is not covered in this guide.  A static IP ensures that you will be able to access your device reliably, without having to check your router for a new IP every so often.   

The interface / webui is broken out into two main pages. The first is the dashboard view where you can check the current status of the speaker selections. Active speakers are highlighted in teal blue.  There are also buttons to select 'All On' which will turn on all speakers, and a button for 'Default', which defaults to the 'Living Room' speakers only.

![Dashboard](documents/photos/Screenshot_Dashboard.jpg)

Pressing the hamburger icon in the upper right of the interface, allows you to also access to the administration screen. This interface allows you to generate an API key for external control via the API, and an API enable selection.  

![Admin & Settings](documents/photos/Screenshot_API.jpg)

Scrolling down further gives you the option to reboot the system or shutdown the system.  Below these controls, you'll see more information about the system hardware, and the uptime.  

![Admin & Settings](documents/photos/Screenshot_Admin.jpg)

### Adding Speaker Select to your Homescreen using Chrome on your Android Phone

If you are an Android person, you are likely to be using Chrome on your phone and can not only setup a link to the web-app on your homescreen, but it also makes the interface look like a native application.  Pretty cool right?  Well here's how you set this up, it's very simple.  

First, navigate to the instance of the application in your Chrome browser on your phone.  Remember, it's as easy as going to the IP address that was assigned to you device.  Then, from the Chrome drop-down menu in the upper right of the screen, select "Add to Home screen".  

![Add to Home screen in Chrome](documents/photos/Screenshot_Chrome01.jpg)

Then, when the new dialog box pops up, you will have the opportunity to rename the application, or keep the default.

![Rename the application](documents/photos/Screenshot_Chrome02.jpg)

And there you have it, you've not only created a quick link to your web-app, but you've also created a pseudo application at the same time.

### Set Up Self Signed Cert for External Access (Google Assistant or Alexa and IFTTT Integration)

*Credit to this article for providing details on setting up self signed certificates in nginx. (https://www.humankode.com/ssl/create-a-selfsigned-certificate-for-nginx-in-5-minutes)*

Optionally, you may want to be able to control the speaker selection via Google Assistant or via the IFTTT WebHooks.  I have setup an API interface to allow HTTPS calls to control the speaker settings.  The nginx reverse proxy will allow HTTPS (port 443) calls to be sent to the /extapi application route only.  To avoid having to obtain a certificate from an certificate authority (and potentially have to purchase a domain), I'm providing instructions here how to self-sign a certificate that can be used in conjunction with the nginx webserver. Because the self-signed certificate is only good enough to encrypt traffic between IFTTT and the application, and not to confirm the correct identity of the requester, a shared API key secret must be provided by the service to perform any actions.  

In order to properly use this, you must provide a certificate for nginx to use (see the nginx setup above, where this should be taken care of by default) so that a secure connection can be created between the client and server.  Additionally, an API key should be generated and stored by going to the admin page of the application, and enabling the API interface.  

Additionally, the router must be configured to redirect from an external port (preferably a random port number) to the IP of your speaker-select raspberry pi, and port 443.  This setup will vary from router to router, but this is usually in NAT configuration or Port Forwarding.  

Also, since most of us are on residential internet service, and have IP addresses that are assigned dynamically to our modems, you may want to setup a Dynamic DNS service which assign a simple URL to forward web requests to your IP, and update the IP when it changes.  I won't cover how this works in this guide, however I would recommend that you do some web searches for dynamic DNS.  I would also recommend [DuckDNS](https://duckdns.org) who provide a completely free service for dynamic IP addresses.  It's more bare-bones than something like DynDNS, but free is a pretty good price.  

Once this is setup, you'll want to configure an applet in IFTTT call your API, with your API key and the actions you want to take.  Ensure your IFTTT call is using the HTTPS protocol to protect your API key in transit.  The application should not respond to non-SSL based requests and should only work properly with the correct API key.  No other interfaces are accessible via this API.  

Your API Key can be enabled in the Admin settings page.  You can also regenerate a new key if you'd like by clicking the "Generate New API Key" button.  

![API01](documents/photos/Screenshot_API.jpg)

#### Setting up IFTTT to work with Speaker Select External Access

Go to https://IFTTT.com and add a new applet.

Select Google Assistant and select "Say a simple phrase and trigger an action"

![IFTTT01](documents/photos/Screenshot_IFTTT01.JPG)

You will want to use the phrase that you'd like to trigger an action like "Turn on all the speakers." or "Hey Google, Turn off the Kitchen Speakers".

For the THEN action, select WebHooks and fill in as below:

![IFTTT02](documents/photos/Screenshot_IFTTT02.JPG)

Use the URL that you registered on your dynamic DNS service (for example DuckDNS mentioned above).  Use the port and your API key as generated by the application in the admin screen.  

* **URL:** If you are using a dynamic DNS service or if you are using a doman that you have already registered, you can simply use this to point to your instance.  Example: https://yoursite.duckdns.org:34534/extapi/AbCdEfGHiJkLMnOPqrSTuVwXyZ012345  Note that the HTTPS portion of the URL is very important - since regular unsecure HTTP calls will be rejected by this app.   

* **Method:** POST

* **Content Type:** application/x-www-form-urlencoded

* **Body:** This can be any combination of speaker settings either on or off, separated by an ampersand '&'.  For example: spkrs_01=on&spkrs_02=on&spkrs_03=off which would turn Speakers 1 & 2 on and Speakers 3 off.  


#### Additional Notes on Accessing the Application from Outside your Local Network

Please take the utmost care in considering options for exposing this application outside of your home network. Given that this application has very limited security built-in, anyone that is able to gain access to it directly or indirectly, may be able to control your hardware which could result in damage to your property or even potentially physical harm to someone nearby.  

If you want to have access to this application outside of your home network, and I haven't already convinced you not to do this, then I would recommend setting up a VPN for your local network.  This would allow you to tunnel to your home network and access all of your local equipment with some level of security.  A good, low cost, and dead simple VPN project I would recommend is [PiVPN](http://www.pivpn.io/).   
