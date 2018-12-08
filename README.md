Joystick to PPM converter using using a pair of Arduino through RF
=========

## General
This is still work in progress. It aims to use an USB joystick connected to a Linux notebook acting as a Ground Control Station (GCS) as a remote control for ArduPilot compatible vehicles. 

## Hardware
All you need is a Linux computer, a Linux compatible Joystick, two Arduino board and a pair of NRF24L01 modules. Plug the Joystick into the computer. Connect the computer to one Arduino via USB. Connect each of the NRF24L01 modules to each Arduino and connect PIN 6 of the PPM generator to the PPM input of your ArduPilot device.

Arduino code is based on https://github.com/DzikuVx/ppm_encoder

The Python code for the joystick reader is based on https://github.com/bitcraze/crazyflie-clients-python

## TODOs
The project is still at a very early alpha-stage and does not have any warranty. Run it at your own risk.
