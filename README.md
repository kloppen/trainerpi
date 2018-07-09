# Introduction


# Bill of Materials

PiTFT Plus LCD/Touchscreen [https://learn.adafruit.com/running-opengl-based-games-and-emulators-on-adafruit-pitft-displays/pitft-setup]

# Installation and Setup
## Basic Setup
These instructions are based on installing Raspberrian Stretch. If you are
using a newer version of Raspberrian, the instructions will likely work with
a few tweaks.

First, install Raspberrian Stretch on an SD card.

Plug in the Pi to a keyboard, mouse and monitor and boot it. You'll need to
connect to your WiFi network. You'll also want to use the Raspberry Pi
Configuration utility to set a few parameters:

- Hostname: `trainerpi`
- Boot: To CLI
- SSH: Enabled
- Keyboard: Your choice (I used United States/English (US)
- Locale: Your choice
- Timezone

Now, reboot the Pi and you'll be able to ssh into it.

Now is a very good time to change the password for the default `pi` account.
Also, you'll probably want to copy your SSH key to the Pi so that you can
ssh into it without having to enter a password. Optionally, once you've done
so, you can disable password authentication.

You'll probably want to update/upgrade all the packages on the Pi using
`apt-get`.

## Configuration of the Screen
Follow the instructions from [here](https://learn.adafruit.com/adafruit-pitft-28-inch-resistive-touchscreen-display-raspberry-pi/easy-install-2)

```
cd ~
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/adafruit-pitft.sh
chmod +x adafruit-pitft.sh
sudo ./adafruit-pitft.sh
```

Select the following options:

- PiTFT 2.4", 2.8" or 3.2" resistive (240x320)
- 90 Degrees (landscape)
- Console: yes

Reboot the pi

## Setup Bluetooth
Install latest bluez. See
[https://learn.adafruit.com/install-bluez-on-the-raspberry-pi/installation](https://learn.adafruit.com/install-bluez-on-the-raspberry-pi/installation):

```
wget http://www.kernel.org/pub/linux/bluetooth/bluez-5.49.tar.xz
tar xvf bluez-5.49.tar.xz
cd bluez-5.49
sudo apt-get update
sudo apt-get install libusb-dev libdbus-1-dev libglib2.0-dev libudev-dev libical-dev libreadline-dev
./configure
make
sudo make install
systemctl status bluetooth
sudo systemctl start bluetooth
```

## Install the Required System Packages
Install the following packages

```
sudo apt-get install bluez
sudo apt-get install libglib2.0-dev
sudo apt-get install python3-dev
sudo apt-get install libboost-python-dev
sudo apt-get install libboost-dev
sudo apt-get install libboost-all-dev
sudo apt-get install libbluetooth-dev libreadline-dev
sudo apt-get install libgtk-3-dev
sudo apt-get install bluetooth
sudo apt-get install pi-bluetooth
sudo apt-get install bluez
sudo apt-get install libglib2.0-dev
```

## Install the Required Python Packages


# Bluetooth
You'll need to find the addresses of your two sensors. You can do this by using
`bluetoothctl` as follows:

```
bluetoothctl
[bluetooth]# scan on
```
Now, you'll need to move one of the sensors so that it wakes up and starts
sending data. The device address should show up on your screen when you do
so. Make note of this address. Now, move the other sensor and make note of
its address.

Once you have the two addresses, you can connect to one of the sensors to
see the data stream coming out of it.

```
[bluetooth]# scan off
[bluetooth]# connect <BLE ADDRESS>
[sensor-name]# info <BLE ADDRESS>
```

This should produce an output that includes a line about Cycling Speed and
Cadence. Do the same for the other sensor. This will tell you that you're
able to connect. You can now quit by typing `quit`

# Bluetooth Theory
The Bluetooth CSC sensors

# Configuration



[sensor-name]# list-attributes <BLE ADDRESS>
[sensor-name]# select /org/bluez/hci0/dev_D0_AC_A5_BF_B7_52/service0018/char0019
[sensor-name:/service0018/char0019]# notify on
[sensor-name:/service0018/char0019]# notify off
[sensor-name:/service0018/char0019]# disconnect
```

Sensor 1: D0:AC:A5:BF:B7:52
UUIDs:
	00001800-0000-1000-8000-00805f9b34fb
	00001801-0000-1000-8000-00805f9b34fb
	00001816-0000-1000-8000-00805f9b34fb
	0000fe59-0000-1000-8000-00805f9b34fb
	6e400001-b5a3-f393-e0a9-e50e24dcca9e

    
https://github.com/IanHarvey/bluepy/issues/53

https://github.com/ukBaz/python-bluezero
https://www.youtube.com/watch?v=F39xhYWHDKA

Information about GATT service "Cycling Speed and Cadence":
https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.service.cycling_speed_and_cadence.xml


```
# sudo pip3 install pygatt
# sudo pip3 install pybluez
# sudo apt-get install python-dev
# sudo apt-get install python-gattlib
# sudo apt-get install libboost-python-dev
# sudo apt-get install libboost-dev
# sudo apt-get install libboost-all-dev
# sudo pip3 install gattlib
# sudo pip3 install pybluez[ble]
# sudo apt-get install libgtk2.0-dev
# sudo apt-get install libbluetooth-dev libreadline-dev
# sudo pip3 install bluepy
sudo pip3 install bluezero
sudo pip3 install dbus
```

https://bitbucket.org/OscarAcena/pygattlib
https://www.slideshare.net/LarsAlexanderBlumber/ble-with-raspberry-pi


# Bluetooth (Stretch)

```
sudo apt-get install python3-dev
sudo apt-get install libboost-python-dev
sudo apt-get install libboost-dev
sudo apt-get install libboost-all-dev
sudo apt-get install libgtk2.0-dev
sudo apt-get install libbluetooth-dev libreadline-dev
sudo apt-get install libgtk-3-dev
pip3 download gattlib
tar xvzf ./gattlib-0.20150805.tar.gz
cd gattlib-0.20150805/
sed -ie 's/boost_python-py34/boost_python-py35/' setup.py
sudo pip3 install .
sudo apt-get install bluetooth
sudo apt-get install pi-bluetooth
sudo reboot now
sudo apt-get install bluez
sudo apt-get install libglib2.0-dev
sudo pip3 install bluepy
```

https://github.com/rlangoy/bluepy_examples_nRF51822_mbed


```
a = numpy.loadtxt("power-4.csv", delimiter=",")
numpy.interp(xi, a[:,0], a[:,1])
```

http://effbot.org/tkinterbook/

Termianl printing/updating
https://stackoverflow.com/questions/2122385/dynamic-terminal-printing-with-python

# Console Text Size
```
sudo dpkg-reconfigure console-setup
```
Choose the font VGA, then set the font size as 16x32 (was 8x8)

# GPIO Input
The screen comes with four buttons. We'll map these so that we can launch the program with them.

First, install the prerequisites:

```
sudo apt-get install input-utils
```

Run lsinput to list the input devices (disconnect any keyboards, etc.)

```
lsinput
```

Now, 

Reference: http://blog.gegg.us/2017/01/setting-up-a-gpio-button-keyboard-on-a-raspberry-pi/


# References

- https://learn.adafruit.com/install-bluez-on-the-raspberry-pi/installation
- https://www.jaredwolff.com/blog/get-started-with-bluetooth-low-energy/
- https://www.spinics.net/lists/linux-bluetooth/msg66942.html
- https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.service.cycling_speed_and_cadence.xml
