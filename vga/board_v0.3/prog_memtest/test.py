import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))

import collections
import functools
import random
import time

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
    ss.write(1)
    sck.write(0)
    # sck.write(1)
    # sck.write(0)
    time.sleep(0.01)
    ss.write(0)
    time.sleep(0.01)

    def sendAll(l):
        rtn = 0
        for b in l:
            mosi.write(b)
            sck.write(1)
            v = miso.read()
            rtn = (rtn << 1) + v
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

    def _readmem(cmd, addr):
        """
        time -1: "cmd" mosi is 0b11, miso is [prev]; fpga changes to READMEM
        time 0: "ad0" mosi is addr[0], miso is X; fpga clocks in byte 0
        time 1: "ad1" mosi is addr[1], miso is X; fpga clocks in byte 1
        time 2: "ad2" mosi is addr[2], miso is X; fpga clocks in byte 2
        time 3: "ad3" mosi is addr[3], miso is X; fpga clocks in byte 3
        time 4: "dm0" mosi is X, miso is X; fpga submits command
        time 5: "dm1" mosi is X, miso is ack; fpga reads status
        time 6: "dm2" mosi is X, miso is status; fpga reads data[0]
        time 7: "bt0" mosi is X, miso is data[0]; fpga reads data[1]
        time 8: "bt1" mosi is X, miso is data[1]; fpga reads data[2]
        time 9: "bt2" mosi is X, miso is data[2]; fpga reads data[3], pops the read word, goes to IDLE
        time 10: "bt3" mosi is 0, miso is data[3]; fpga interprets as IDLE command
        """

        sendAll(cmd) # command

        sendAll([(addr >> i) & 1 for i in xrange(31, 23, -1)]) # addr (BE)
        sendAll([(addr >> i) & 1 for i in xrange(23, 15, -1)]) # addr (BE)
        sendAll([(addr >> i) & 1 for i in xrange(15, 7, -1)]) # addr (BE)
        sendAll([(addr >> i) & 1 for i in xrange(7, -1, -1)]) # addr (BE)

        sendAll([0,0,0,0,0,0,0,0]) # dummy (command being submitted)
        ack = sendAll([0,0,0,0,0,0,0,0]) # dummy (read latency)
        assert ack == 0b10101010
        diag = sendAll([0,0,0,0,0,0,0,0]) # diagnostics
        assert diag == 0b00000100, bin(diag) # 1 byte in the read fifo, no errors

        b0 = sendAll([0,0,0,0,0,0,0,0]) # byte 0 (BE)
        b1 = sendAll([0,0,0,0,0,0,0,0]) # byte 1 (BE)
        b2 = sendAll([0,0,0,0,0,0,0,0]) # byte 2 (BE)
        b3 = sendAll([0,0,0,0,0,0,0,0]) # byte 3 (BE) [IDLE command]
        return (b0 << 24) + (b1 << 16) + (b2 << 8) + (b3)

    readmem1 = functools.partial(_readmem, [0,0,0,0,0,0,1,1])
    readmem3 = functools.partial(_readmem, [0,0,0,0,0,1,0,1])

    def _writemem(cmd, addr, data):
        # print
        # print "writemem", addr, data
        r = sendAll(cmd) # command
        assert r == 0, hex(r)

        r = sendAll([(data >> i) & 1 for i in xrange(31, 23, -1)]) # data (BE)
        assert r == 0, hex(r)
        r = sendAll([(data >> i) & 1 for i in xrange(23, 15, -1)]) # data (BE)
        assert r == 0, hex(r)
        r = sendAll([(data >> i) & 1 for i in xrange(15, 7, -1)]) # data (BE)
        assert r == 1, hex(r)
        r = sendAll([(data >> i) & 1 for i in xrange(7, -1, -1)]) # data (BE)
        assert r == 2, hex(r)

        r = sendAll([(addr >> i) & 1 for i in xrange(31, 23, -1)]) # addr (BE)
        assert r == 3, hex(r)
        r = sendAll([(addr >> i) & 1 for i in xrange(23, 15, -1)]) # addr (BE)
        assert r == 0, hex(r)
        r = sendAll([(addr >> i) & 1 for i in xrange(15, 7, -1)]) # addr (BE)
        assert r == 0b00000100, hex(r)
        r = sendAll([(addr >> i) & 1 for i in xrange(7, -1, -1)]) # addr (BE)
        assert r == 6, hex(r)

        r = sendAll([0,0,0,0,0,0,0,0]) # dummy (for command)
        assert r == 7, hex(r)
        ack = sendAll([0,0,0,0,0,0,0,0]) # dummy (for write latency)
        assert ack == 0b10101010, ack
        diag = sendAll([0,0,0,0,0,0,0,0]) # extra IDLE command to clock out last byte
        assert diag == 0b00000000 # no bytes in the write fifo, no errors

    writemem1 = functools.partial(_writemem, [0,0,0,0,0,1,0,0])
    writemem3 = functools.partial(_writemem, [0,0,0,0,0,1,1,0])

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

    readmem, writemem = readmem1, writemem1
    readmem, writemem = readmem3, writemem3

    def check(l):
        for i in l:
            print "writing", i
            writemem(i, i)
        for i in l:
            print "checking", i
            v = readmem(i)
            assert v == i, (hex(i), hex(v))

    check(range(0, 32, 8))

    def determine_size():
        for i in xrange(31, 1, -1):
            addr = 2**i
            writemem(addr, addr)
        return readmem(0)
    print "memory size: %.1fMB" % (determine_size() * 0.5**20)

    # for i in xrange(16, 31):
        # base = (2 ** i)
        # check(range(base, base + 32, 4))

    for i in xrange(100):
        val = random.randrange(0, 1<<32)
        val &= ~3

        addrs = [val]
        for i in xrange(2, 24):
            addrs.append(val ^ (1 << i))
        check(addrs)

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
