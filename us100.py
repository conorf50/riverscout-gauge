import utime
import machine
# Based on code from Kai Fricke, available here:
# https://github.com/kfricke/micropython-us100

class US100UART:
    """Read the US-100 sonar sensor in UART mode."""

    def __init__(self, uart):
        self.uart = uart
        uart = machine.UART(1, baudrate=9600)

        utime.sleep_ms(100)
        self.buf = bytearray(2)
        self.t = 0

    def distance(self):
        """Read the temperature compensated distance im millimeters."""
        #print("polling sensor")
        self.buf[0] = 0
        self.buf[1] = 0
        self.uart.write(b'\x55')
        #print("bytes written, wait for output")    
        self.t = utime.ticks_ms()
        while not self.uart.any():
            #print("cannot connect to sensor")
            if utime.ticks_diff(utime.ticks_ms(), self.t) > 100:
                raise Exception('Timeout while reading from US100 sensor!')
            utime.sleep_us(100)
        #print("reading output")    
        self.uart.readinto(self.buf, 2)
        #print("returning")
        return (self.buf[0] * 256) + self.buf[1]

    def temperature(self):
        """Read the temperature in degree celcius."""
        self.buf[0] = 0
        self.uart.write(b'\x50')
        self.t = utime.ticks_ms()
        while not self.uart.any():
            if utime.ticks_diff(utime.ticks_ms(), self.t) > 100:
                raise Exception('Timeout while reading from US100 sensor!')
            utime.sleep_us(100)
        self.uart.readinto(self.buf, 1)
        return self.buf[0] - 45