import bleCSC


class CSCDelegatePrint(bleCSC.CSCDelegate):
    def __init__(self):
        super(CSCDelegatePrint, self).__init__()

    def handle_speed_notification(self, wheel_speed: float, crank_speed: float) -> None:
        print("Wheel: {} RPM, Crank: {} RPM".format(
            wheel_speed * 60.,
            crank_speed * 60.
        ))


sensor = bleCSC.CSCSensor("D0:AC:A5:BF:B7:52", CSCDelegatePrint())
location = sensor.get_location()
print("Location: {}".format(location))

sensor.notifications(True)

print("Entering loop...Press ctrl+c to exit")

while True:
    try:
        if sensor.wait_for_notifications(1.0):
            continue
        print("Waiting...")
    except (KeyboardInterrupt, SystemExit):
        break

print("Exiting")
