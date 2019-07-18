
# Riverscout - A distributed envrionmental monitoring system

This README provides info on the device section of Riverscout, my final year college project. For the other half of the project that handles data collection, processing and access, please visit [the server repo](https://github.com/conorf50/riverscout-server)


For a more in-depth overview of the project, refer to the report in the backend server repo. This goes into detail behind the design choices of the project.

Riverscout uses a [Pycom SiPy](https://pycom.io/product/sipy/) with a [US-100 ultrasonic sensor](https://www.adafruit.com/product/4019) and a DS18B20 temperature sensor. The SiPy is a internet enabled microcontroller that connects to the Sigfox network and can be programmed using a specialized variant of Python called MicroPython.

The SiPy runs on an Espressif ESP32 SOC and offers the following hardware (adapted from official spec sheet):
* 32 bit CPU
* Multi thread support through MicroPython
* Separate low power co-processor to handle deep sleep
* Multiple interfaces (I2C, SPI, UART, DAC, ADC)
* Built in support for Wifi and Bluetooth and Sigfox.

For a full list of specifications, refer to [the official datasheet](https://pycom.io/wp-content/uploads/2018/08/sipy-specsheet.pdf)


**Note about demo code** 

The demo code differs slightly from the main code in that it uses a potentiometer in place of the ultrasonic sensor because of a bug with the serial port of the SiPy. This occurs in multiple revisions of the device firmware and causes the SiPy to hang while sending a Sigfox message with the serial port connected.
It may be related to [this issue](https://forum.pycom.io/topic/2607/socket-send-stops-working-sigfox).

### LPWAN Introduction
For applications with a tight power budget or only a need for a small message size, using normal protocols like 3G and 4G is not recommended. Special protocols have been developed to fill this need such as: LoRa, Sigfox,  LTE-M and Narrowband IoT. All of these differ in implementation but the end goal is the same.

These systems are not designed for constant high bandwidth applications but instead are more suited to sensor networks where a small amount of data gets transferred infrequently in set intervals.

[![tech.png](https://i.postimg.cc/zDS1qvkK/tech.png)](https://postimg.cc/7b6RVxdZ)
##### Source: Vodafone Business whitepaper: “Narrowband-IoT: pushing the boundaries of IoT” available at https://www.vodafone.com/business/iot/managed-iot-connectivity/nb-iot


For a better look at the protocol, refer to [this video](https://www.youtube.com/watch?v=_aTzrOxIroY)


### Sensors Used
#### US-100
The US-100 is an ultrasonic distance sensor that measures distance by emitting 40kHz pulses and measuring the time it takes to detect them reflecting back.
It has a range of between 20 to 450 cm, however it loses accuracy after 250cm. 

It runs on between 3 and 5 V DC and is easy to interface with the SiPy. The sensor is an improved version of the ‘HC-SR04’, a popular choice in hobby projects. I chose the US-100 over the SR04 because of its serial mode, built in thermal compensation and 3.3v operation4. By connecting the jumper pins on the rear of the sensor, it sends the measurements over a standard UART interface @ 9600 baud which I thought could be handled more easily than the trigger / echo pins. 

Also performing the distance calculations independently allows the main microcontroller to perform other tasks while the US-100 is calculating the distance.


To use the sensor, send ```0x55``` for a distance measurement (or ```0x50``` for a temperature measurement).
The distance response will come back in two bytes. To get the distance ```D``` in mm:

``` D = MSB ∗ 256 + LSB```

where ```MSB``` = Most Significant Bit, ```LSB``` = Least Significant Bit

To get the temperature from the sensor (not used in this project) subtract 45 from the byte value that comes back 3.


#### DS18B20

The DS18B20 is a low-cost temperature sensor that uses the OneWire protocol. I chose this sensor because of its popularity and low cost. It operates between -55and +125on a supply of 3 to 5 volts 1.

To operate this sensor, I used the libraries provided by Pycom available [on their Github](https://github.com/pycom/pycom-libraries/tree/master/examples/DS18X20). This meant I did not have to write a OneWire driver from scratch and instead rely on an existing solution. The code to get a value from the sensor is as follows:

```
ow = OneWire(Pin('P8')) // init the Onewire bus on pin 8
temp = DS18X20(ow) // init the sensor class

# round the result value to two decimal places
waterTemp = round(temp.read_temp_async(), 2) // read the value
print(float(waterTemp)) // print to console
```

### Code Overview

The SiPy runs code written in Micropython which is an embedded derivative of CPython (standard Python). Micropython aims to provide most of the features of Python 3, with some differences that are documented here: https://docs.micropython.org/en/latest/genrst/index.html

The SiPy runs Pycom’s own Micropython distribution. When powered on, the interpreter will look for a file called ```boot.py``` If this does not exist, the board will not be able to connect to the computer via serial. A boot file is provided as standard so it is not necessary to provide it (unless modifications need to be made).
The boot file sets up the serial terminal and specifies the main code file (usually called ```main.py```). It runs on device startup similar to a ```main.c``` file in C/Arduino/conventional microcontrollers. Its purpose is to perform board initialization and point to the main file.

The other important file is ```main.py```. This is where most of the processing gets done.

In the Riverscout project, there are a number of other files
* ```onewire.py ``` : Provided by Pycom, this library provides a Onewire bus driver to interface with the temperature sensor as well as functions to get data from it.
* ```us100.py``` : This is a driver for the ultrasonic sensor.

##### ```main.py```
This is the main file that runs on the microcontroller after ```boot.py``` . It performs the following tasks:
* Import all other files and libraries for the project
* Set up the interfaces
* Runs an infinite loop to poll the sensors, send the data to Sigfox and wait for a set amount of time before polling again

##### ```us100.py```
This provides helper functions that abstract the process of polling the sensor for data. These functions are:
* distance() = returns the distance in millimeters
* temperature() = returns the temperature in ℃

##### ```onewire.py``` 
Provides a driver for the Onewire bus and the ```read_temp_async``` function to interface with the temperature sensor. This is provided by Pycom and contains no code written by myself.

Refer to the comments in the source code for a detailed explanation.

### Schematics


| Sensor | Pin | Connection (SiPy)| Connection (Expansion Board)|
| ----   | ---- | -----| ----- |
| DS18B20 |Data| Pin 8| G15|
| US-100 | TX | Pin 4| G24|
| US-100 | RX| Pin 3| G11|
### Data Compression Scheme

In order to reach the constrained 12 byte (96 bit) message limit of Sigfox and remain reasonably accurate,  the system needs to be able to compress data so that as little information is lost as possible. Also for power saving reasons, we would like the message size to be as short as possible. The compression scheme is as follows:

* Bytes 0 to 4 : 32-bit float value, little endian
* Byte 5: 8-bit unsigned integer

Extra space is not padded - some devices will pad out the remaining bytes to get a full 96 bit message

The Micropython code for compressing the data is below:

```struct.pack('f',float(waterTemp)) + bytes([waterLevel])```