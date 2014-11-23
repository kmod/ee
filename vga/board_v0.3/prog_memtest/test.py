import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))

import time

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
    ss.write(1)
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
        print sendAll([0,0,0,0,0,0,0,1])
        print sendAll([(idx >> (7-i)) & 1 for i in xrange(8)])
        print sendAll([0,0,0,0,0,0,0,0])

    def write(port, val):
        print
        assert 0 <= port < 128
        assert val in (0, 1)

        print sendAll([0,0,0,0,0,0,1,0])
        byte = (port << 1) + val
        print bin(byte)
        print sendAll([(byte >> (7-i)) & 1 for i in xrange(8)])
        print sendAll([0,0,0,0,0,0,0,0])

    read(0)

    while True:
        write(4, 0)
        write(5, 0)
        write(6, 0)
        write(4, 1)
        write(5, 1)
        write(6, 1)

if __name__ == "__main__":
    main()
