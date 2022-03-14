#!/bin/bash

# Install Dependencies
sudo apt-get install libcblas-dev libhdf5-dev libhdf5-serial-dev libatlas-base-dev
sudo apt-get install libjasper-dev libqtgui4 libqt4-test libilmbase-dev 
sudo apt-get install libopenexr-dev libgstreamer1.0-dev libavcodec-dev libavformat-dev
sudo apt-get install libswscale-dev libwebp-dev

sudo pip3 install flask
sudo pip3 install numpy
sudo pip3 install opencv-python

pip3 install flask
pip3 install numpy
pip3 install opencv-python

git clone https://github.com/125007007/pi_security_camera.git

cd pi_security_camera

ls