#!/bin/sh

cd /home/pi/launch
cd /usr/local/lib/python2.7/site-packages
#sudo workon cv3
sudo python trackObjs.py
cd /home/pi/launch
sudo sh email1.sh
#sudo rm -rf /home/pi/launch/images/*
cd /
