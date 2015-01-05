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

class Controller(object):
    def __init__(self):
        self.ctlr = Jtagusaur2BitbangController(1000000, 16)

        self.miso = self.ctlr.B4
        self.mosi = self.ctlr.B3
        self.sck = self.ctlr.B5
        self.ss = self.ctlr.B2

        self.miso.mode('i')
        self.mosi.mode('o')
        self.sck.mode('o')
        self.ss.mode('o')
        self.ss.write(1)
        self.sck.write(0)
        # self.sck.write(1)
        # self.sck.write(0)
        time.sleep(0.01)
        self.ss.write(0)
        time.sleep(0.01)

    def sendAll(self, l):
        rtn = 0
        for b in l:
            self.mosi.write(b)
            self.sck.write(1)
            v = self.miso.read()
            rtn = (rtn << 1) + v
            self.sck.write(0)
        return rtn

    def read(self, idx):
        # print "read", idx
        b = self.sendAll([0,0,0,0,0,0,0,1])
        assert b == 0
        byte = idx
        b = self.sendAll([(byte >> (7-i)) & 1 for i in xrange(8)])
        assert b == 0
        r = self.sendAll([0,0,0,0,0,0,0,0])
        return r

    def write(self, port, val):
        # print "write", port, val
        assert 0 <= port < 128
        assert val in (0, 1)

        b = self.sendAll([0,0,0,0,0,0,1,0])
        assert b == 0
        byte = (port << 1) + val
        b = self.sendAll([(byte >> (7-i)) & 1 for i in xrange(8)])
        assert b == 0
        b = self.sendAll([0,0,0,0,0,0,0,0])
        assert b == 0

    def _readmem(self, cmd, addr):
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

        self.sendAll(cmd) # command

        self.sendAll([(addr >> i) & 1 for i in xrange(31, 23, -1)]) # addr (BE)
        self.sendAll([(addr >> i) & 1 for i in xrange(23, 15, -1)]) # addr (BE)
        self.sendAll([(addr >> i) & 1 for i in xrange(15, 7, -1)]) # addr (BE)
        self.sendAll([(addr >> i) & 1 for i in xrange(7, -1, -1)]) # addr (BE)

        self.sendAll([0,0,0,0,0,0,0,0]) # dummy (command being submitted)
        ack = self.sendAll([0,0,0,0,0,0,0,0]) # dummy (read latency)
        assert ack == 0b10101010
        diag = self.sendAll([0,0,0,0,0,0,0,0]) # diagnostics
        assert diag == 0b00000100, bin(diag) # 1 byte in the read fifo, no errors

        b0 = self.sendAll([0,0,0,0,0,0,0,0]) # byte 0 (BE)
        b1 = self.sendAll([0,0,0,0,0,0,0,0]) # byte 1 (BE)
        b2 = self.sendAll([0,0,0,0,0,0,0,0]) # byte 2 (BE)
        b3 = self.sendAll([0,0,0,0,0,0,0,0]) # byte 3 (BE) [IDLE command]
        return (b0 << 24) + (b1 << 16) + (b2 << 8) + (b3)

    def _writemem(self, cmd, addr, data):
        # print
        # print "writemem", addr, data
        r = self.sendAll(cmd) # command
        assert r == 0, hex(r)

        r = self.sendAll([(data >> i) & 1 for i in xrange(31, 23, -1)]) # data (BE)
        assert r == 0, hex(r)
        r = self.sendAll([(data >> i) & 1 for i in xrange(23, 15, -1)]) # data (BE)
        assert r == 0, hex(r)
        r = self.sendAll([(data >> i) & 1 for i in xrange(15, 7, -1)]) # data (BE)
        assert r == 1, hex(r)
        r = self.sendAll([(data >> i) & 1 for i in xrange(7, -1, -1)]) # data (BE)
        assert r == 2, hex(r)

        r = self.sendAll([(addr >> i) & 1 for i in xrange(31, 23, -1)]) # addr (BE)
        assert r == 3, hex(r)
        r = self.sendAll([(addr >> i) & 1 for i in xrange(23, 15, -1)]) # addr (BE)
        assert r == 0, hex(r)
        r = self.sendAll([(addr >> i) & 1 for i in xrange(15, 7, -1)]) # addr (BE)
        assert r == 0b00000100, hex(r)
        r = self.sendAll([(addr >> i) & 1 for i in xrange(7, -1, -1)]) # addr (BE)
        assert r == 6, hex(r)

        r = self.sendAll([0,0,0,0,0,0,0,0]) # dummy (for command)
        assert r == 7, hex(r)
        ack = self.sendAll([0,0,0,0,0,0,0,0]) # dummy (for write latency)
        assert ack == 0b10101010, ack
        diag = self.sendAll([0,0,0,0,0,0,0,0]) # extra IDLE command to clock out last byte
        assert diag == 0b00000000, bin(diag) # no bytes in the write fifo, no errors

    def readmem1(self, addr):
        return self._readmem([0,0,0,0,0,0,1,1], addr)

    def writemem1(self, addr, data):
        return self._writemem([0,0,0,0,0,1,0,0], addr, data)

    def readmem3(self, addr):
        return self._readmem([0,0,0,0,0,1,0,1], addr)

    def writemem3(self, addr, data):
        return self._writemem([0,0,0,0,0,1,1,0], addr, data)


