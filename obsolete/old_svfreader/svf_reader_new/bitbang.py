import sys
import time

from hub import ControllerHub

class BitbangController(object):
    def __init__(self, stream):
        self.stream = stream

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

PORT_IDS = {
        "DDRB" : 0,
        "DDRC" : 1,
        "DDRD" : 2,
        "PINB" : 3,
        "PINC" : 4,
        "PIND" : 5,
        "PORTB" : 6,
        "PORTC" : 7,
        "PORTD" : 8,
        }

def main():
    hub = ControllerHub(br=1000000)
    stream = hub.openEndpoint(0x1000)
    ctlr = BitbangController(stream)

    while True:
        l = sys.stdin.readline()
        if not l:
            break

        l = l.strip()
        if not l:
            continue
        if l.startswith('#'):
            continue

        args = l.split()
        cmd, args = args[0], args[1:]

        if cmd in ("sleep", "wait"):
            amount, = args
            amount = float(amount)
            time.sleep(amount)

        elif cmd in ('pinmode', 'mode'):
            port, pin, dir = args
            port = port.upper()
            assert port in "BCD"
            pin = int(pin)
            assert 0 <= pin < 8
            assert dir in 'io'
            val = (1 if dir == 'o' else 0)

            port_id = PORT_IDS["DDR" + port]

            ctlr.writeBit(port_id, pin, val)
        elif cmd in ('set', 'write'):
            port, pin, val = args
            port = port.upper()
            assert port in "BCD"
            pin = int(pin)
            assert 0 <= pin < 8
            assert val in '01'
            val = int(val)

            port_id = PORT_IDS["PORT" + port]

            ctlr.writeBit(port_id, pin, val);
        elif cmd == "read":
            port, = args
            port = port.upper()
            assert port in "BCD"

            port_id = PORT_IDS["PIN" + port]

            val = ctlr.read(port_id)
            print "0b%s" % bin(val)[2:].rjust(8, '0')
        elif cmd == "debug":
            b, = args
            b = int(b, 0)
            stream.write(chr(b))

        else:
            raise Exception(cmd, args)

if __name__ == "__main__":
    main()
