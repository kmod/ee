import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import Queue
import threading
import time

from debugger.controller import Controller

print_lock = threading.Lock()

class JtagController(object):
    def __init__(self, use_verify_thread):
        self.state = None
        self.ctlr = Controller(autoflush=0, br=500000)

        self.buf = None

        self.npulses = 0
        self.est_buf = 0
        self.EST_SPEED = 15000.0
        self.last_est = time.time()

        if use_verify_thread:
            self._verify_queue = Queue.Queue(maxsize=1)

            t = threading.Thread(target=self._verify_thread)
            t.setDaemon(True)
            t.start()

    def _write(self, s):
        # print bin(ord(s))[2:].rjust(8, '0')
        assert len(s) < 10
        cost = len(s)
        while True:
            now = time.time()
            new_est = self.est_buf - self.EST_SPEED * (now - self.last_est)
            self.est_buf = max(new_est, 0)
            self.last_est = now

            if self.est_buf + cost < 50:
                break
            self.ctlr.flush()
        self.est_buf += cost
        self.ctlr._write(s)

    def sleep_micros(self, micros):
        assert self.state in ("drpause", "idle", "irpause"), self.state

        start = time.time()
        micros_per_pulse = 1000000.0 / (self.EST_SPEED * 2)
        npulses = int((micros + micros_per_pulse + 1) / micros_per_pulse)
        npulses = max(npulses, 5)
        # print "Doing %d pulses" % npulses
        for i in xrange(npulses):
            self.pulse(0, 0, get_tdo=False)
        print time.time() - start

    def flush(self):
        if self.buf is not None:
            self._write(chr(self.buf | (1<<4)))
            self.buf = None
        self.ctlr.flush()

    def pulse(self, tms, tdi, get_tdo=True):
        # with print_lock:
            # print tms, tdi, get_tdo
        data = (tms << 3) | (tdi << 2) | (get_tdo << 1)
        if self.buf is None:
            self.buf = data
        else:
            self._write(chr((self.buf << 4) | data))
            self.buf = None
        self.npulses += 1

    def queue_verify(self, nbits, tdo, tdo_mask):
        try:
            self._verify_queue.put((nbits, tdo, tdo_mask), timeout=0)
        except Queue.Full:
            self.flush()
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
                with print_lock:
                    print bin(got_tdo).rjust(nbits+10)
                    print bin(tdo).rjust(nbits+10)
                    print bin(mask).rjust(nbits+10)
                os._exit(1)
            self._verify_queue.task_done()

    def join(self):
        self.flush()
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

