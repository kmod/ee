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
            self._verify_queue = Queue.Queue(maxsize=2)

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
        # self.join()

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
                    print "Gotten:     ", bin(got_tdo)[2:].rjust(nbits, '0')
                    print "Expected:   ", bin(tdo)[2:].rjust(nbits, '0')
                    print "Care-mask:  ", bin(mask)[2:].rjust(nbits, '0')
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

        if self.state is None or new_state == "reset":
            for i in xrange(5):
                self.pulse(1, 0, get_tdo=False)
            self.state = "reset"

        assert self.state

        while new_state != self.state:
            if self.state == "reset":
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

    if fn == '-':
        f = sys.stdin
    else:
        f = open(fn)
    cur = ""

    while True:
        l = f.readline()
        if not l:
            break

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

    if fn == "spam":
        ctlr = JtagController(use_verify_thread=False)
        ctlr.goto("RESET")
        ctlr.goto("IDLE")
        ctlr.goto("IRSHIFT")
        while True:
            ctlr.pulse(0, 0, get_tdo=False)
            ctlr.flush()
            ctlr.pulse(0, 1, get_tdo=False)
            ctlr.flush()

    elif fn == "enumerate":
        MAX_CHAIN_SIZE = 8
        MAX_BYPASS_INST = 8 * MAX_CHAIN_SIZE

        ctlr = JtagController(use_verify_thread=False)
        ctlr.goto("reset")
        ctlr.goto("idle")

        ctlr.goto("irshift")
        ctlr.send(MAX_BYPASS_INST, (1 << MAX_BYPASS_INST) - 1, 0x0)
        for i in xrange(8 * MAX_CHAIN_SIZE):
            c = ord(ctlr.ctlr.q.get())

        ctlr.goto("idle")
        ctlr.goto("drshift")
        DRSHIFT_SIZE = MAX_CHAIN_SIZE + 1
        ctlr.send(DRSHIFT_SIZE, (1 << DRSHIFT_SIZE) - 1, (1 << DRSHIFT_SIZE) - 1)
        ctlr.goto("idle")

        ctlr.flush()

        r = 0
        for i in xrange(DRSHIFT_SIZE):
            c = ord(ctlr.ctlr.q.get())
            r |= c << i
        # print hex(r)

        nconnected = 0
        while r & (1 << nconnected) == 0:
            nconnected += 1
            assert nconnected <= MAX_CHAIN_SIZE, "Error: either there are more than %d devices connected, or there is a break in the JTAG chain" % MAX_CHAIN_SIZE
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
            IDCODES = [
                ('xc2c128_cp132', 0x6d8b093, 0xfffffff),
                ('xc2c128_cv100', 0x86d8e093, 0xffffffff),
                ('xc2c128_ft256', 0x6d8e093, 0xfffffff),
                ('xc2c128_tq144', 0x6d8c093, 0xfffffff),
                ('xc2c128_vq100', 0x6d8a093, 0xfffffff),
                ('xc2c256_cp132', 0x6d4b093, 0xfffffff),
                ('xc2c256_ft256', 0x6d4e093, 0xfffffff),
                ('xc2c256_pq208', 0x6d4d093, 0xfffffff),
                ('xc2c256_tq144', 0x6d4c093, 0xfffffff),
                ('xc2c256_vq100', 0x6d4a093, 0xfffffff),
                ('xc2c32_cp56', 0x6c1b093, 0xfdfffff),
                ('xc2c32_pc44', 0x6c1d093, 0xfdfffff),
                ('xc2c32_pc64', 0x6c1d093, 0xfdfffff),
                ('xc2c32_vq44', 0x6c1c093, 0xfdfffff),
                ('xc2c32a_cp56', 0x6e1b093, 0xfffffff),
                ('xc2c32a_cv64', 0x86e1a093, 0xffffffff),
                ('xc2c32a_pc44', 0x6e1d093, 0xfffffff),
                ('xc2c32a_pc64', 0x6e1d093, 0xfffffff),
                ('xc2c32a_qf32', 0x6c1b093, 0xffffffff),
                ('xc2c32a_vq44', 0x6e1c093, 0xfffffff),
                ('xc2c384_cp204', 0x6d5b093, 0xfffffff),
                ('xc2c384_fg324', 0x6d5a093, 0xfffffff),
                ('xc2c384_ft256', 0x6d5e093, 0xfffffff),
                ('xc2c384_pq208', 0x6d5d093, 0xfffffff),
                ('xc2c384_tq144', 0x6d5c093, 0xfffffff),
                ('xc2c512_fg324', 0x6d7a093, 0xfffffff),
                ('xc2c512_ft256', 0x6d7e093, 0xfffffff),
                ('xc2c512_pq208', 0x6d7c093, 0xfffffff),
                ('xc2c64_cp132', 0x6c5b093, 0xfdfffff),
                ('xc2c64_cp56', 0x6c5d093, 0xfdfffff),
                ('xc2c64_pc44', 0x6c5a093, 0xfdfffff),
                ('xc2c64_vq100', 0x6c5c093, 0xfdfffff),
                ('xc2c64_vq44', 0x6c5e093, 0xfdfffff),
                ('xc2c64a_cp132', 0x6e5b093, 0xfffffff),
                ('xc2c64a_cp56', 0x6e5d093, 0xfffffff),
                ('xc2c64a_cv64', 0x6e5c093, 0xfffffff),
                ('xc2c64a_pc44', 0x6e5a093, 0xfffffff),
                ('xc2c64a_qf48', 0x6e59093, 0xfffffff),
                ('xc2c64a_vq100', 0x6e5c093, 0xfffffff),
                ('xc2c64a_vq44', 0x6e5e093, 0xfffffff),

                ('xc6slx9', 0x4001093, 0xfffffff),
            ]

            for name, idcode, mask in IDCODES:
                if code & mask == idcode:
                    return name

            return "<unknown IDCODE: 0x%x>" % code

        for i, code in enumerate(idcodes):
            print "Device %d: %s" % (i+1, idcode_to_name(code))

        assert ctlr.ctlr.q.qsize() == 0, ctlr.ctlr.q.qsize()
    else:
        main(fn)

