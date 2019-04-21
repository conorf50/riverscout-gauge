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
from machine import UART
import utime
import us100
import pycom
from machine import Pin # listings for device pins
from machine import ADC # 'substitute' for a temp sensor by using a pot connected to the ADC
from onewire import DS18X20 # driver for the temperature sensor
from onewire import OneWire # onewire driver for DS18B20 driver above
import socket # sigfox
import struct # compression of float values
import gc
# garbage collection
gc.enable()

# init Sigfox for RCZ1 (Europe)
sigfox = Sigfox(mode=Sigfox.SIGFOX, rcz=Sigfox.RCZ1)
# create a Sigfox socket
s = socket.socket(socket.AF_SIGFOX, socket.SOCK_RAW)
# make the socket blocking
s.setblocking(False)
# configure it as uplink only
s.setsockopt(socket.SOL_SIGFOX, socket.SO_RX, False)

# init the ADC
#adc = ADC(0)
# set up the ADC on pin 13 with an 11db attenuation factor 
# this means the max value will be 4095 at 3.3v
#adc_c = adc.channel(pin='P13', attn=ADC.ATTN_11DB)


# The SiPy has two serial ports, one is used to communicate with the computer
# the second is used here

# Configure second UART bus on pins P3(TX1) and P4(RX1). Refer to datasheet if in doubt
uart1 = machine.UART(1, baudrate=9600)
sensor = us100.US100UART(uart1)

print("Free memory pre sensor reading")
print(str(gc.mem_free()))
#DS18B20 temp sensor data line (yellow wire) connected to pin P8 (G15 on Expansion Board)
ow = OneWire(Pin('P8')) # breaks Sigfox connectivity
temp = DS18X20(ow) 
temp.start_conversion()
time.sleep(1)
temp = round(temp.read_temp_async(), 2)
print("Free memory post sensor reading")
print(str(gc.mem_free()))
gc.collect()
print("Free memory post gc")
print(str(gc.mem_free()))
# take the value from the ADC, divide it by 100 to get a float value and round this to two decimal places
#tempVal = round(adc_c.value()/100, 2)

# get the distance in millimeters from the sensor
waterLevel = sensor.distance()

print("Temp =")
# #print(tempVal) # scale the value down to a more realistic level
print(float(temp))
print("Water Level = ")
print(sensor.distance())
# # 'f' = float value
#adc.deinit()
print("sending data")
gc.collect()
print("Free memory after data collcted")
print(str(gc.mem_free()))
    # 'f' = float value, 'i' = unsigned integer
    #s.send(struct.pack('f',float(12.3)) + struct.pack('i', int(1020)))
try:
    s.send(struct.pack('f',float(temp)) + bytes([123]))
except Exception as error:
    print("unable to send data" + str(error))
    
