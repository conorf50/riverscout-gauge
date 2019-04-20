'''
Riverscout Device Code.
Author:  Conor Farrell (+ others where noted)


Sigfox parts based on Pycom example here:
https://github.com/pycom/pycom-libraries/blob/master/examples/sigfoxUplink/main.py

DS18X20 code from Pycom available here:
https://github.com/pycom/pycom-libraries/tree/master/examples/DS18X20

Struct function for data compression based on code from Austin Spivey/Wia.io available here:
https://dzone.com/articles/build-an-end-to-end-sigfox-gps-tracker-using-wia-a

US100 distance sensor code forked from Kai Fricke (https://github.com/kfricke/) and adapted to Pycom by myself
Modified code available at: https://github.com/conorf50/pycom-us100
'''

from network import Sigfox # sigfox libs
import time 
from machine import Pin # listings for device pins
from onewire import DS18X20 # driver for the temperature sensor
from onewire import OneWire # onewire driver for DS18B20 driver above
import socket # sigfox
import struct # compression of float values

# init Sigfox for RCZ1 (Europe)
sigfox = Sigfox(mode=Sigfox.SIGFOX, rcz=Sigfox.RCZ1)
# create a Sigfox socket
s = socket.socket(socket.AF_SIGFOX, socket.SOCK_RAW)
# make the socket blocking
s.setblocking(True)
# configure it as uplink only
s.setsockopt(socket.SOL_SIGFOX, socket.SO_RX, False)

#DS18B20 temp sensor data line (yellow wire) connected to pin P8 (G15 on Expansion Board)
ow = OneWire(Pin('P8'))
# temp = DS18X20(ow) 
# temp.start_conversion()
# time.sleep(1)
# temp = round(temp.read_temp_async(), 2)

# print("Temp =")
# print(float(temp))
# time.sleep(1)
# # 'f' = float value

print("sending data")
    # 'f' = float value, 'i' = unsigned integer
    #s.send(struct.pack('f',float(12.3)) + struct.pack('i', int(1020)))
s.send(struct.pack('f',float(34.1)) + bytes([12]))