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

        self.npulses = 0
        self.EST_SPEED = 50000.0
        self.bufbuf = ''

        if use_verify_thread:
            self._verify_queue = Queue.Queue(maxsize=4)

            t = threading.Thread(target=self._verify_thread)
            t.setDaemon(True)
            t.start()

    def _write(self, s):
        self.ctlr._write(s)

    def sleep_micros(self, micros):
        assert self.state in ("drpause", "idle", "irpause"), self.state

        # start = time.time()
        micros_per_pulse = 1000000.0 / (self.EST_SPEED)
        npulses = int((micros + micros_per_pulse + 1) / micros_per_pulse)
        npulses = max(npulses, 5)
        # print "Doing %d pulses" % npulses
        for i in xrange(npulses):
            self.pulse(0, 0, get_tdo=False)
        # print time.time() - start

    def flush(self):
        # assert not self.bufbuf
        self._write(self.bufbuf)
        self.bufbuf = ""
        self.ctlr.flush()
        # time.sleep(0.001)

    def pulse(self, tms, tdi, get_tdo=True):
        # with print_lock:
            # print tms, tdi, get_tdo
        data = (tms << 3) | (tdi << 2) | (get_tdo << 1)
        data = chr(data + 16)
        self.bufbuf += data
        if len(self.bufbuf) >= 1024:
            self._write(self.bufbuf)
            # time.sleep(0.001)
            self.bufbuf = ""
        self.npulses += 1

        if self.npulses % 100 == 0:
            time.sleep(0.001)

    def queue_verify(self, nbits, tdo, tdo_mask):
        return # verifying is broken
        try:
            self._verify_queue.put((nbits, tdo, tdo_mask), timeout=0)
        except Queue.Full:
            self.flush()
            self._verify_queue.put((nbits, tdo, tdo_mask), timeout=60)
        # self.join()

    def _verify_thread(self):
        while True:
            nbits, tdo, mask = self._verify_queue.get()
            print "waiting for %d bits" % nbits

            hex_digits = [0] * ((nbits + 3) / 4)
            for i in xrange(nbits):
                if i and i % 10000 == 0:
                    with print_lock:
                        print "i =", i, self.ctlr.q.qsize()
                # print i, nbits
                c = self.ctlr.q.get()
                if c != '\0':
                    hex_digits[i/4] |= (1 << (i%4))

            got_tdo_hex = ''.join(reversed([hex(i)[2] for i in hex_digits]))
            got_tdo = int(got_tdo_hex, 16)

            mismatch = (got_tdo ^ tdo) & mask
            if mismatch:
                if mask < (1<<1000):
                    with print_lock:
                        print "Gotten:     ", bin(got_tdo)[2:].rjust(nbits, '0')
                        print "Expected:   ", bin(tdo)[2:].rjust(nbits, '0')
                        print "Care-mask:  ", bin(mask)[2:].rjust(nbits, '0')
                else:
                    with print_lock:
                        print "Mismatch -- too long to print, but %d/%d bits different" % (bin(mismatch).count('1'), nbits)
                        # with open("gotten.out", 'w') as f:
                            # f.write(bin(got_tdo)[2:].rjust(nbits, '0'))
                        # with open("expected.out", 'w') as f:
                            # f.write(bin(tdo)[2:].rjust(nbits, '0'))
                        # with open("mask.out", 'w') as f:
                            # f.write(bin(mask)[2:].rjust(nbits, '0'))
                        # print "Written to gotten.out, expected.out, and mask.out"
                # raise Exception()
                os._exit(-1)
            self._verify_queue.task_done()

    def join(self):
        self.flush()
        self._verify_queue.join()

    def send(self, nbits, tdi, tdo_mask):
        assert self.state in ("irshift", "drshift"), self.state

        tdi_hex = hex(tdi)
        assert tdi_hex.startswith("0x")
        if tdi_hex.endswith("L"):
            tdi_hex = tdi_hex[2:-1]
        else:
            tdi_hex = tdi_hex[2:]
        tdi_hex = tdi_hex.rjust((nbits + 3) / 4, '0')

        for i in xrange(nbits):
            tdi_chr = tdi_hex[-(i/4 + 1)]
            tdi_bit = (int(tdi_chr, 16) >> (i % 4)) & 1
            get_tdo = 0 if i == nbits-1 else 1
            self.pulse(1 if i == nbits-1 else 0, tdi_bit, get_tdo=get_tdo)

            if (nbits - i) % 10000 == 0:
                print "%d bits left in this command" % (nbits - i,)

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
                elif new_state == "irshift":
                    self.pulse(0, 0, get_tdo=True)
                    self.state = "irshift"
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

