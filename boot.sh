#!/bin/sh
cd /home/pi/spkr-select
#sudo python app.py &
# Run via Gunicorn / nginx
sudo gunicorn app:app &
# Run via Python
sudo python control.py &