def main():
    c = Controller()

    start = time.time()
    print "Doing LED flash"
    for i in xrange(2):
        c.write(REGS.led0, 1)
        c.write(REGS.led1, 1)
        c.write(REGS.led2, 1)
        c.write(REGS.led0, 0)
        c.write(REGS.led1, 0)
        c.write(REGS.led2, 0)
    elapsed = time.time() - start

    def check(name, expected):
        # print name, "=",
        r = c.read(getattr(REGS, name))
        # print r
        if r != expected:
            print "\033[31mERROR: expected %s=%d, but got %d\033[0m" % (name, expected, r)
            return 1
        return 0

    def checkStatuses():
        print "Checking statuses..."
        err = 0
        err += check('led0', 0)
        err += check('led1', 0)
        err += check('led2', 0)
        err += check('calib1_done', 1)
        err += check('calib3_done', 1)
        err += check('cmd_empty', 1)
        err += check('cmd_full', 0)
        err += check('wr_empty', 1)
        err += check('wr_full', 0)
        err += check('wr_underrun', 0)
        err += check('wr_error', 0)
        err += check('rd_empty', 1)
        err += check('rd_full', 0)
        err += check('rd_overflow', 0)
        err += check('rd_error', 0)
        return err

    if checkStatuses():
        pass
        # return

    def runChecks(rd, wr):
        failed = False

        print "Doing basic DQ checks..."
        wr(0, 0)
        r0 = rd(0)
        wr(0, ~0)
        r1 = rd(0)
        if r0 == r1:
            print "\033[31mWrite to addr 0 had no effect!"
            print "Aborting rest of checks\033[0m"
            return

        if r0 != 0:
            failed = True
            print "\033[31mWrite of 0 to addr 0 read back as %d\033[0m" % r0
            for i in xrange(32):
                if r0 & (1 << i):
                    print "Bit %d is still set" % i
        if r1 != 0xffffffff:
            failed = True
            print "\033[31mWrite of -1 to addr 0 read back as %d\033[0m" % r1
            for i in xrange(32):
                if r0 & (1 << i) == 0:
                    print "Bit %d is not set" % i

        """
        print "Determining size of SDRAM..."
        for i in xrange(31, 1, -1):
            addr = 2**i
            wr(addr, addr)
        size = rd(0)
        print "memory size: %.1fMB" % (size * 0.5**20)
        """

        print "Doing addr checks..."
        wr(0, 0)
        failed_addrs = []
        for i in xrange(2, 32):
            print "\033[100D%d" % i,
            sys.stdout.flush()
            addr = 2**i
            wr(addr, addr)
            b = rd(0)
            assert b == 0 or b == addr, (b, addr)
            if b == addr:
                failed_addrs.append(i)
                wr(0, 0)
        print

        if failed_addrs:
            if failed_addrs == range(failed_addrs[0], 32) and failed_addrs[0] > 20:
                # print "Byte address bits %d+ failed_addrs" % failed_addrs[0]
                print "Failures consistent with memory being %.1fMB" % (2.0 ** (failed_addrs[0] - 20))
            else:
                failed = True
                print "\033[31mERROR"
                print "Address line failures detected!\033[0m"
                for i in failed_addrs:
                    print "Byte address bit %d had no effect" % i
                    print "(Ok if size <= %.1fMB)" % (2.0 ** (addr - 20))

        N_TO_CHECK = 128
        l = []
        for i in xrange(N_TO_CHECK):
            val = random.randrange(0, 1<<24)
            l.append(val & ~0x3)

        def check_retain(l):
            for i, addr in enumerate(l):
                print "\033[100DWriting %d" % (i+1),
                sys.stdout.flush()
                # print "writing", addr
                wr(addr, addr)
            print
            for i, addr in enumerate(l):
                print "\033[100DReading %d" % (i+1),
                sys.stdout.flush()
                # print "checking", addr
                v = rd(addr)
                assert v == addr, (hex(addr), hex(v))
            print

        # check_retain(range(0, 32, 4))

        print "Writing %d values and reading them back..." % len(l)
        check_retain(l)

        if failed:
            print "Failures detected!"
        else:
            print "\033[36;1mAll checks passed!\033[0m"

    print
    print "\033[1mDoing DDR3 checks\033[0m"
    runChecks(c.readmem3, c.writemem3)
    if checkStatuses():
        return

    print
    print "\033[1mDoing DDR1 checks\033[0m"
    runChecks(c.readmem1, c.writemem1)
    if checkStatuses():
        return

    return

if __name__ == "__main__":
    main()
