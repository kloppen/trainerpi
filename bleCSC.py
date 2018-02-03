from bluepy.btle import UUID, Peripheral, DefaultDelegate
import struct


class CSCMeasurement():
    """
    Defines the fields of a CSC measurement
    """
    def __init__(self):
        self.wheel_revolution_data_present = False
        self.crank_revolution_data_present = False
        self.cum_wheel_revs = 0
        self.last_wheel_event_time = 0.
        self.cum_crank_revs = 0
        self.last_crank_event_time = 0.

    def from_bytes(self, measurement: bytes) -> None:
        """
        Parses the raw bytes that the sensor provides
        :param measurement: The raw bytes provided by the sensor
        :return:
        """
        flags = measurement[0]
        self.wheel_revolution_data_present = bool(flags & (1 << 0))
        self.crank_revolution_data_present = bool(flags & (1 << 1))

        if self.wheel_revolution_data_present:
            data = struct.unpack("<BLH", measurement)
            self.cum_wheel_revs = data[1]
            self.last_wheel_event_time = data[2]
        elif self.crank_revolution_data_present:
            data = struct.unpack("<BHH", measurement)
            self.cum_crank_revs = data[1]
            self.last_crank_event_time = data[2]


class CSCDelegate(DefaultDelegate):
    def __init__(self, params):
        DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        meas = CSCMeasurement()
        meas.from_bytes(data)
        print("WR: {} LWT: {} CR: {} LCT: {} Handle: {}".format(
            meas.cum_wheel_revs,
            meas.last_wheel_event_time,
            meas.cum_crank_revs,
            meas.last_crank_event_time,
            cHandle
        ))


csc_service_uuid = UUID(0x1816)
csc_char_uuid = UUID(0x2A5B)
location_char_uuid = UUID(0x2A5D)


class CSCSensor:
    """
    This class defines a cycling speed and cadence sensor
    """

    def __init__(self, address: str):
        """
        Initializes the class
        :param address: A string with the address of the sensor
        """
        self.peripheral = Peripheral(address, "random")
        self.peripheral.setDelegate(CSCDelegate(self.peripheral))  # TODO: Should allow user to set this
        self.cscService = self.peripheral.getServiceByUUID(csc_service_uuid)
        self.cscCharacteristic = self.cscService.getCharacteristics(csc_char_uuid)[0]
        self.cscCharacteristicHandle = self.cscCharacteristic.getHandle()

    def get_location(self) -> str:
        """
        Returns the location of the sensor
        :return: an integer representing the location
        """
        location_list = ["Other",
                         "Top of shoe",
                         "In shoe",
                         "Hip",
                         "Front Wheel",
                         "Left Crank",
                         "Right Crank",
                         "Left Pedal",
                         "Right Pedal",
                         "Front Hub",
                         "Rear Dropout",
                         "Chainstay",
                         "Rear Wheel",
                         "Rear Hub",
                         "Chest",
                         "Spider",
                         "Chain Ring"]
        characteristic = self.cscService.getCharacteristics(location_char_uuid)[0]
        handle = characteristic.getHandle()
        location = self.peripheral.readCharacteristic(handle)
        return location_list[int.from_bytes(location, "little")]

    def notifications(self, notify: bool) -> None:
        """
        Starts or stops notifications from this sensor
        :param notify: True to start notifications, False to stop
        :return: None
        """
        hccc = 0
        for descriptor in self.peripheral.getDescriptors(self.cscCharacteristicHandle):
            if descriptor.uuid == 0x2902:
                hccc = descriptor.handle
                break

        self.peripheral.writeCharacteristic(hccc, struct.pack("<bb", 0x01 & notify, 0x00))

    def wait_for_notifications(self, time: float) -> bool:
        """
        Wait `time` seconds for a notification
        :param time: The number of seconds to wait
        :return: A boolean indicating whether a notification was received
        """
        return self.peripheral.waitForNotifications(time)
