import bleCSC
import numpy
import asyncio
import curses


ROLLING_LENGTH = 2096.  # mm
power_curve = numpy.loadtxt("power-4.csv", delimiter=",")


class CSCWorker:
    def __init__(self):
        self.address = ""
        self._number = 0
        self.stdscr = None
        self._location_row = 0
        self._data_row = 0
        self._location = None

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, value):
        self._number = value
        n = 3
        self._location_row = n * value
        self._data_row = n * value + 1

    def handle_notification(self, wheel_speed: float, crank_speed: float) -> None:
        speed = wheel_speed * 3600. * ROLLING_LENGTH / 1e+6
        power = numpy.interp(speed, power_curve[:, 0], power_curve[:, 1])
        if "Wheel" in self._location:
            self.stdscr.addstr(self._data_row, 0, "Wheel: {:2.0f} km/h, Power: {:3.0f} W".format(
                wheel_speed * 3600. * ROLLING_LENGTH / 1e+6,
                power
            ))
        if "Crank" in self._location:
            self.stdscr.addstr(self._data_row, 0, "Crank: {:3.0f}".format(
                crank_speed * 60.
            ))
        self.stdscr.refresh()

    async def worker(self):
        sensor = bleCSC.CSCSensor()
        sensor.connect(self.address, self.handle_notification)
        await asyncio.sleep(0)
        self._location = sensor.get_location()
        self.stdscr.addstr(self._location_row, 0, "Location: {}".format(self._location))
        self.stdscr.refresh()
        await asyncio.sleep(0)
        sensor.notifications(True)
        while True:
            try:
                await asyncio.sleep(0)
                notify_ret = await sensor.wait_for_notifications(1.0)
                if notify_ret:
                    continue
                self.stdscr.addstr(self._data_row, 0, "Waiting for Sensor {}...".format(self.number))
                self.stdscr.refresh()
            except (KeyboardInterrupt, SystemExit):
                break


def main_screen(stdscr):
    stdscr.clear()
    curses.curs_set(0)
    stdscr.refresh()

    sensor1_thread = CSCWorker()
    sensor1_thread.address = "D0:AC:A5:BF:B7:52"
    sensor1_thread.number = 1
    sensor1_thread.stdscr = stdscr

    sensor2_thread = CSCWorker()
    sensor2_thread.address = "C6:F9:84:6A:C0:8E"
    sensor2_thread.number = 2
    sensor2_thread.stdscr = stdscr

    ioloop = asyncio.get_event_loop()
    tasks = [ioloop.create_task(sensor1_thread.worker()),
             ioloop.create_task(sensor2_thread.worker())]
    wait_tasks = asyncio.wait(tasks)
    ioloop.run_until_complete(wait_tasks)
    ioloop.close()


curses.wrapper(main_screen)
