# -*- coding: utf-8 -*-
"""
Driver for reading data from the PySDL2 API. Used from Inpyt.py for reading input data.
"""

import sdl2
import sdl2.ext
import sdl2.hints

class PySDL2Reader():
    """Used for reading data from input devices using the PySDL2 API."""
    def __init__(self):
        sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO | sdl2.SDL_INIT_JOYSTICK)
        sdl2.SDL_SetHint(sdl2.hints.SDL_HINT_JOYSTICK_ALLOW_BACKGROUND_EVENTS, "1")
        sdl2.ext.init()

    def start_input(self, deviceId):
        """Initalize the reading and open the device with deviceId"""
        self.data = {"vl":0.0, "vr":0.0, "toggle_pid":0, "increment_ref": 0, "decrement_ref":0, "axis":{0:0, 1:0, 2:0, 3:0}}
        self.j = sdl2.SDL_JoystickOpen(deviceId)

    def read_input(self):
        """Read input from the selected device. Modify this to fit your needs."""
        for event in sdl2.ext.get_events():

            # rawaxis = {}
            if event.type == sdl2.SDL_JOYAXISMOTION:
                self.data['axis'][event.jaxis.axis] = event.jaxis.value #/ 32767.0

            if event.type == sdl2.SDL_JOYBUTTONDOWN:
                try:
                    if event.jbutton.button == 8:
                        self.data["toggle_pid"] = 1
                    elif event.jbutton.button == 3:
                        self.data["increment_ref"] = 1
                    elif event.jbutton.button == 2:
                        self.data["decrement_ref"] = 1
                except Exception:
                    # Button not mapped, ignore..
                    pass
            
            if event.type == sdl2.SDL_JOYBUTTONUP:
                try:
                    if event.jbutton.button == 8:
                        self.data["toggle_pid"] = 0
                    elif event.jbutton.button == 3:
                        self.data["increment_ref"] = 0
                    elif event.jbutton.button == 2:
                        self.data["decrement_ref"] = 0
                except Exception:
                    # Button not mapped, ignore..
                    pass
            
            if event.type == sdl2.SDL_JOYHATMOTION:
            #index = "Input.HAT-%d" % event.jhat.hat
                try:
                    if event.jhat.value == sdl2.SDL_HAT_CENTERED:
                        self.data["vl"] = 0.0
                        self.data["vr"] = 0.0
                    elif event.jhat.value == sdl2.SDL_HAT_UP:
                        self.data["vl"] = 1.0
                        self.data["vr"] = 1.0
                    elif event.jhat.value == sdl2.SDL_HAT_DOWN:
                        self.data["vl"] = -1.0
                        self.data["vr"] = -1.0
                    elif event.jhat.value == sdl2.SDL_HAT_LEFT:
                        self.data["vl"] = -1.0
                        self.data["vr"] = 1.0
                    elif event.jhat.value == sdl2.SDL_HAT_RIGHT:
                        self.data["vl"] = 1.0
                        self.data["vr"] = -1.0
                    elif event.jhat.value == sdl2.SDL_HAT_LEFTUP:
                        self.data["vl"] = 0.5
                        self.data["vr"] = 1.0
                    elif event.jhat.value == sdl2.SDL_HAT_LEFTDOWN:
                        self.data["vl"] = 0.0
                        self.data["vr"] = 0.0
                    elif event.jhat.value == sdl2.SDL_HAT_RIGHTUP:
                        self.data["vl"] = 1.0
                        self.data["vr"] = 0.5
                    elif event.jhat.value == sdl2.SDL_HAT_RIGHTDOWN:
                        self.data["vl"] = 0.0
                        self.data["vr"] = 0.0
                except Exception:
                    # Hat not mapped, ignore..
                    pass
        return self.data
        
    def readRawValues(self):
        """Read out the raw values from the device"""
        rawaxis = {}
        rawbutton = {}

        for event in sdl2.ext.get_events():
            if event.type == sdl2.SDL_JOYBUTTONDOWN:
                rawbutton[event.jbutton.button] = 1
            if event.type == sdl2.SDL_JOYBUTTONUP:
                rawbutton[event.jbutton.button] = 0
            if event.type == sdl2.SDL_JOYAXISMOTION:
                rawaxis[event.jaxis.axis] = event.jaxis.value / 32767.0
            if event.type == sdl2.SDL_JOYHATMOTION:
                if event.jhat.value == sdl2.SDL_HAT_CENTERED:
                    rawbutton[21] = 0
                    rawbutton[22] = 0
                    rawbutton[23] = 0
                    rawbutton[24] = 0
                    rawbutton[25] = 0
                    rawbutton[26] = 0
                    rawbutton[27] = 0
                    rawbutton[28] = 0
                elif event.jhat.value == sdl2.SDL_HAT_UP:
                    rawbutton[21] = 1
                elif event.jhat.value == sdl2.SDL_HAT_DOWN:
                    rawbutton[22] = 1
                elif event.jhat.value == sdl2.SDL_HAT_LEFT:
                    rawbutton[23] = 1
                elif event.jhat.value == sdl2.SDL_HAT_RIGHT:
                    rawbutton[24] = 1
                elif event.jhat.value == sdl2.SDL_HAT_LEFTUP:
                    rawbutton[25] = 1
                elif event.jhat.value == sdl2.SDL_HAT_LEFTDOWN:
                    rawbutton[26] = 1
                elif event.jhat.value == sdl2.SDL_HAT_RIGHTUP:
                    rawbutton[27] = 1
                elif event.jhat.value == sdl2.SDL_HAT_RIGHTDOWN:
                    rawbutton[28] = 1
        return [rawaxis, rawbutton]

    def getAvailableDevices(self):
        """List all the available devices."""
        dev = []
        names = []
        if hasattr(self, 'j') and sdl2.joystick.SDL_JoystickGetAttached(self.j):
            sdl2.joystick.SDL_JoystickClose(self.j)

        nbrOfInputs = sdl2.joystick.SDL_NumJoysticks()
        for i in range(0, nbrOfInputs):
            j = sdl2.joystick.SDL_JoystickOpen(i)
            name = sdl2.joystick.SDL_JoystickName(j)
            if names.count(name) > 0:
                name = "{0} #{1}".format(name, names.count(name) + 1)
            dev.append({"id":i, "name" : name})
            names.append(name)
            sdl2.joystick.SDL_JoystickClose(j)
        return dev        

if __name__ == "__main__":
    """ A little test of the PySDL2Reader class """
    import time
    import os
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    
    EnableLoop = True
    j = PySDL2Reader()
    dev = j.getAvailableDevices()
    if dev:
        num = len(dev)
        idx = 0
        if num>1:
            print "There are ", num, " joysticks connected. Choose which one you would like to use."
            for device in dev:
                print device
            try:
                idx = int(raw_input('id:'))
            except ValueError:
                print "Not a number"
                
        print dev[idx]['name'], " test. Press button 10 to exit."
        j.start_input(dev[idx]['id'])
        while EnableLoop:
            #j.read_input()
            [rawaxis, rawbutton] = j.readRawValues()
            if rawbutton:
                print rawbutton
                if 9 in rawbutton:
                    if rawbutton[9]:
                        EnableLoop = False
                        print "Button 10 pressed. Exiting."
            if rawaxis:
                print rawaxis
            time.sleep(0.02)
    else:
        print "No available devices. Exiting."
        