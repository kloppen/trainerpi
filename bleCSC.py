from bluepy.btle import UUID, Peripheral, DefaultDelegate
import struct
import time
from typing import Callable
import asyncio


class CSCMeasurement:
    """
    Defines the fields of a CSC measurement
    """
    def __init__(self):
        self.wheel_revolution_data_present = False
        self.crank_revolution_data_present = False
        self.wheel_revs = 0
        self.wheel_event_time = 0
        self.crank_revs = 0
        self.crank_event_time = 0
        self.time = 0.

    def from_bytes(self, measurement: bytes) -> None:
        """
        Parses the raw bytes that the sensor provides
        :param measurement: The raw bytes provided by the sensor
        :return:
        """
        self.time = time.time()
        flags = measurement[0]
        self.wheel_revolution_data_present = bool(flags & (1 << 0))
        self.crank_revolution_data_present = bool(flags & (1 << 1))

        if self.wheel_revolution_data_present:
            data = struct.unpack("<BLH", measurement)
            self.wheel_revs = data[1]
            self.wheel_event_time = data[2]
        elif self.crank_revolution_data_present:
            data = struct.unpack("<BHH", measurement)
            self.crank_revs = data[1]
            self.crank_event_time = data[2]


class Measurement:
    """
    This class is used for speed averaging. Each "measurement" is the period between subsequent "events." That is, it's
    the period between times when the CSC sensor reports new "last event time."
    """
    def __init__(self, start_t_ticks: int, start_n: int, start_real_t: float):
        self.start_t_ticks = start_t_ticks
        self.start_n = start_n
        self.start_real_t = start_real_t
        self.end_t_ticks = None
        self.end_n = None

    def set_end(self, end_t_ticks: int, end_n: int):
        self.end_t_ticks = end_t_ticks
        self.end_n = end_n


class SpeedAverager:
    def __init__(self, ticks_per_second: int, averaging_window: float, bits_t: int, bits_n: int):
        """
        This class provides the ability to average speed over a certain averaging window.

        Since the bluetooth CSC sensors provide integers for time and the number of rotations, and these integers
        are of finite width, we need to account for overflow (in which case, the sensor simply wraps around zero)

        :param ticks_per_second: The number of ticks of the timer counter per second (1024, normally)
        :param bits_t: The number of bits that represents time
        :param bits_n: The number of bits that represents rotations
        :param averaging_window: The time over which to average the speed
        """
        self.measurements = []
        self.cur_measurement = None
        self.cumulative_rotations = 0
        self.ticks_per_second = ticks_per_second
        self.averaging_window = averaging_window
        self.bits_t = bits_t
        self.bits_n = bits_n
        # Since the time and number of revolutions wraps around zero, we will store the smallest numbers that these
        # could be and wrap as necessary
        self.prev_le_t_ticks = None
        self.prev_le_n = None

    def add_measurement(self, last_event_t_ticks: int, last_event_n: int) -> None:
        if self.cur_measurement is None:
            self.cur_measurement = Measurement(last_event_t_ticks, last_event_n, time.time())
            self.prev_le_t_ticks = last_event_t_ticks
            self.prev_le_n = last_event_n

        while last_event_t_ticks < self.prev_le_t_ticks:
            last_event_t_ticks += 2 ** self.bits_t

        while last_event_n < self.prev_le_n:
            last_event_n += 2 ** self.bits_n

        self.prev_le_t_ticks = last_event_t_ticks
        self.prev_le_n = last_event_n

        if self.cur_measurement.start_t_ticks != last_event_t_ticks:
            self.cur_measurement.set_end(last_event_t_ticks, last_event_n)
            self.cumulative_rotations += self.cur_measurement.end_n - self.cur_measurement.start_n
            self.measurements.append(self.cur_measurement)
            self.cur_measurement = Measurement(last_event_t_ticks, last_event_n, time.time())

    def get_average(self) -> float:
        self.measurements = list([
            meas for meas in self.measurements if meas.start_real_t >= time.time() - self.averaging_window
        ])

        t_window = sum([meas.end_t_ticks - meas.start_t_ticks for meas in self.measurements])

        if t_window > 0:
            n_window = sum([meas.end_n - meas.start_n for meas in self.measurements])
            return n_window / (t_window / self.ticks_per_second)
        return 0.


class CSCDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
        self.notification_callback = None
        self.average_wheel = SpeedAverager(ticks_per_second=1024, averaging_window=3., bits_t=16, bits_n=32)
        self.average_crank = SpeedAverager(ticks_per_second=1024, averaging_window=3., bits_t=16, bits_n=16)

    def handleNotification(self, c_handle, data):
        meas = CSCMeasurement()
        meas.from_bytes(data)

        if meas.crank_revolution_data_present:
            self.average_crank.add_measurement(meas.crank_event_time, meas.crank_revs)
            crank_speed = self.average_crank.get_average()
            cumulative_rotations = self.average_crank.cumulative_rotations
            self.notification_callback(0., crank_speed, cumulative_rotations)

        if meas.wheel_revolution_data_present:
            self.average_wheel.add_measurement(meas.wheel_event_time, meas.wheel_revs)
            wheel_speed = self.average_wheel.get_average()
            cumulative_rotations = self.average_wheel.cumulative_rotations
            self.notification_callback(wheel_speed, 0., cumulative_rotations)


CSC_SERVICE_UUID = UUID(0x1816)
CSC_CHAR_UUID = UUID(0x2A5B)
LOCATION_CHAR_UUID = UUID(0x2A5D)


class CSCSensor:
    """
    This class defines a cycling speed and cadence sensor
    """

    def __init__(self):
        self.peripheral = None
        self.cscService = None
        self.cscCharacteristic = None
        self.cscCharacteristicHandle = None

    def connect(self, address: str,
                notification_callback: Callable[[float, float, int], None]):
        """
        Initializes the class
        :param address: A string with the address of the sensor
        :param notification_callback: A function that takes two floats (speed, cadence) that will be called for each
            notification
        """
        self.peripheral = Peripheral(address, "random")
        delegate = CSCDelegate()
        delegate.notification_callback = notification_callback
        self.peripheral.setDelegate(delegate)
        self.cscService = self.peripheral.getServiceByUUID(CSC_SERVICE_UUID)
        self.cscCharacteristic = self.cscService.getCharacteristics(CSC_CHAR_UUID)[0]
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
        characteristic = self.cscService.getCharacteristics(LOCATION_CHAR_UUID)[0]
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

    @asyncio.coroutine
    async def wait_for_notifications(self, wait_time: float) -> bool:
        """
        Wait `wait_time` seconds for a notification
        :param wait_time: The number of seconds to wait
        :return: A boolean indicating whether a notification was received
        """
        return self.peripheral.waitForNotifications(wait_time)
