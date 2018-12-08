# -*- coding: utf-8 -*-
"""
Module to read input devices and send controls to the Lego NXT.

This module reads input from joysticks or other input devices and sends control
set-points to the Crazyflie. It can be configured in the UI.

Various drivers can be used to read input device data. Currently is uses the
PySDL2 driver.

"""
import traceback
import logging

logger = logging.getLogger(__name__)

from periodictimer import PeriodicTimer
from callbacks import Caller

class JoystickReader:
    """
    Thread that will read input from devices/joysticks and send control-set
    points to the Crazyflie
    """
    def __init__(self):
        from pysdl2reader import PySDL2Reader
        self.inputdevice = PySDL2Reader()

        self.roll = 0
        self.pitch = 0
        self.yaw = 0
        self.throttle = 0
        
        self._pid_flag = 0
        self._min_pow = -100
        self._max_pow = 100
        # This is based on parameter identification of the Lego NXT DC motor.
        # Must check this out once again.
        self._min_pid_ref = -16
        self._max_pid_ref = 16
        
        self._pow = 60
        self._pid_ref = 6
        
        self._old_toggle_pid = 0
        self._old_increment_ref = 0
        self._old_decrement_ref = 0

        self.old_vl = 0
        self.old_vr = 0
        
        self._available_devices = {}
        self._read_timer = PeriodicTimer(0.01, self.read_input)
        self.input_updated = Caller()
        
    def getAvailableDevices(self):
        """List all available input devices."""
        devs = self.inputdevice.getAvailableDevices()
        #approved_devs = []
        for dev in devs:
            self._available_devices[dev["name"]] = dev["id"]
            #approved_devs.append(dev)
        return devs 
        
    def _toggle(self,flag):
        flag ^= 1
        return flag
    
    def _increment_ref_value(self):
        if self._pid_flag:
            self._pid_ref = min(self._pid_ref+1, self._max_pid_ref)
        else:
            self._pow = min(self._pow+1, self._max_pow)
        
    def _decrement_ref_value(self):
        if self._pid_flag:
            self._pid_ref = max(self._pid_ref-1, self._min_pid_ref)
        else:
            self._pow = max(self._pow-1, self._min_pow)
        
    def readRawValues(self):
        """ Read raw values from the input device."""
        return self.inputdevice.readRawValues()
        
    def start_input(self, device_name):
        """
        Start reading input from the device with name device_name using config
        config_name
        """
        try:
            device_id = self._available_devices[device_name]
            self.inputdevice.start_input(device_id)
            self._read_timer.start()
        except Exception:
            print "Error while opening/initializing  input device"
            logger.warning("Error while opening/initializing  input device\n\n%s" %
                     (traceback.format_exc()))
                 
    def stop_input(self):
        """Stop reading from the input device."""
        self._read_timer.stop()
        
    def read_input(self):
        """Read input data from the selected device"""        
        try:
            # print self.inputdevice.readRawValues()
            data = self.inputdevice.read_input()
            self.roll = data['axis'][2]
            self.pitch = data['axis'][3]
            self.yaw = data['axis'][0]
            self.throttle = data['axis'][1]

            # print data
            # print self.throttle
            # print self.yaw

            vl = data["vl"]
            vr = data["vr"]
            toggle_pid = data["toggle_pid"]
            increment_ref = data["increment_ref"]
            decrement_ref = data["decrement_ref"]
            
            if self._pid_flag:
                vl = data["vl"] * self._pid_ref
                vr = data["vr"] * self._pid_ref
            else:
                vl = data["vl"] * self._pow
                vr = data["vr"] * self._pow
            
            # We want to toggle when we press the button.
            if self._old_increment_ref < increment_ref:
                self._increment_ref_value()
            self._old_increment_ref = increment_ref
                
            if self._old_decrement_ref < decrement_ref:
                self._decrement_ref_value()
            self._old_decrement_ref = decrement_ref
            
            if self._old_toggle_pid < toggle_pid:
                self._pid_flag = self._toggle(self._pid_flag)
            self._old_toggle_pid = toggle_pid

            # If this comparison is not done and data always sent, the NXT receive buffer is filled quickly.
            #if (self.old_vl != vl or self.old_vr != vr):
            self.input_updated.call(vl, vr)
            self.old_vl = vl
            self.old_vr = vr
        except Exception:
            print "Exception while reading inputdevice"
            logger.warning("Exception while reading inputdevice: %s",
                           traceback.format_exc())
            self._read_timer.stop()
        
                     
if __name__ == "__main__":
    import time
    import os
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    logging.basicConfig(level=logging.DEBUG)
    
    class VelocityPrinter:
        def __init__(self):
            self.old_vl = 0
            self.old_vr = 0
        
        def printVelocities(self, vl,vr):
            if (self.old_vl != vl or self.old_vr != vr):
                print "vl: ", vl, " vr: ", vr
                self.old_vl = vl
                self.old_vr = vr
            
    vp = VelocityPrinter()

    jr = JoystickReader()    
    jr.input_updated.add_callback(vp.printVelocities)
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
            print k
            print jr.yaw
            print jr.throttle
            print jr.roll
            print jr.pitch
            k += 1
            time.sleep(0.2)
    else:
        print "No available devices. Exiting."                             