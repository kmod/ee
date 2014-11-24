import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))

import time
time

from hub.jtagusaur_bitbang import Jtagusaur2BitbangController

def main():
    ctlr = Jtagusaur2BitbangController(1000000)

    miso = ctlr.B4
    mosi = ctlr.B3
    sck = ctlr.B5
    ss = ctlr.B2

    miso.mode('i')
    mosi.mode('o')
    sck.mode('o')
    ss.mode('o')
    sck.write(0)
    ss.write(0)
    time.sleep(.1)
    ss.write(1)
    time.sleep(.1)
    ss.write(0)

    def sendAll(l):
        rtn = []
        for b in l:
            mosi.write(b)
            sck.write(1)
            v = miso.read()
            rtn.append(v)
            sck.write(0)
        return rtn

    def read(idx):
        print
        print "read", idx
        print sendAll([0,0,0,0,0,0,0,1])
        byte = idx
        print sendAll([(byte >> (7-i)) & 1 for i in xrange(8)])
        r = sendAll([0,0,0,0,0,0,0,0])
        print r
        t = 0
        for b in r:
            t = (t << 1) + b
        return t

    def write(port, val):
        print
        print "write", port, val
        assert 0 <= port < 128
        assert val in (0, 1)

        print sendAll([0,0,0,0,0,0,1,0])
        byte = (port << 1) + val
        print sendAll([(byte >> (7-i)) & 1 for i in xrange(8)])
        print sendAll([0,0,0,0,0,0,0,0])

    print read(0)

    LED_REGS = [0, 1, 2]
    while True:
        for r in LED_REGS:
            write(r, 1)
        print read(0)
        for r in LED_REGS:
            write(r, 0)
        print read(0)

if __name__ == "__main__":
    main()
