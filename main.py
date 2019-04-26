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

This code has been modified for a demonstration so it uses the RGB LED on the board to signify different states 
of operation. Also because of a bug with UART and the Sigfox stack, this code expects a 
potentiometer to be connected to pin 13 (G5 on Expansion Board) to act as a substitute for 
a water level sensor.

'''
from network import Sigfox # sigfox libs
import time 
#from machine import UART # broken on this firmware revision
import utime
#import us100
import pycom
from machine import Pin # listings for device pins
from machine import ADC # 'substitute' for a temp sensor by using a pot connected to the ADC
import pycom # control the RGB led
from onewire import DS18X20 # driver for the temperature sensor
from onewire import OneWire # onewire driver for DS18B20 driver above
import socket # sigfox
import struct # compression of float values

delayVal = 60 # delay in seconds between sensor polling + sending

pycom.heartbeat(False) # disable the heartbeat to change the LED colour


# init Sigfox for RCZ1 (Europe)
sigfox = Sigfox(mode=Sigfox.SIGFOX, rcz=Sigfox.RCZ1)
# create a Sigfox socket
s = socket.socket(socket.AF_SIGFOX, socket.SOCK_RAW)
# make the socket blocking, will cause the board to wait until send is successful
s.setblocking(True)
# configure it as uplink only
s.setsockopt(socket.SOL_SIGFOX, socket.SO_RX, False)


# The SiPy has two serial ports, one is used to communicate with the computer
# the second is used here

# Configure second UART bus on pins P3(TX1) and P4(RX1). Refer to datasheet if in doubt
# uart1 = machine.UART(1, baudrate=9600)
# sensor = us100.US100UART(uart1)

#init the ADC
adc = ADC(0)
#set up the ADC on pin 13 with an 11db attenuation factor 
#this means the max value will be 4095 at 3.3v
adc_c = adc.channel(pin='P13', attn=ADC.ATTN_11DB)



#DS18B20 temp sensor data line (yellow wire) connected to pin P8 (G15 on Expansion Board)
ow = OneWire(Pin('P8')) # breaks Sigfox connectivity on some firmwares!
temp = DS18X20(ow) 

# # 'f' = float value

#s.send(struct.pack('f',float(12.3)) + struct.pack('i', int(1020)))
while True:
# run this in an infinite loop
    try:
        pycom.rgbled(0x220022) # set LED to purple
        temp.start_conversion() # poll the sensor
        time.sleep(1) # wait until sensor is ready
        
        # round the result value to two decimal places
        waterTemp = round(temp.read_temp_async(), 2)
        # take the value from the ADC, divide it by 100 to get a float value and round this to an integer
        waterLevel = round(adc_c.value()/100)

        print("Temp =")
        # #print(tempVal) # scale the value down to a more realistic level
        print(float(waterTemp))

        print("Water Level = " + str(waterLevel))
        pycom.rgbled(0x321000) # set LED to orange
        
        # 'f' = float value, 'i' = unsigned integer
        try:
            print("sending data")
            s.send(struct.pack('f',float(waterTemp)) + bytes([waterLevel]))
            pycom.rgbled(0x002000) # change LED to dim green colour
        except Exception as e:
            print("unable to send data" + str(e))

        print("waiting for %s seconds before reading again" % str(delayVal))
        pycom.rgbled(0x000002) # turn the LED to a dim blue  
        time.sleep(delayVal) # wait 30s before reading values again        
    except Exception as error:
        print("reading data failed" + str(error))
        break
    
