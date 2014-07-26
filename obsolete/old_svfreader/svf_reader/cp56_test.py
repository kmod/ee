import time
import sys

BSCAN_SIZE = 97
class BScanConfig(object):
    def __init__(self):
        self.vals = {}

    def default(self, idx):
        # IN_0 is a special case since it is input-only
        if idx == 0:
            return 1

        # Control register:
        if idx % 3 == 1:
            return 0
        # INPUT/OUTPUT:
        return 1

    def setDriveTo(self, io, val):
        assert 0 <= io <= 31, io
        cfg_pin = 1 + 3 * (31 - io)
        out_pin = 1 + cfg_pin

        assert cfg_pin not in self.vals
        assert out_pin not in self.vals

        self.vals[cfg_pin] = 1
        self.vals[out_pin] = val

    def setExpected(self, io, val):
        assert 0 <= io <= 32, io
        in_pin = 3 * (32 - io)

        assert in_pin not in self.vals

        self.vals[in_pin] = val

    def configInt(self):
        t = 0
        for i in xrange(BSCAN_SIZE):
            t += self.vals.get(i, self.default(i)) << i
        return t

    def expectedInt(self):
        t = 0
        for i in xrange(BSCAN_SIZE):
            if i % 3 == 0:
                t += self.vals.get(i, self.default(i)) << i
            else:
                t += self.default(i) << i
        return t



if __name__ == "__main__":
    print """
TRST OFF;
ENDIR IDLE;
ENDDR IDLE;
STATE RESET;
STATE IDLE;
FREQUENCY 1E6 HZ;
TIR 0 ;
HIR 0 ;
TDR 0 ;
HDR 0 ;
TIR 0 ;
HIR 0 ;
HDR 0 ;
TDR 0 ;

//Loading device with 'idcode' instruction.
SIR 8 TDI (01) SMASK (ff) ;
SDR 32 TDI (00000000) SMASK (ffffffff) TDO (f6e1f093) MASK (0fff8fff) ;
    """

    connected = [
            ("G1", "F1"),
            ("F3", "G3"),
            ("H1", "J1"),
            ("K1", "K2"),
            ("K3", "H3"),
            ("K5", "H5"),
            ("H8", "K8"),
            ("H10", "G10"),
            ("F10", "C10"),
            ("E8", "C8"),
            ("A10", "B10"),
            ("C4", "C5"),
            ("A1", "B1"),
            ("A2", "A3"),
            ("C1", "D1"),
            ("E1", "E3"),
            ]

    # connected = [
            # ("F10", "C10"),
            # ]

    raw_pin_map = [
        "IO_0 : F1",
        "IO_1 : E3",
        "IO_2 : E1",
        "IO_3 : D1",
        "IO_4 : C1",
        "IO_5 : A3",
        "IO_6 : A2",
        "IO_7 : B1",
        "IO_8 : A1",
        "IO_9 : C4",
        "IO_10 : C5",
        "IO_11 : C8",
        "IO_12 : A10",
        "IO_13 : B10",
        "IO_14 : C10",
        "IO_15 : E8",
        "IO_16 : G1",
        "IO_17 : F3",
        "IO_18 : H1",
        "IO_19 : G3",
        "IO_20 : J1",
        "IO_21 : K1",
        "IO_22 : K2",
        "IO_23 : K3",
        "IO_24 : H3",
        "IO_25 : K5",
        "IO_26 : H5",
        "IO_27 : H8",
        "IO_28 : K8",
        "IO_29 : H10",
        "IO_30 : G10",
        "IO_31 : F10",
    ]
    pin_map = {}

    for r in raw_pin_map:
        io, pin = r.split(':')
        io = io[3:-1]
        pin = pin[1:]
        pin_map[pin] = int(io)

    # config = BScanConfig()
    # config.vals[1] = 1
    # config.vals[2] = 0
    # config.vals[3] = 0
    # config.vals[54] = 0

    config = BScanConfig()
    config.setDriveTo(14, 0)
    config.setExpected(31, 0)
    config.setExpected(14, 0)

    print "//", bin(config.configInt())
    print "//", bin(config.expectedInt())

    # print bin(config.configInt())
    print "SIR 8 TDI (03) SMASK (ff) ;"
    print "SDR %d TDI (%x) SMASK (0) TDO (0) MASK (0) ;" % (BSCAN_SIZE, config.configInt())

    print "SIR 8 TDI (00) SMASK (ff) ;"
    print "SDR %d TDI (0) SMASK (0) TDO (%x) MASK (1ffffffffffffffffffffffff) ;" % (BSCAN_SIZE, config.expectedInt())

    config = BScanConfig()
    config.setDriveTo(31, 0)
    config.setExpected(31, 0)
    config.setExpected(14, 0)

    print "//", bin(config.configInt())
    print "//", bin(config.expectedInt())

    # print bin(config.configInt())
    print "SIR 8 TDI (03) SMASK (ff) ;"
    print "SDR %d TDI (%x) SMASK (0) TDO (0) MASK (0) ;" % (BSCAN_SIZE, config.configInt())

    print "SIR 8 TDI (00) SMASK (ff) ;"
    print "SDR %d TDI (0) SMASK (0) TDO (%x) MASK (1ffffffffffffffffffffffff) ;" % (BSCAN_SIZE, config.expectedInt())

    c = BScanConfig()
    print "SIR 8 TDI (00) SMASK (ff) ;"
    print "SDR %d TDI (%x) SMASK (0) TDO (0) MASK (0) ;" % (BSCAN_SIZE, c.configInt())
    print "SIR 8 TDI (03) SMASK (ff) ;"
    print "SDR %d TDI (0) SMASK (0) TDO (%x) MASK (1ffffffffffffffffffffffff) ;" % (BSCAN_SIZE, c.expectedInt())

    # sys.exit()

    for l in connected:
        for driver in l:
            c = BScanConfig()

            # print >>sys.stderr, "// Checking that %s are all connected, by driving %s low" % (l, driver)
            print "// Checking that %s are all connected, by driving %s low" % (l, driver)

            # print "//", "Driving", pin_map[driver], "to 0"
            c.setDriveTo(pin_map[driver], 0)
            for o in l:
                # print "//", "Expecting 0 from", pin_map[o]
                c.setExpected(pin_map[o], 0)

            print "//", bin(c.configInt())
            print "//", bin(c.expectedInt())

            print "SIR 8 TDI (03) SMASK (ff) ;"
            print "SDR %d TDI (%x) SMASK (0) TDO (0) MASK (0) ;" % (BSCAN_SIZE, c.configInt())

            print "SIR 8 TDI (00) SMASK (ff) ;"
            print "SDR %d TDI (0) SMASK (0) TDO (%x) MASK (1ffffffffffffffffffffffff) ;" % (BSCAN_SIZE, c.expectedInt())

    print "STATE RESET;"
