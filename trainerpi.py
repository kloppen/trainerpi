import bleCSC
import numpy


ROLLING_LENGTH = 2096.  # mm


class CSCDelegatePrint(bleCSC.CSCDelegate):
    def __init__(self):
        super(CSCDelegatePrint, self).__init__()
        self.power_curve = numpy.loadtxt("power-4.csv", delimiter=",")

    def handle_speed_notification(self, wheel_speed: float, crank_speed: float) -> None:
        speed = wheel_speed * 3600. * ROLLING_LENGTH / 1e+6
        power = numpy.interp(speed, self.power_curve[:, 0], self.power_curve[:, 1])
        print("Wheel: {:2.0f} km/h, Power (assuming resistance=4): {:3.0f} W".format(
            wheel_speed * 3600. * ROLLING_LENGTH / 1e+6,
            power
            # crank_speed * 60.
        ))


wheel_sensor = bleCSC.CSCSensor("D0:AC:A5:BF:B7:52", CSCDelegatePrint())
location_wheel = wheel_sensor.get_location()
print("Location (wheel_sensor): {}".format(location_wheel))

# crank_sensor = bleCSC.CSCSensor("C6:F9:84:6A:C0:8E", CSCDelegatePrint())
# location_crank = crank_sensor.get_location()
# print("Location (crank_sensor): {}".format(location_crank))

wheel_sensor.notifications(True)
# crank_sensor.notifications(True)

print("Entering loop...Press ctrl+c to exit")

while True:
    try:
        if wheel_sensor.wait_for_notifications(1.0):  # or crank_sensor.wait_for_notifications(1.0):
            continue
        print("Waiting...")
    except (KeyboardInterrupt, SystemExit):
        break

print("Exiting")
