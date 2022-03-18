#!/bin/bash

sudo modprobe v4l2loopback video_nr=3
gst-launch-1.0 libcamerasrc ! 'video/x-raw,width=1920,height=1080' ! videoconvert ! tee ! v4l2sink device=/dev/video3