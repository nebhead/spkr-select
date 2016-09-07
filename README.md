# spkr-select

## Raspberry Pi based Speaker Selector using Python and Flask/Gunicorn/nginx (and optionally LIRC)
##### Also uses Bootstrap (http://getbootstrap.com/) and Ti-Ta Toggle (http://kleinejan.github.io/titatoggle/)

This project was inspired by David Liu and his excellent speaker selector project (http://iceboundflame.com/projects/multi-room-audio-control-with-rpi).  I encourage you to check it out and get a rough idea of how this all works.

This version of the speaker selector script is highly tuned to my particular setup.  I have only three sets of speakers, using the Niles SS4 speaker switch.  I've used relays that I purchased on Amazon.com (https://amzn.com/B00KTELP3I), which are great for this particular project.  If you want a fourth set of speakers to be added, you will need to add a couple relays to support this.    

Since my personal setup will use the living room speakers only, by default, 99% of the time I've set this up as "normally closed" on the relay.  The other three sets of relays can be normally open since they're more rarely used.  This will hopefully save the relays from getting worn out too quickly.

I've added an IR receiver (https://amzn.com/B005T960JC) so that I can also use my universal remote to control the speaker output.  This is likely optional, but a really convenient addition to the project.  The code uses LIRC and Python LIRC to accept input from the IR receiver.

Initially this project used Flask's native WSGI services without Gunicorn or nginx as a proxy.  However, I noticed that after some time, the app would become unresponsive.  After a little research, it appears that Flask's built in web server is for testing purposes only and shouldn't really be used in production.  With that said, I'm using Gunicorn and nginx to proxy web resquests.  This is simple enough to configure and setup, however I had to redesign the application without the threading libraries, due to conflicts with Gunicorn.  Instead, I am using two processes running concurrently (control.py and app.py).  Control handles all of the RasPi GPIO interfaces, while App handles the web routes.  They communicate through a .dat file (using pickle to simplify the format).  

## Hardware Configuration
TBD

### Raspberry Pi GPIO Mapping
GPIO17 LED 01 - Speakers 1
GPIO18 LED 02 - Speakers 2
GPIO19 LED 03 - Speakers 3
GPIO20 LED 04 - Not used / connected currently
GPIO21 LED 05 - Protection

GPIO22 Relays (1 & 2) - Speakers 1 (L/R)
GPIO23 Relays (3 & 4) - Speakers 2 (L/R)
GPIO24 Relays (5 & 6) - Speakers 3 (L/R)
GPIO25 Relays (7 & 8) - Protection (L/R)

GPIO02 IR Input (configured in LIRC setup)

## Software Installation:
NOTE: The install.sh script doesn't work properly.  Please follow the below instructions to install instead.

### Install Python PIP, Flask, Gunicorn, nginx
>sudo apt-get update
>sudo apt-get install python-pip nginx git -y
>git clone https://github.com/nebhead/spkr-select
>sudo pip install gunicorn flask pickle

### Setup nginx to proxy to gunicorn
>sudo rm /etc/nginx/sites-enabled/default # Delete default configuration
>sudo cp spkr-select.nginx /etc/nginx/sites-available/spkr-select # Copy configuration file to nginx
>sudo ln -s /etc/nginx/sites-available/spkr-select /etc/nginx/sites-enabled # Create link in sites-enabled
>sudo service nginx restart # Restart nginx

### LIRC Install and Configuration
>echo "Installing and configuring LIRC... "
>sudo apt-get install lirc python-lirc -y
>echo "lirc_dev" >> /etc/modules
>echo "lirc_rpi gpio_in_pin=02" >> /etc/modules # **** EDIT GPIO PIN ****
>echo "dtoverlay=lirc-rpi,gpio_in_pin=02" >> /boot/config.txt  # **** EDIT GPIO PIN ****

### Copy LIRC configuration files to /etc/lirc (make sure to include these in the install directory)
>sudo cp hardware.conf /etc/lirc/hardware.conf
>sudo cp lircd.conf /etc/lirc/lircd.conf
>sudo cp lircrc.txt /etc/lirc/.lircrc
>sudo cp lircrc.txt .lircrc
>sudo /etc/init.d/lirc stop
>sudo /etc/init.d/lirc start

### Configure Crontab for boot
>sudo crontab -l > mycron
>echo "@reboot cd /home/pi/spkr-select && sudo sh boot.sh &" >> mycron
>sudo crontab mycron
>rm mycron
