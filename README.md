
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
bluetoothctl
[bluetooth]# connect <BLE ADDRESS>
[sensor-name]# select-attribute /org/bluez/hci0/dev_D0_AC_A5_BF_B7_52/service0018/char0019
[sensor-name:/service0018/char0019]# notify on
[sensor-name:/service0018/char0019]# notify off
[sensor-name:/service0018/char0019]# disconnect
```

Sensor 1: D0:AC:A5:BF:B7:52
    


Information about GATT service "Cyclig Speed and Cadence":
https://www.bluetooth.com/specifications/gatt/viewer?attributeXmlFile=org.bluetooth.service.cycling_speed_and_cadence.xml


```
pip3 install pygatt
```

```
a = numpy.loadtxt("power-4.csv", delimiter=",")
numpy.interp(xi, a[:,0], a[:,1])
```

http://effbot.org/tkinterbook/
