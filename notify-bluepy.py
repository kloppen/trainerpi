from bluepy.btle import UUID, Peripheral, DefaultDelegate
from binascii import hexlify
import struct


class CSCDelegate(DefaultDelegate):
    def __init__(self, params):
        DefaultDelegate.__init__(self)
        print("Initializing CSCDelegate")

    def handleNotification(self, cHandle, data):
        print("Notification from handle: {} Value: {}".format(
            cHandle, data))

csc_service_uuid = UUID(0x1816)
csc_char_uuid = UUID(0x2A5B)

p = Peripheral("D0:AC:A5:BF:B7:52", "random")
p.setDelegate(CSCDelegate(p))
print("Peripheral: {}".format(p))

CSCService = p.getServiceByUUID(csc_service_uuid)
print("Service: {}".format(CSCService))

CSCChar = CSCService.getCharacteristics(csc_char_uuid)[0]
print("Characteristic: {}".format(CSCChar))

hCSCChar = CSCChar.getHandle()
print("Handle: {}".format(hCSCChar))

hCCC = []

for descriptor in p.getDescriptors(hCSCChar):
    print("Descriptor handle: {} uuid: {}".format(
        descriptor.handle, descriptor.uuid))
    if descriptor.uuid == 0x2902:
        hCCC.append(descriptor.handle)
        print(".. Storing CCC handle")

for h in hCCC:
    print("Writing to CCC handle {}".format(h))
    p.writeCharacteristic(h, struct.pack("<bb", 0x01, 0x00))

print("Entering loop...Press ctrl+c to exit")

while True:
    try:
        if p.waitForNotifications(1.0):
            continue
        print("Waiting...")
    except (KeyboardInterrupt, SystemExit):
        break


print("Exiting")

