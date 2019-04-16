#!/bin/bash

echo "============================="
echo "Generate Self Signed Certs"
echo "============================="
echo ""
echo "Credit to https://www.humankode.com/ssl/create-a-selfsigned-certificate-for-nginx-in-5-minutes"
echo "for providing the steps and setup guides."

echo "Starting Script..."
if [ "$EUID" -ne 0 ]
  then echo "Error: Please run as root using sudo.  Exiting script."
  exit
fi

# Move to working directory
cd /home/pi/spkr-select/certs

# Modify the localhost configuration file
nano localhost.conf

# Create public and private key pairs based on localhost.conf information
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout localhost.key -out localhost.crt -config localhost.conf

# Move the public key to the /etc/ssl/certs directory
sudo mv localhost.crt /etc/ssl/certs/localhost.crt
# Move the private key to the /etc/ssl/private directory
sudo mv localhost.key /etc/ssl/private/localhost.key
