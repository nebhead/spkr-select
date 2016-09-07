#!/bin/sh
echo "*****************************************"
echo "Welcome to the Speaker Selector Installer"
echo "*****************************************"
echo ""
read -p "Press [Enter] key to start..."
echo ""
echo "Let's install Python PIP and nginx first... "
# Install Python PIP, Flask, Gunicorn, nginx
sudo apt-get update
sudo apt-get install python-pip nginx -y
echo "Next, install gunicorn and flask."
sudo pip install gunicorn flask
# Setup nginx to proxy to gunicorn
echo "Configuring nginx..."
sudo rm /etc/nginx/sites-enabled/default # Delete default configuration
sudo cp spkr-select.nginx /etc/nginx/sites-available/spkr-select # Copy configuration file to nginx
sudo ln -s /etc/nginx/sites-available/spkr-select /etc/nginx/sites-enabled # Create link in sites-enabled
sudo service nginx restart # Restart nginx
# LIRC Install and Configuration
echo "Installing and configuring LIRC... "
sudo apt-get install lirc python-lirc -y
echo "lirc_dev" >> /etc/modules
echo "lirc_rpi gpio_in_pin=02" >> /etc/modules # **** EDIT GPIO PIN ****
echo "dtoverlay=lirc-rpi,gpio_in_pin=02" >> /boot/config.txt  # **** EDIT GPIO PIN ****
# Copy LIRC configuration files to /etc/lirc (make sure to include these in the install directory)
sudo cp hardware.conf /etc/lirc/hardware.conf
sudo cp lircd.conf /etc/lirc/lircd.conf
sudo cp lircrc.txt /etc/lirc/.lircrc
sudo cp lircrc.txt .lircrc
sudo /etc/init.d/lirc stop
sudo /etc/init.d/lirc start
# Configure Crontab for boot
echo "Adding boot script to crontab..." 
sudo crontab -l > mycron
echo "@reboot cd /home/pi/spkr-select && sudo sh boot.sh &" >> mycron
sudo crontab mycron
rm mycron
# Finish
echo "Aaaannnd, we're done... reboot required"
