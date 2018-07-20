#!/bin/bash

# Ensure that bluetooth is powered on
bluetoothctl power on

# Launch the script, assuming that there is a virtualenv named trainerpi-ve
trainerpi-ve/bin/python trainerpi.py

