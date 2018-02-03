import bleCSC


sensor = bleCSC.CSCSensor("D0:AC:A5:BF:B7:52")
location = sensor.get_location()
print("Location: {}".format(location))

print("Entering loop...Press ctrl+c to exit")

while True:
    try:
        if sensor.wait_for_notifications(1.0):
            continue
        print("Waiting...")
    except (KeyboardInterrupt, SystemExit):
        break

print("Exiting")