def read_svf_file(fn):
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
        size = 1 << 30
    else:
        f = open(fn)
        size = os.stat(fn).st_size

    cur = []

    bytes_read = 0

    while True:
        l = f.readline()
        if not l:
            break

        bytes_read += len(l)

        l = l.split('//')[0].strip()
        if not l:
            continue

        cur.append(l)

        with print_lock:
            if bytes_read < 10000:
                print l
            else:
                print "%d/%d (%.1f%%)" % (bytes_read, size, 100.0 * bytes_read / size)

        if not l.endswith(';'):
            continue
        else:
            l = ''.join(cur)
            cur = []

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

            # with print_lock:
                # print length, hex(tdi), hex(tdo), hex(mask)

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
    ctlr.ctlr.ser.close()

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
        MAX_INSTRUCTION_LEN = 8
        MAX_BYPASS_INST = MAX_INSTRUCTION_LEN * MAX_CHAIN_SIZE

        ctlr = JtagController(use_verify_thread=False)
        ctlr.goto("reset")
        ctlr.goto("idle")

        ctlr.goto("irshift")
        ctlr.send(MAX_BYPASS_INST, (1 << MAX_BYPASS_INST) - 1, 0x0)
        ctlr.flush()
        for i in xrange(MAX_BYPASS_INST):
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

        IDCODE_CMDS = [
                (0b00000001, 8),
                (0b001001, 6),
                ]

        identified_instr_lens = []
        for device_idx in xrange(nconnected):
            print "Identifying device #%d..." % device_idx,
            sys.stdout.flush()

            for idcode_cmd, idcode_len in IDCODE_CMDS:
                cmd = 0x0
                cmd_len = 0

                for j in xrange(device_idx):
                    l = identified_instr_lens[j]
                    cmd = (cmd << l) | ((1 << l) - 1)
                    cmd_len += l

                cmd = (cmd << idcode_len) | idcode_cmd
                cmd_len += idcode_len

                for j in xrange(device_idx + 1, nconnected):
                    cmd = (cmd << MAX_INSTRUCTION_LEN) | ((1 << MAX_INSTRUCTION_LEN) - 1)
                    cmd_len += MAX_INSTRUCTION_LEN

                # cmd = 0b1111111111111100000001
                # cmd_len = 22

                ctlr.goto("irshift")
                # print cmd_len, bin(cmd)
                ctlr.send(cmd_len, cmd, 0x0)
                ctlr.flush()
                for i in xrange(cmd_len):
                    c = ord(ctlr.ctlr.q.get())
                ctlr.goto("idle")

                ctlr.goto("drshift")
                rtnsize = 32 + (nconnected - 1)
                ctlr.send(rtnsize, 0x0, (1 << rtnsize) - 1)
                ctlr.goto("idle")

                idcode = 0
                ctlr.flush()
                for i in xrange(rtnsize):
                    c = ord(ctlr.ctlr.q.get())
                    idcode |= c << i
                # print bin(idcode)
                idcode >>= (nconnected - 1 - device_idx)
                idcode &= (1<<32) - 1

                idcode_str = idcode_to_name(idcode)
                if idcode_str and 'unknown' not in idcode_str:
                    print idcode_str
                    identified_instr_lens.append(idcode_len)
                    break
            else:
                print "Unable to identify!"
                raise Exception("Unable to identify!")


        assert ctlr.ctlr.q.qsize() == 0, ctlr.ctlr.q.qsize()
    else:
        # import cProfile
        # def run():
            # try:
                # read_svf_file(fn)
            # except Exception:
                # import traceback
                # traceback.print_exc()
        # cProfile.run("run()", "cprofile.stats")
        read_svf_file(fn)


