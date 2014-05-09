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
        # setup:
        ctlr.writeBit(8, 2, 0)
        ctlr.writeBit(8, 4, 0)

        print bin(ctlr.read(5))[2:].rjust(8, '0')

    def enable(self):
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


def main():
    ctlr = Controller()

    ctlr.enable()
    print ctlr.clock_byte(0x05)
    print ctlr.clock_byte(0x00)
    print ctlr.clock_byte(0x00)
    print ctlr.clock_byte(0x00)

    print ctlr.clock_byte(0x00)
    print ctlr.clock_byte(0x00)
    ctlr.disable()

if __name__ == "__main__":
    main()
