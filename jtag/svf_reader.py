import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import Queue
import time

from debugger.controller import Controller

class SpiController(object):
    def __init__(self):
        self.ctlr = Controller()
        self.ctlr.on_read.append(self._on_read)
        self.q = Queue.Queue()

        self.TDO = 5
        self.TCK = 4
        self.TMS = 3
        self.TDI = 2
        self.DBG1 = 6
        self.DBG2 = 7

        self.ctlr.pinMode(self.TDO, "input")
        self.ctlr.pinMode(self.TCK, "output")
        self.ctlr.pinMode(self.TMS, "output")
        self.ctlr.pinMode(self.TDI, "output")
        self.ctlr.pinMode(self.DBG1, "output")
        self.ctlr.pinMode(self.DBG2, "output")

    def _on_read(self, c):
        self.q.put(c)

    def pulse(self, tms, tdi, tdo=True):
        DELAY = 0.0
        self.ctlr.digitalWrite(self.TMS, tms)
        self.ctlr.digitalWrite(self.TDI, tdi)
        time.sleep(DELAY)

        self.ctlr.digitalWrite(self.TCK, 1)
        time.sleep(DELAY)
        self.ctlr.digitalWrite(self.TCK, 0)
        time.sleep(DELAY)

        if tdo:
            self.ctlr.digitalRead(self.TDO)
            b = ord(self.q.get())
            # print "pulse", tms, tdi, b
            return b

class JtagController(object):
    def __init__(self):
        self.state = None
        self.ctlr = SpiController()

        self.pulse = self.ctlr.pulse

    def send(self, nbits, tdi, tdo_mask):
        assert self.state in ("irshift", "drshift"), self.state
        rtn = 0
        for i in xrange(nbits):
            bitmask = (1<<i)
            get_tdo = (i==nbits+1) or bool(tdo_mask & (1<<(i+1)))
            b = self.pulse(1 if i == nbits-1 else 0, 1 if (tdi & bitmask) else 0, tdo=get_tdo)
            if b and i != nbits -1:
                rtn |= bitmask

        if self.state == "irshift":
            self.state = "irexit1"
        else:
            self.state = "drexit1"

        return rtn, b

    def goto(self, new_state):
        new_state = new_state.lower()
        if self.state is None:
            assert new_state == "reset"
        else:
            assert new_state != "reset"

        b = None
        while new_state != self.state:
            if self.state is None:
                assert new_state == "reset"
                for i in xrange(5):
                    b = self.ctlr.pulse(1, 0)
                self.state = "reset"
            elif self.state == "reset":
                b = self.ctlr.pulse(0, 0)
                self.state = "idle"
            elif self.state == "idle":
                b = self.ctlr.pulse(1, 0)
                self.state = "drselect"
            elif self.state == "irpause":
                b = self.ctlr.pulse(1, 0)
                self.state = "irexit2"
            elif self.state == "irexit2":
                if new_state in ("irupdate", "idle") or new_state.startswith("dr"):
                    b = self.ctlr.pulse(1, 0)
                    self.state = "irupdate"
                else:
                    raise Exception(new_state)
            elif self.state == "irupdate" or self.state == "drupdate":
                if new_state == "idle":
                    b = self.ctlr.pulse(0, 0)
                    self.state = "idle"
                else:
                    b = self.ctlr.pulse(1, 0)
                    self.state = "drselect"
            elif self.state == "drselect":
                if new_state.startswith("dr"):
                    b = self.ctlr.pulse(0, 0)
                    self.state = "drcapture"
                else:
                    b = self.ctlr.pulse(1, 0)
                    self.state = "irselect"
            elif self.state == "irselect":
                assert new_state.startswith("ir")
                b = self.ctlr.pulse(0, 0)
                self.state = "ircapture"
            elif self.state == "drcapture":
                if new_state in ("drexit1", "drpause"):
                    b = self.ctlr.pulse(1, 0)
                    self.state = "drexit1"
                elif new_state == "drshift":
                    b = self.ctlr.pulse(0, 0)
                    self.state = "drshift"
                else:
                    raise Exception(new_state)
            elif self.state == "ircapture":
                if new_state in ("irexit1", "irpause"):
                    b = self.ctlr.pulse(1, 0)
                    self.state = "irexit1"
                elif new_state == "irshift":
                    b = self.ctlr.pulse(0, 0)
                    self.state = "irshift"
                else:
                    raise Exception(new_state)
            elif self.state == "drexit1":
                if new_state == "drpause":
                    b = self.ctlr.pulse(0, 0)
                    self.state = "drpause"
                elif new_state in ("idle", "drupdate"):
                    b = self.ctlr.pulse(1, 0)
                    self.state = "drupdate"
                else:
                    raise Exception(new_state)
            elif self.state == "irexit1":
                if new_state == "irpause":
                    b = self.ctlr.pulse(0, 0)
                    self.state = "irpause"
                elif new_state == "idle":
                    b = self.ctlr.pulse(1, 0)
                    self.state = "irupdate"
                else:
                    raise Exception(new_state)
            elif self.state == "drpause":
                b = self.ctlr.pulse(1, 0)
                self.state = "drexit2"
            elif self.state == "drexit2":
                if new_state in ("drupdate", "idle", "irshift"):
                    b = self.ctlr.pulse(1, 0)
                    self.state = "drupdate"
                else:
                    raise Exception(new_state)
            else:
                raise Exception((self.state, new_state))
        return b

