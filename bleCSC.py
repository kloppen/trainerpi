from bluepy.btle import UUID, Peripheral, DefaultDelegate
import struct
import collections
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


# TODO: Remove?
def meas_difference(t1: int, t2: int, bits: int) -> float:
    """
    Determines the difference between two measurements
    :param t1: The first measurement
    :param t2: The second measurement
    :param bits: The number of bits for the measurement (when it wraps around to zero)
    :return: The difference between the two
    """
    if t2 < t1:
        # It wrapped around 2**bits
        return ((1 << bits) - 1) - t1 + t2
    return t2 - t1


class SpeedAveragingSegment:
    """
    This class is used for speed averaging. Each "segment" is the period between subsequent changes in the rotation
    count provided by the sensor.

    A window is a period of time that contains part or all of one or more segment.
    """
    def __init__(self, t_start: float, n_start: int):
        self.t_start = t_start
        self.t_end = None
        self.n_start = n_start
        self.n_end = None

    def set_finish(self, t_end, n_end):
        self.t_end = t_end
        self.n_end = n_end

    @property
    def t_total(self) -> float:
        return self.t_end - self.t_start

    @property
    def rotation_speed(self) -> float:
        return (self.n_end - self.n_start) / (self.t_end - self.t_start)

    def time_within_window(self, window_start: float, window_end: float) -> float:
        if self.rotation_speed is None:
            return 0.  # The segment is not yet complete
        return min(window_end, self.t_end) - max(window_start, self.t_start)


AVERAGING_TIME = 3.


class SpeedAverager:
    def __init__(self):
        self.speed_segments = []
        self.cur_speed_segment = None

    def update_average(self, cur_t: float, cur_n: int) -> float:
        if self.cur_speed_segment is None:
            self.cur_speed_segment = SpeedAveragingSegment(cur_t, cur_n)

        if self.cur_speed_segment.n_start != cur_n:
            self.cur_speed_segment.set_finish(cur_t, cur_n)
            self.speed_segments.append(self.cur_speed_segment)
            self.cur_speed_segment = SpeedAveragingSegment(cur_t, cur_n)

            self.cur_speed_segment = list([ss for ss in self.speed_segments if ss.t_end >= cur_t - AVERAGING_TIME])

            t_window = sum([s.time_within_window(cur_t - AVERAGING_TIME, cur_t) for s in self.speed_segments])
            if t_window > 0:
                return sum([s.time_within_window(cur_t - AVERAGING_TIME, cur_t) * s.rotation_speed
                            for s in self.speed_segments if s.rotation_speed is not None]) / t_window
            return 0.  # The window contains no completed segments


class CSCDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
        self.notification_callback = None
        self.average_wheel = SpeedAverager()
        self.average_crank = SpeedAverager()

    def handleNotification(self, cHandle, data):
        meas = CSCMeasurement()
        meas.from_bytes(data)

        if meas.crank_revolution_data_present:
            crank_speed = self.average_crank.update_average(meas.crank_event_time / 1024, meas.crank_revs)
            self.notification_callback(0., crank_speed)

        if meas.wheel_revolution_data_present:
            wheel_speed = self.average_wheel.update_average(meas.wheel_event_time / 1024, meas.wheel_revs)
            self.notification_callback(wheel_speed, 0.)


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
                notification_callback: Callable[[float, float], None]):
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
    async def wait_for_notifications(self, time: float) -> bool:
        """
        Wait `time` seconds for a notification
        :param time: The number of seconds to wait
        :return: A boolean indicating whether a notification was received
        """
        return self.peripheral.waitForNotifications(time)
