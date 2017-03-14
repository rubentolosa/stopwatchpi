#!/bin/bash
xset s off         # don't activate screensaver
xset -dpms         # disable DPMS (Energy Star) features.
xset s noblank     # don't blank the video device
while true
do
    /usr/local/stopwatchpi/chrono.py
done
