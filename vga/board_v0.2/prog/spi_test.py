import sys
sys.path.append('../../../jtag/svf_reader_new')

import time

from bitbang import BitbangController, ControllerHub

class Controller(object):
    def __init__(self):
        hub = ControllerHub(br=1000000)
        stream = hub.openEndpoint(0x1000)
        self.ctlr = ctlr = BitbangController(stream)

        ctlr.writeBit(0, 0, 1)
        ctlr.writeBit(3, 0, 0)
        time.sleep(0.1)
        ctlr.writeBit(3, 0, 1)

        ctlr.writeBit(2, 2, 1) # mosi
        ctlr.writeBit(2, 3, 1) # cso_b
        ctlr.writeBit(2, 4, 1) # cclk
        ctlr.writeBit(2, 5, 0) # miso

        self.disable()

        # print bin(ctlr.read(5))[2:].rjust(8, '0')

    def enable(self):
        # make sure clk starts low:
        self.ctlr.writeBit(8, 4, 0)
        # then enable:
        self.ctlr.writeBit(8, 3, 0)

    def disable(self):
        self.ctlr.writeBit(8, 3, 1)

    def clock_byte(self, val):
        rtn = 0
        for i in xrange(8):
            bval = (val >> (7 - i)) & 0x1

            # set mosi:
            self.ctlr.writeBit(8, 2, bval)

            # set cclk:
            self.ctlr.writeBit(8, 4, 1)

            # then read
            v = self.ctlr.read(5)
            if v & 0x20:
                rtn |= 1 << (7-i)

            # set cclk:
            self.ctlr.writeBit(8, 4, 0)

        return rtn

    def status(self):
        self.enable()
        self.clock_byte(0x05)
        print bin(self.clock_byte(0x00))[2:].rjust(8, '0')
        self.disable()

    def read(self, addr, nbytes):
        assert 1 <= nbytes <= 256
        self.enable()
        self.clock_byte(0x03)
        self.clock_byte((addr >> 16) & 0xff)
        self.clock_byte((addr >> 8) & 0xff)
        self.clock_byte((addr >> 0) & 0xff)

        l = []
        for i in xrange(nbytes):
            print i
            c = chr(self.clock_byte(0x00))
            l.append(c)
        self.disable()

        return ''.join(l)

    def program(self, addr, data):
        assert 1 <= len(data) <= 256

        self.enable()
        self.clock_byte(0x06) # wren
        self.disable()
        self.enable()

        self.clock_byte(0x02) # program
        self.clock_byte((addr >> 16) & 0xff)
        self.clock_byte((addr >> 8) & 0xff)
        self.clock_byte((addr >> 0) & 0xff)

        for c in data:
            print ord(c)
            self.clock_byte(ord(c))

        self.disable()


def main():
    ctlr = Controller()

    ctlr.status()
    print repr(ctlr.read(0, 16))
    ctlr.status()
    # ctlr.program(0, "\xfe\xfd\xfc")
    # ctlr.status()
    print repr(ctlr.read(0, 16))
    ctlr.status()

if __name__ == "__main__":
    main()
