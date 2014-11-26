import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))

import collections
import time
time

REGS = dict(
        led0=0,
        led1=1,
        led2=2,
        calib1_done=8,
        calib3_done=9,
        cmd_empty=10,
        cmd_full=11,
        wr_empty=12,
        wr_full=13,
        wr_underrun=14,
        wr_error=15,
        rd_empty=16,
        rd_full=17,
        rd_overflow=18,
        rd_error=19
        )
REGS = collections.namedtuple("Registers", REGS.keys())(**REGS)

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
        print "write", port, val
        assert 0 <= port < 128
        assert val in (0, 1)

        print sendAll([0,0,0,0,0,0,1,0])
        byte = (port << 1) + val
        print sendAll([(byte >> (7-i)) & 1 for i in xrange(8)])
        print sendAll([0,0,0,0,0,0,0,0])

    def readmem(addr):
        print
        print "readmem", addr
        print sendAll([0,0,0,0,0,0,1,1]) # command

        print sendAll([(addr >> i) & 1 for i in xrange(31, 23, -1)]) # addr (BE)
        print sendAll([(addr >> i) & 1 for i in xrange(23, 15, -1)]) # addr (BE)
        print sendAll([(addr >> i) & 1 for i in xrange(15, 7, -1)]) # addr (BE)
        print sendAll([(addr >> i) & 1 for i in xrange(7, -1, -1)]) # addr (BE)

        print sendAll([0,0,0,0,0,0,0,0]) # dummy (for command)
        print sendAll([0,0,0,0,0,0,0,0]) # dummy (for read latency)
        print sendAll([0,0,0,0,0,0,0,0]) # byte 0 (BE)
        print sendAll([0,0,0,0,0,0,0,0]) # byte 1 (BE)
        print sendAll([0,0,0,0,0,0,0,0]) # byte 2 (BE)
        print sendAll([0,0,0,0,0,0,0,0]) # byte 3 (BE)
        print sendAll([0,0,0,0,0,0,0,0]) # extra IDLE command to clock out last byte

        print sendAll([0,0,0,0,0,0,0,0]) # test
        print sendAll([0,0,0,0,0,0,0,0]) # test

    def writemem(addr, data):
        print
        print "writemem", addr, data
        print sendAll([0,0,0,0,0,1,0,0]) # command

        print sendAll([(data >> i) & 1 for i in xrange(31, 23, -1)]) # data (BE)
        print sendAll([(data >> i) & 1 for i in xrange(23, 15, -1)]) # data (BE)
        print sendAll([(data >> i) & 1 for i in xrange(15, 7, -1)]) # data (BE)
        print sendAll([(data >> i) & 1 for i in xrange(7, -1, -1)]) # data (BE)

        print sendAll([(addr >> i) & 1 for i in xrange(31, 23, -1)]) # addr (BE)
        print sendAll([(addr >> i) & 1 for i in xrange(23, 15, -1)]) # addr (BE)
        print sendAll([(addr >> i) & 1 for i in xrange(15, 7, -1)]) # addr (BE)
        print sendAll([(addr >> i) & 1 for i in xrange(7, -1, -1)]) # addr (BE)

        print sendAll([0,0,0,0,0,0,0,0]) # dummy (for command)
        print sendAll([0,0,0,0,0,0,0,0]) # dummy (for write latency)
        print sendAll([0,0,0,0,0,0,0,0]) # extra IDLE command to clock out last byte

        print sendAll([0,0,0,0,0,0,0,0]) # test
        print sendAll([0,0,0,0,0,0,0,0]) # test

    # print read(0)

    LED_REGS = [REGS.led0, REGS.led1, REGS.led2]


    # print read(REGS.calib1_done)
    # print read(REGS.calib3_done)
    # for k, v in REGS.__dict__.items():
        # print
        # print k
        # print read(v)
    # for i in xrange(16):
        # print i
        # print read(i)

    # readmem(0)
    # # readmem(1<<30)
    # writemem(0, 0x12345678)
    # readmem(0)
    # readmem(1)
    # readmem(2)
    # readmem(3)
    # readmem(4)

    for i in xrange(0, 1024, 4):
        writemem(i, i)
    for i in xrange(0, 1024, 4):
        readmem(i)

    """
    while True:
        for r in LED_REGS:
            write(r, 1)
        print read(0)
        for r in LED_REGS:
            write(r, 0)
        print read(0)
    """

if __name__ == "__main__":
    main()
