import sys
import time

BITBANG_ENDPOINT = 0x1000
class BitbangController(object):
    def __init__(self, hub):
        self.hub = hub
        self.stream = self.hub.openEndpoint(BITBANG_ENDPOINT)

    def writeBit(self, addr, bitnum, val):
        data = 'w' + chr((addr << 4) + (bitnum << 1) + val)
        self.stream.write(data)

        check = self.stream.read(1)
        assert check == '\x00', repr(check)

    def read(self, addr):
        data = 'r' + chr(addr)

        self.stream.write(data)
        check = self.stream.read(1)
        assert check == '\x00', repr(check)
        val = ord(self.stream.read(1))
        return val

JTAG_AUTO_ENDPOINT = 0x3001
JTAG_INTERACTIVE_ENDPOINT = 0x3081

class JtagAutoController(object):
    def __init__(self, hub):
        self.hub = hub
        self.f = self.hub.openEndpoint(JTAG_AUTO_ENDPOINT)

        self.buf = ""
        self.nibble = None
        self.expected_acks = 0

        pulses_per_baud = 0.2
        pulses_per_sec = hub.baud_rate * pulses_per_baud
        self.micros_per_pulse = 1000000.0 / pulses_per_sec

    def pulses_for_micros(self, micros):
        npulses = int((micros + self.micros_per_pulse - 1) / self.micros_per_pulse)
        npulses = max(npulses, 50)
        # print >>sys.stderr, micros, npulses
        return npulses

    def close(self):
        pass
        # print "close() not implemented"

    def _flush_buf(self):
        num_nibbles = 2 * len(self.buf)
        if self.nibble is not None:
            self.buf += chr(self.nibble)
            num_nibbles += 1
            self.nibble = None

        assert 0 <= num_nibbles < 256
        if num_nibbles:
            self.f.write(chr(num_nibbles) + self.buf)
            self.buf = ""
            self.expected_acks += 1

        self._wait_for_acks(128)

    def _wait_for_acks(self, max_acks_outstanding):
        if self.expected_acks > max_acks_outstanding:
            s = self.f.read(1024, timeout=0)
            # print "Got %d acks out of %d" % (len(s), self.expected_acks)
            assert len(s) <= self.expected_acks
            for c in s:
                assert c == '\x00', repr(c)
                self.expected_acks -= 1

        while self.expected_acks > max_acks_outstanding:
            nmore = self.expected_acks - max_acks_outstanding
            print "Waiting for %d more acks..." % nmore
            s = self.f.read(nmore, timeout=0)
            if not s:
                s = self.f.read(1)

            for c in s:
                assert c == '\x00', repr(c)
                self.expected_acks -= 1

        assert 0 <= self.expected_acks <= max_acks_outstanding, (self.expected_acks, max_acks_outstanding)

    def flush(self):
        self._flush_buf()
        self.f.flush()

    def pulse(self, tms, tdi, care_tdo, tdo_val):
        data = (tms << 3) | (tdi << 2) | (care_tdo << 1) | (tdo_val << 0)

        if self.nibble is None:
            self.nibble = data
            return

        c = chr((data << 4) | self.nibble)
        self.nibble = None
        self.buf += c

        if len(self.buf) >= 127:
            self._flush_buf()

    def join(self):
        self.flush()
        self._wait_for_acks(0)
        s = self.f.read(1024, timeout=0)
        assert not s, (len(s), repr(s))

