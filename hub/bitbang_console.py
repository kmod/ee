import sys
import time
import readline
readline

from hub import ControllerHub
from jtagusaur_bitbang import Jtagusaur2BitbangController

def main():
    hub = ControllerHub(br=1000000)
    ctlr = Jtagusaur2BitbangController(hub)

    while True:
        try:
            l = raw_input()
        except EOFError:
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
            ctlr.mode(port, pin, dir)
        elif cmd in ('set', 'write'):
            port, pin, val = args
            port = port.upper()
            assert port in "BCD"
            pin = int(pin)
            assert 0 <= pin < 8
            assert val in '01'
            val = int(val)

            ctlr.write(port, pin, val)
        elif cmd == "read":
            port, = args
            port = port.upper()
            assert port in "BCD"

            val = ctlr.read(port)
            print "0b%s" % bin(val)[2:].rjust(8, '0')
        else:
            raise Exception(cmd, args)

if __name__ == "__main__":
    main()
