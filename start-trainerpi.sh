#!/bin/bash

# Ensure that bluetooth is powered on
bluetoothctl power on

# Launch the script, assuming that there is a virtualenv named trainerpi-ve
# But before trying to launch, ensure that there is only one instance
if pgrep -f "python trainerpi.py" > /dev/null
then
    echo "trainerpi is already running"
else
    cd ~/trainerpi/
    trainerpi-ve/bin/python trainerpi.py
fi

