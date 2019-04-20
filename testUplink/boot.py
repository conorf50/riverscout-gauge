# standard startup script from Pycom
# source:https://github.com/pycom/pycom-libraries/blob/master/examples/sigfoxUplink/boot.py
from machine import UART
import machine
import os

uart = UART(0, baudrate=115200)
os.dupterm(uart)

machine.main('main.py')