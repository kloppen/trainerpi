
PiTFT Plus LCD/Touchscreen [https://learn.adafruit.com/running-opengl-based-games-and-emulators-on-adafruit-pitft-displays/pitft-setup]

Install image that includes TFT support from here:
https://learn.adafruit.com/adafruit-pitft-28-inch-resistive-touchscreen-display-raspberry-pi/easy-install

# PiTFT on Rasperrian Stretch

https://learn.adafruit.com/adafruit-pitft-28-inch-resistive-touchscreen-display-raspberry-pi/help-faq

```
sudo apt-get update
wget https://raw.githubusercontent.com/adafruit/Adafruit-PiTFT-Helper/master/adafruit-pitft-helper
chmod +x adafruit-pitft-helper
sudo ./adafruit-pitft-helper -t 28r
```
Select the following options:

Console = yes
GPIO23 = yes

Reboot the pi

# Bluetooth

https://www.jaredwolff.com/blog/get-started-with-bluetooth-low-energy/
https://www.spinics.net/lists/linux-bluetooth/msg66942.html

Install latest bluez (https://learn.adafruit.com/install-bluez-on-the-raspberry-pi/installation):

```
wget http://www.kernel.org/pub/linux/bluetooth/bluez-5.48.tar.xz
tar xvf bluez-5.48.tar.xz
cd bluez-5.37
sudo apt-get update
sudo apt-get install libusb-dev libdbus-1-dev libglib2.0-dev libudev-dev libical-dev libreadline-dev
./configure
make
sudo make install
systemctl status bluetooth
sudo systemctl start bluetooth
```


Scan BT-LE devices:

```
bluetoothctl
[bluetooth]# scan on
[bluetooth]# scan off
[bluetooth]# connect <BLE ADDRESS>
[sensor-name]# list-attributes <BLE ADDRESS>
[sensor-name]# select-attribute /org/bluez/hci0/dev_D0_AC_A5_BF_B7_52/service0018/char0019
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

