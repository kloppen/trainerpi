
PiTFT Plus LCD/Touchscreen [https://learn.adafruit.com/running-opengl-based-games-and-emulators-on-adafruit-pitft-displays/pitft-setup]

```
cd
curl -O https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/pitft-fbcp.sh
sudo bash pitft-fbcp.sh
```

Select manual configuration. Select PiTFT Plus resistive. Select normal (landscape) HDMI rotation. Select 0 degree TFT rotation. Reboot when prompted.

https://www.jaredwolff.com/blog/get-started-with-bluetooth-low-energy/
https://www.spinics.net/lists/linux-bluetooth/msg66942.html


Scan BT-LE devices:

```
sudo hcitool lescan
```

Connect to BE-LE device:

```
sudo gatttool -b <BLE ADDRESS> -I
connect
```

Sensor 1: D0:AC:A5:BF:B7:52
    


```
pip3 install pexpect
pip3 install "pygatt[GATTTOOL]"
```

```
a = numpy.loadtxt("power-4.csv", delimiter=",")
numpy.interp(xi, a[:,0], a[:,1])
```

http://effbot.org/tkinterbook/
