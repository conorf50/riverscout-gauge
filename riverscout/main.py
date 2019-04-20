# based on Pycom example here:
# https://github.com/pycom/pycom-libraries/blob/master/examples/sigfoxUplink/main.py
from network import Sigfox
import socket
import struct
import sys
# init Sigfox for RCZ1 (Europe)
sigfox = Sigfox(mode=Sigfox.SIGFOX, rcz=Sigfox.RCZ1)

# # create a Sigfox socket
s = socket.socket(socket.AF_SIGFOX, socket.SOCK_RAW)

# # make the socket blocking
s.setblocking(True)

# # configure it as uplink only
s.setsockopt(socket.SOL_SIGFOX, socket.SO_RX, False)
 
try:
    print("sending data")
    # 'f' = float value, 'i' = unsigned integer
    #s.send(struct.pack('f',float(12.3)) + struct.pack('i', int(1020)))
    s.send(struct.pack('f',float(34.134)) + bytes([12]))
except Exception:
    print(Exception)    
    sys.exit(0)