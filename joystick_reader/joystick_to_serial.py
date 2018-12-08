import logging
import time
import os
import serial
from input import JoystickReader

os.environ["SDL_VIDEODRIVER"] = "dummy"
logging.basicConfig(level=logging.DEBUG)

ser = serial.Serial('/dev/ttyUSB0', 9600)
print("Sleeping 2 seconds...")
time.sleep(2)

def toBytes(n):
    n_h = (n + 32768) >> 8
    n_l = (n + 32768) & 0xFF
    return chr(n_h)+chr(n_l)

jr = JoystickReader()    
# jr.input_updated.add_callback(vp.printVelocities)
devs = jr.getAvailableDevices()
if devs:
    num = len(devs)
    idx = 0
    if num>1:
        print "There are ", num, " joysticks connected. Choose which one you would like to use."
        for device in devs:
            print device
        try:
            idx = int(raw_input('id:'))
        except ValueError:
            print "Not a number"
    print "Will use [%s] for input" % devs[idx]["name"]
    jr.start_input(devs[idx]["name"])        
    k = 0
    while True:
        roll = jr.roll
        pitch = jr.pitch
        yaw = jr.yaw
        throttle = jr.throttle

        # De http://ardupilot.org/rover/docs/common-radio-control-calibration.html
        # Recommended channels:
        # Ch 1: Roll
        # Ch 2: Pitch
        # Ch 3: Throttle
        # Ch 4: Yaw
        # Ch 8: Flight modes
        msg = toBytes(roll) + toBytes(pitch) + toBytes(throttle) + toBytes(yaw)
    
        ser.write(msg)
        ser.flush()
        print ser.readline()
        time.sleep(0.05)


        # print k
        # print jr.yaw
        # print jr.throttle
        # k += 1
        # time.sleep(1)
else:
    print "No available devices. Exiting."
