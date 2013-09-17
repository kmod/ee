import readline # just importing this activates the module
readline # "reference" it to surpress pyflakes errors

import serial # pip install pyserial
import sys
import threading
import time

from controller import Controller

ctlr = Controller()

def on_read(c):
    sys.stdout.write("\033[34m%02x\033[0m\n" % ord(c))
    sys.stdout.flush()
ctlr.on_read.append(on_read)

while True:
    l = raw_input()
    if not l.strip():
        continue
    tokens = l.split()
    cmd, args = tokens[0], tokens[1:]

    if cmd == "mode":
        port, mode = args
        port = int(port)
        ctlr.pinMode(port, mode)
        continue
    elif cmd == "set":
        port, val = map(int, args)
        ctlr.digitalWrite(port, val)
        continue
    elif cmd == "read":
        port, = map(int, args)
        ctlr.digitalRead(port)
        continue

    print "Unknown command!"
