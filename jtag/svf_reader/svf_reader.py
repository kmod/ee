import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import Queue
import threading
import time

from debugger.controller import Controller

class JtagController(object):
    def __init__(self):
        self.state = None
        self.ctlr = Controller(autoflush=0, br=115200)

        self.npulses = 0

        self._verify_queue = Queue.Queue()

        t = threading.Thread(target=self._verify_thread)
        t.setDaemon(True)
        t.start()

    def sleep_micros(self, micros):
        for i in xrange(0, micros, 100):
            self.ctlr._write(chr(1<<4))

    def pulse(self, tms, tdi, get_tdo=True):
        data = (tms << 7) | (tdi << 6) | (get_tdo << 5)
        self.ctlr._write(chr(data))
        self.npulses += 1

    def queue_verify(self, nbits, tdo, tdo_mask):
        try:
            self._verify_queue.put((nbits, tdo, tdo_mask), timeout=0)
        except Queue.Full:
            self.ctlr.flush()
            self._verify_queue.put((nbits, tdo, tdo_mask))

    def _verify_thread(self):
        while True:
            nbits, tdo, mask = self._verify_queue.get()

            got_tdo = 0
            for i in xrange(nbits):
                # print i, nbits
                d = ord(self.ctlr.q.get())
                if d:
                    got_tdo |= 1 << i
            if (got_tdo ^ tdo) & mask:
                print bin(got_tdo).rjust(nbits+10)
                print bin(tdo).rjust(nbits+10)
                print bin(mask).rjust(nbits+10)
                os._exit(1)
            self._verify_queue.task_done()

    def join(self):
        self.ctlr.flush()
        self._verify_queue.join()

    def send(self, nbits, tdi, tdo_mask):
        assert self.state in ("irshift", "drshift"), self.state
        for i in xrange(nbits):
            bitmask = (1<<i)
            get_tdo = 0 if i == nbits-1 else 1
            self.pulse(1 if i == nbits-1 else 0, 1 if (tdi & bitmask) else 0, get_tdo=get_tdo)

        if self.state == "irshift":
            self.state = "irexit1"
        else:
            self.state = "drexit1"

    def goto(self, new_state):
        new_state = new_state.lower()
        if self.state is None:
            assert new_state == "reset"
        else:
            assert new_state != "reset"

        while new_state != self.state:
            if self.state is None:
                assert new_state == "reset"
                for i in xrange(5):
                    self.pulse(1, 0, get_tdo=False)
                self.state = "reset"
            elif self.state == "reset":
                self.pulse(0, 0, get_tdo=False)
                self.state = "idle"
            elif self.state == "idle":
                self.pulse(1, 0, get_tdo=False)
                self.state = "drselect"
            elif self.state == "irpause":
                self.pulse(1, 0, get_tdo=False)
                self.state = "irexit2"
            elif self.state == "irexit2":
                if new_state in ("irupdate", "idle") or new_state.startswith("dr"):
                    self.pulse(1, 0, get_tdo=False)
                    self.state = "irupdate"
                else:
                    raise Exception(new_state)
            elif self.state == "irupdate" or self.state == "drupdate":
                if new_state == "idle":
                    self.pulse(0, 0, get_tdo=False)
                    self.state = "idle"
                else:
                    self.pulse(1, 0, get_tdo=False)
                    self.state = "drselect"
            elif self.state == "drselect":
                if new_state.startswith("dr"):
                    self.pulse(0, 0, get_tdo=False)
                    self.state = "drcapture"
                else:
                    self.pulse(1, 0, get_tdo=False)
                    self.state = "irselect"
            elif self.state == "irselect":
                assert new_state.startswith("ir")
                self.pulse(0, 0, get_tdo=False)
                self.state = "ircapture"
            elif self.state == "drcapture":
                if new_state in ("drexit1", "drpause"):
                    self.pulse(1, 0, get_tdo=False)
                    self.state = "drexit1"
                elif new_state == "drshift":
                    self.pulse(0, 0, get_tdo=True)
                    self.state = "drshift"
                else:
                    raise Exception(new_state)
            elif self.state == "ircapture":
                if new_state in ("irexit1", "irpause"):
                    self.pulse(1, 0, get_tdo=False)
                    self.state = "irexit1"
                elif new_state == "irshift":
                    self.pulse(0, 0, get_tdo=True)
                    self.state = "irshift"
                else:
                    raise Exception(new_state)
            elif self.state == "drexit1":
                if new_state == "drpause":
                    self.pulse(0, 0, get_tdo=False)
                    self.state = "drpause"
                elif new_state in ("idle", "drupdate"):
                    self.pulse(1, 0, get_tdo=False)
                    self.state = "drupdate"
                else:
                    raise Exception(new_state)
            elif self.state == "irexit1":
                if new_state == "irpause":
                    self.pulse(0, 0, get_tdo=False)
                    self.state = "irpause"
                elif new_state == "idle":
                    self.pulse(1, 0, get_tdo=False)
                    self.state = "irupdate"
                else:
                    raise Exception(new_state)
            elif self.state == "drpause":
                self.pulse(1, 0, get_tdo=False)
                self.state = "drexit2"
            elif self.state == "drexit2":
                if new_state in ("drupdate", "idle", "irshift"):
                    self.pulse(1, 0, get_tdo=False)
                    self.state = "drupdate"
                else:
                    raise Exception(new_state)
            else:
                raise Exception((self.state, new_state))
        return b

def main(fn):
    ctlr = JtagController()

    start = time.time()
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

            ctlr.sleep_micros(int(args[0]))
        elif cmd == "STATE":
            for new_state in args:
                new_state = new_state.lower()
                ctlr.goto(new_state)
        elif cmd == "SIR" or cmd == "SDR":
            if cmd == "SIR":
                ctlr.goto("irshift")
            else:
                ctlr.goto("drshift")

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

            ctlr.send(length, tdi, mask)
            ctlr.queue_verify(length, tdo, mask)
            # ctlr.join()

            if cmd == "SIR":
                ctlr.goto(endir)
            else:
                ctlr.goto(enddr)
        else:
            raise Exception(l)

    ctlr.join()
    print "Took %.1fs to program, sent %d pulses" % (time.time() - start, ctlr.npulses)
    print "Sent %d bytes, received %d" % (ctlr.ctlr.bytes_written, ctlr.ctlr.bytes_read)

if __name__ == "__main__":
    fn = sys.argv[1]
    main(fn)