def main(fn):
    ctlr = JtagController(use_verify_thread=True)

    start = time.time()
    endir = None
    enddr = None

    hir_length = 0
    hir_tdi = 0
    hir_tdo = 0
    hir_mask = 0
    hdr_length = 0
    hdr_tdi = 0
    hdr_tdo = 0
    hdr_mask = 0

    tir_length = 0
    tir_tdi = 0
    tir_tdo = 0
    tir_mask = 0
    tdr_length = 0
    tdr_tdi = 0
    tdr_tdo = 0
    tdr_mask = 0

    tick_micros = None

    f = open(fn)
    cur = ""
    for l in f:
        l = cur + l.strip()
        if not l:
            continue

        with print_lock:
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
            assert args[1] == "HZ"
            tick_micros = args[0]
            if tick_micros == "1E6":
                tick_micros = 1
            else:
                assert 0, tick_micros
        elif cmd in ("HIR", "HDR", "TIR", "TDR"):
            length = int(args[0])

            if cmd == "HIR":
                tdi, tdo, mask, prev_length = hir_tdi, hir_tdo, hir_mask, hir_length
            elif cmd == "HDR":
                tdi, tdo, mask, prev_length = hdr_tdi, hdr_tdo, hdr_mask, hdr_length
            elif cmd == "TIR":
                tdi, tdo, mask, prev_length = tir_tdi, tir_tdo, tir_mask, tir_length
            else:
                tdi, tdo, mask, prev_length = tdr_tdi, tdr_tdo, tdr_mask, tdr_length

            if prev_length != length:
                mask = (1 << length) - 1

            if length != 0:
                assert "TDI" in args
            else:
                tdi = 0

            if "TDO" not in args:
                tdo = 0
                mask = 0

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

            if cmd == "HIR":
                hir_tdi, hir_tdo, hir_mask, hir_length = tdi, tdo, mask, length
            elif cmd == "HDR":
                hdr_tdi, hdr_tdo, hdr_mask, hdr_length = tdi, tdo, mask, length
            elif cmd == "TIR":
                tir_tdi, tir_tdo, tir_mask, tir_length = tdi, tdo, mask, length
            else:
                tdr_tdi, tdr_tdo, tdr_mask, tdr_length = tdi, tdo, mask, length

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

            ctlr.sleep_micros(int(args[0]) * tick_micros)
        elif cmd == "STATE":
            for new_state in args:
                new_state = new_state.lower()
                ctlr.goto(new_state)
        elif cmd == "SIR" or cmd == "SDR":
            assert "TDI" in args

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

            if cmd == "SIR":
                ctlr.goto("irshift")
                tdi = (((tir_tdi << length) + tdi) << hir_length) + hir_tdi
                tdo = (((tir_tdo << length) + tdo) << hir_length) + hir_tdo
                mask = (((tir_mask << length) + mask) << hir_length) + hir_mask
                length += hir_length + tir_length
            else:
                ctlr.goto("drshift")
                tdi = (((tdr_tdi << length) + tdi) << hdr_length) + hdr_tdi
                tdo = (((tdr_tdo << length) + tdo) << hdr_length) + hdr_tdo
                mask = (((tdr_mask << length) + mask) << hdr_length) + hdr_mask
                length += hdr_length + tdr_length

            with print_lock:
                print length, hex(tdi), hex(tdo), hex(mask)

            ctlr.send(length, tdi, mask)
            ctlr.queue_verify(length, tdo, mask)
            # ctlr.join()

            if cmd == "SIR":
                ctlr.goto(endir)
            else:
                ctlr.goto(enddr)
        else:
            raise Exception(l)

    assert not cur, "trailing command"

    ctlr.join()
    with print_lock:
        elapsed = time.time() - start
        print "Took %.1fs to program, sent %d pulses (%.1fkHz)" % (elapsed, ctlr.npulses, ctlr.npulses * 0.001 / elapsed)
        print "Sent %d bytes, received %d" % (ctlr.ctlr.bytes_written, ctlr.ctlr.bytes_read)

if __name__ == "__main__":
    fn = sys.argv[1]

    if fn == "enumerate":
        ctlr = JtagController(use_verify_thread=False)
        ctlr.goto("reset")
        ctlr.goto("idle")

        ctlr.goto("irshift")
        ctlr.send(64, 0xffffffffffffffff, 0x0)
        for i in xrange(64):
            c = ord(ctlr.ctlr.q.get())

        ctlr.goto("idle")
        ctlr.goto("drshift")
        ctlr.send(64, 0xffffffffffffffff, 0xffffffffffffffff)
        ctlr.goto("idle")

        ctlr.flush()

        r = 0
        for i in xrange(64):
            c = ord(ctlr.ctlr.q.get())
            r |= c << i

        nconnected = 0
        while r & (1 << nconnected) == 0:
            nconnected += 1
            assert nconnected < 64, "unsupported -- increase the length of the bypass instruction"
        print "Found %d devices:" % (nconnected,)

        ctlr.goto("irshift")
        cmd = 0x0
        for i in xrange(nconnected):
            cmd = (cmd << 8) | 0x01
        cmdsize = nconnected * 8
        ctlr.send(cmdsize, cmd, 0x00)
        for i in xrange(cmdsize):
            c = ord(ctlr.ctlr.q.get())
        ctlr.goto("idle")

        ctlr.goto("drshift")
        rtnsize = 32 * nconnected
        ctlr.send(rtnsize, 0x0, (1<<rtnsize) - 1)

        idcodes = [0] * nconnected
        for i in xrange(rtnsize):
            c = ord(ctlr.ctlr.q.get())
            idcodes[i / 32] |= c << (i % 32)

        # idcodes come out starting with the last device in the chain;
        # reverse it, and it's in the order of the chain:
        idcodes.reverse()

        def idcode_to_name(code):
            masked = code & 0x0fff8fff

            idcode_to_name = {
                    0x06d58093: "cr_64",
                    0x06d88093: "cr_128",
                    }
            return idcode_to_name[masked]

        for i, code in enumerate(idcodes):
            print "Device %d: %x (%s)" % (i+1, code, idcode_to_name(code))

        assert ctlr.ctlr.q.qsize() == 0, ctlr.ctlr.q.qsize()
    else:
        main(fn)

