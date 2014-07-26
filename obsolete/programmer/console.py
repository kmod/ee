import readline

import re
import serial
import sys
import threading
import time

br = 115200
ser = serial.Serial("/dev/ttyUSB0", br, timeout=1)

def read_thread():
    while True:
        try:
            c = ser.read(1)
            if c:
                sys.stdout.write("\033[34m%02x\033[0m\n" % ord(c))
                sys.stdout.flush()
        except OSError:
            print
            print "OSError, assuming it's being programmed, waiting"
            time.sleep(6)
            print "starting"

t = threading.Thread(target=read_thread)
t.setDaemon(True)
t.start()

def reset():
    ser.write("s\x0d\x00")
    ser.flush()
    time.sleep(.1)
    ser.write("s\x0a\x01")
    ser.flush()
    time.sleep(.1)
    ser.write("s\x0a\x00")
    ser.flush()
    time.sleep(.1)

def send_bit(b):
    ser.write("s\x0d\x00") # SCK = 0
    ser.write("s\x0b" + chr(b)) # MOSI = b
    ser.write("s\x0d\x01") # SCK = 1
    ser.write('i\x0c')
    ser.flush()

def send_byte(b):
    for i in xrange(7, -1, -1):
        send_bit((b>>i)&1)
    ser.flush()

def init():
    reset()
    send_byte(0xac)
    send_byte(0x53)
    send_byte(0xff)
    ser.write('v')
    send_byte(0xff)

time.sleep(1)
init()
while True:
    l = raw_input()
    if not l.strip():
        continue
    tokens = l.split()
    cmd, args = tokens[0], tokens[1:]

    if cmd == "set":
        port, val = map(int, args)
        ser.write("s" + chr(port) + chr(val))
        ser.flush()
        continue
    elif cmd == "read":
        port, = map(int, args)
        ser.write("r" + chr(port))
        ser.flush()
        continue
    elif cmd == "init":
        init()
        continue
    elif cmd == "shift":
        ser.write("i\x03")
        ser.write("v")
        ser.flush()
        continue
    elif cmd == "sig":
        send_byte(0x30)
        send_byte(0x00)
        send_byte(0x00)
        send_byte(0x00)
        ser.write('v')

        send_byte(0x30)
        send_byte(0x00)
        send_byte(0x01)
        send_byte(0x00)
        ser.write('v')

        send_byte(0x30)
        send_byte(0x00)
        send_byte(0x02)
        send_byte(0x00)
        ser.write('v')
        ser.flush()
        continue
    elif cmd == "fuse":
        send_byte(0x50)
        send_byte(0x00)
        send_byte(0x00)
        send_byte(0x00)
        ser.write('v')

        send_byte(0x58)
        send_byte(0x08)
        send_byte(0x00)
        send_byte(0x00)
        ser.write('v')

        send_byte(0x50)
        send_byte(0x08)
        send_byte(0x00)
        send_byte(0x00)
        ser.write('v')
        ser.flush()
        continue
    elif cmd == "readprog":
        send_byte(0x20)
        send_byte(0x00)
        send_byte(int(args[0]))
        send_byte(0xff)
        ser.write('v')

        send_byte(0x28)
        send_byte(0x00)
        send_byte(int(args[0]))
        send_byte(0xff)
        ser.write('v')

        ser.flush()
        continue
    elif cmd == "writeprog":
        send_byte(0x40)
        send_byte(0x00)
        send_byte(0x00)
        send_byte(0xaa)

        send_byte(0x48)
        send_byte(0x00)
        send_byte(0x00)
        send_byte(0xaa)

        send_byte(0x4c)
        send_byte(0x00)
        send_byte(0x00)
        send_byte(0x00)
        ser.flush()
        continue
    elif cmd == "erase":
        send_byte(0xac)
        send_byte(0x80)
        send_byte(0x00)
        send_byte(0x00)
        ser.flush()
        continue

    print "Unknown command!"