def main(fn):
    ctlr = JtagController()

    endir = None
    enddr = None

    f = open(fn)
    cur = ""
    for l in f:
        l = cur + l.strip()
        if not l:
            continue

        print l
        l = l.split('//')[0].strip()
        if not l:
            continue

        if not l.endswith(';'):
            cur = l
            continue
        else:
            cur = ''
        assert l.endswith(';')
        l = l[:-1]

        tokens = l.split()
        cmd, args = tokens[0], tokens[1:]
        if cmd == "TRST":
            assert args == ["OFF"]
            assert ctlr.state is None
        elif cmd == "FREQUENCY":
            pass
        elif cmd in ("TIR", "HIR", "TDR", "HDR"):
            assert args == ["0"]
        elif cmd == "ENDIR":
            endir = args[0].lower()
        elif cmd == "ENDDR":
            enddr = args[0].lower()
        elif cmd == "RUNTEST":
            assert args[-1] == "TCK"
            if len(args) == 3:
                ctlr.goto(args[0].lower())
                assert args[0].lower() == ctlr.state, ctlr.state
                del args[0]

            mult = 1.0 / 1000000 # 1MHz
            to_sleep = mult * int(args[0])
            to_sleep = min(0.001, to_sleep*10) # to be safe
            time.sleep(to_sleep)
        elif cmd == "STATE":
            for new_state in args:
                new_state = new_state.lower()
                ctlr.goto(new_state)
        elif cmd == "SIR" or cmd == "SDR":
            if cmd == "SIR":
                b = ctlr.goto("irshift")
            else:
                b = ctlr.goto("drshift")

            tdi = None
            tdo = 0
            mask = 0
            length = int(args[0])
            for i in xrange(1, len(args), 2):
                if args[i] == "TDI":
                    tdi = int(args[i+1][1:-1], 16)
                elif args[i] == "TDO":
                    tdo = int(args[i+1][1:-1], 16)
                elif args[i] == "MASK":
                    mask = int(args[i+1][1:-1], 16)
                elif args[i] == "SMASK":
                    pass
                else:
                    raise Exception(args[i])

            got_tdo, _ = ctlr.send(length, tdi, mask)
            got_tdo = (got_tdo << 1) | b
            if (got_tdo ^ tdo) & mask != 0:
                print "Bad TDO back!"
                print str(bin(got_tdo)).rjust(length+3)
                print str(bin(tdo)).rjust(length+3)
                print str(bin(mask)).rjust(length+3)
            assert (got_tdo ^ tdo) & mask == 0, (bin(got_tdo), bin(tdo), bin(mask))

            if cmd == "SIR":
                ctlr.goto(endir)
            else:
                ctlr.goto(enddr)
        else:
            raise Exception(l)

if __name__ == "__main__":
    fn = sys.argv[1]
    main(fn)

