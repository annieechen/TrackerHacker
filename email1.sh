#!/bin/sh
#
#

cd /home/pi
sudo python email1.py
sudo python email2.py
sudo python email3.py
sudo rm -rf /home/pi/datawrite.txt
sudo rm -rf /home/pi/overalldata.txt
sudo rm -rf /home/pi/timestamp.txt
cd /
