# Introduction
This project provides a simple interface to Bluetooth speed and cadence sensors
that you can use with your bike. It's intended for use when your bike is on a
trainer. Using power curves published
[here](http://www.powercurvesensor.com/cycling-trainer-power-curves/), it
estimates the power dissipated by the resistance unit of the trainer.

This README provides an outline of the installation and use of the `trainerpi`
software in this repository. It assumes a basic understanding of Linux, git and
Raspberry Pi.

![Image of The TrainerPi, Mounted on a Bike Stem](Screen.jpg)

# Bill of Materials
I used the following items for this project:

- [Raspberry Pi 3B](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/)
- [Adafruit 2.8" PiTFT Capacitive Touch Screen](https://learn.adafruit.com/adafruit-2-8-pitft-capacitive-touch/overview). Note, this project doesn't actually the touch functionality, so a non-touch screen would work too.
- [PiTFT Plus Pibow Case](https://www.buyapi.ca/product/pibow-pitft/). I modified mine a bit by adding a bracket to the back of the case so that I could mount it to the stem of my bike.
- (2) Bluetooth Cycling Speed and Cadence Sensors. I bought mine on eBay from a sell in China. The protocol is standardized, so any Bluetooth CSC sensor should theoretically work.
- A power supply and a USB cable


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

## Installing the Required System Packages
Install the following system packages:

```
sudo apt-get update
sudo apt-get install libusb-dev libdbus-1-dev libglib2.0-dev libudev-dev
sudo apt-get install libical-dev libreadline-dev libglib2.0-dev
sudo apt-get install bluez libglib2.0-dev python3-dev libboost-python-dev
sudo apt-get install libboost-dev libboost-all-dev libbluetooth-dev
sudo apt-get install libreadline-dev libgtk-3-dev bluetooth pi-bluetooth
sudo apt-get install libatlas-base-dev
```

## Setup Bluetooth
Install latest bluez. See
[https://learn.adafruit.com/install-bluez-on-the-raspberry-pi/installation](https://learn.adafruit.com/install-bluez-on-the-raspberry-pi/installation):

```
wget http://www.kernel.org/pub/linux/bluetooth/bluez-5.50.tar.xz
tar xvf bluez-5.50.tar.xz
cd bluez-5.50
sudo apt-get update
./configure
make
sudo make install
sudo systemctl enable bluetooth
sudo systemctl start bluetooth
```

# Playing Around with Bluetooth
You'll need to find the addresses of your two sensors. You can do this by using
`bluetoothctl` as follows.

```
bluetoothctl
[bluetooth]# power on  # This may not be necessary
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

This should produce an output that looks like the following:

```
Device D0:AC:A5:BF:B7:52 (random)
	Name: 27700-113
	Alias: 27700-113
	Appearance: 0x0480
	Paired: no
	Trusted: no
	Blocked: no
	Connected: no
	LegacyPairing: no
	UUID: Generic Access Profile    (00001800-0000-1000-8000-00805f9b34fb)
	UUID: Generic Attribute Profile (00001801-0000-1000-8000-00805f9b34fb)
	UUID: Cycling Speed and Cadence (00001816-0000-1000-8000-00805f9b34fb)
	UUID: Nordic Semiconductor ASA  (0000fe59-0000-1000-8000-00805f9b34fb)
	UUID: Nordic UART Service       (6e400001-b5a3-f393-e0a9-e50e24dcca9e)
	ManufacturerData Key: 0xffff
	ManufacturerData Value:
  6b 00 34 6c 71 03 00 01 00 01                    k.4lq.....
	RSSI: -71
```

Now, you can connect to the sensor:

```
connect <BLE ADDRESS>
```

This should produce an output like the following. Note that I've removed some
of the unnecessary lines.

```
Attempting to connect to D0:AC:A5:BF:B7:52
[CHG] Device D0:AC:A5:BF:B7:52 Connected: yes
Connection successful
...
[NEW] Primary Service
	/org/bluez/hci0/dev_D0_AC_A5_BF_B7_52/service0018
	00001816-0000-1000-8000-00805f9b34fb
	Cycling Speed and Cadence
[NEW] Characteristic
	/org/bluez/hci0/dev_D0_AC_A5_BF_B7_52/service0018/char0019
	00002a5b-0000-1000-8000-00805f9b34fb
	CSC Measurement
...
[NEW] Characteristic
	/org/bluez/hci0/dev_D0_AC_A5_BF_B7_52/service0018/char001e
	00002a5d-0000-1000-8000-00805f9b34fb
	Sensor Location
...
[CHG] Device D0:AC:A5:BF:B7:52 ServicesResolved: yes
```

Now, you'll need to switch into the `gatt` menu,  select characteristic 0x0019
and view the data. In the snippet below, replace the path after
`select-attribute` with the path for characteristic 0x0019 shown earlier.

```
menu gatt
select-attribute /org/bluez/hci0/dev_D0_AC_A5_BF_B7_52/service0018/char0019
notify on
```

You'll see a stream of data that looks like the following (to stop it, type
`notify off`).

```
[CHG] Attribute /org/bluez/hci0/dev_D0_AC_A5_BF_B7_52/service0018/char0019 Value:
  01 0e 71 00 00 3e e9                             ..q..>.
[CHG] Attribute /org/bluez/hci0/dev_D0_AC_A5_BF_B7_52/service0018/char0019 Value:
  01 0e 71 00 00 3e e9                             ..q..>.
[CHG] Attribute /org/bluez/hci0/dev_D0_AC_A5_BF_B7_52/service0018/char0019 Value:
  01 0e 71 00 00 3e e9
```

This is the raw data streaming from the sensor. The format is defined here:
[https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.service.cycling_speed_and_cadence.xml](https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.service.cycling_speed_and_cadence.xml)

## Installation of the TrainerPi Software
Just clone this repo into your Pi:

```
git clone https://github.com/kloppen/trainerpi
```

Now, create a virtualenv for use with trainerpi (optionally, you could install
all the packages in your system python. Once we've created the virtualenv, we
can install the required packages.

```
sudo pip3 install virtualenv
cd ~/trainerpi
virtualenv -p python3 trainerpi-ve
source trainerpi-ve/bin/activate
pip3 install -r requirements.txt
```

# Configuring the Code
There are a number of variables that you'll need to set, such as the addresses
of your CSC sensors. These are all defined towards to the top of `trainerpi.py`

# Launch On Boot
So that you don't have to connect a keyboard to the Pi, you'll probably want
trainerpi to start on boot. There are a number of ways to do this. The way
that I've chosen to do so is to call the script `start-trainerpi.sh` from my
`.bashrc` file. You can do so by adding the following to the end of the
`.bashrc` file for the default user on your Pi.

```bash
source trainerpi/start-trainerpi.sh
```

# Contributing
This project is licensed under the MIT license. Do with it as you please.

If you find a bug, feel free to create [an issue](https://github.com/kloppen/trainerpi/issues).
And if you want to contribute a feature, feel free to discuss it in an issue
and submit a Pull Request.


# References

- https://learn.adafruit.com/install-bluez-on-the-raspberry-pi/installation
- https://www.jaredwolff.com/blog/get-started-with-bluetooth-low-energy/
- https://www.spinics.net/lists/linux-bluetooth/msg66942.html
- https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.service.cycling_speed_and_cadence.xml
- http://www.powercurvesensor.com/cycling-trainer-power-curves/
- https://scribles.net/auto-power-on-bluetooth-adapter-on-boot-up/

