from bluepy import btle
# from btle import Peripheral, ADDR_TYPE_RANDOM, AssignedNumbers
from binascii import hexlify
import time

class CSC(btle.Peripheral):
    def __init__(self, addr):
        btle.Peripheral.__init__(self, addr, addrType=btle.ADDR_TYPE_RANDOM)

if __name__=="__main__":
    cccid = btle.AssignedNumbers.client_characteristic_configuration
    cscid = btle.AssignedNumbers.cyclingSpeedAndCadence
    cscmid = btle.AssignedNumbers.csc_measurement

    csc = None
    try:
        csc = CSC("D0:AC:A5:BF:B7:52")
        service, = [s for s in csc.getServices() if s.uuid==cscid]
        ccc, = service.getCharacteristics(forUUID=str(cscmid))
        
        if 0: # This doesn't work
            ccc.write('\1\0')
        else:
            desc = csc.getDescriptors(service.hndStart,
                                      service.hndEnd)
            d = [d[0] for d in desc if d.uuid==cscid]
            csc.writeCharacteristic(d.handle, '\1\0')

        t0=time.time()
        
        def print_csc(cHandle, data):
            print("data: {}".format(hexlify(data)))

        csc.delegate.handleNotification = print_csc

        for x in range(10):
            csc.waitForNotifications(3.)

    finally:
        if csc:
            csc.disconnect()

