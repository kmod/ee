import sys
import time

from hub import ControllerHub

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

if __name__ == "__main__":
    hub = ControllerHub(br=1000000)
    stream = hub.openEndpoint(0x1000)

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

            data = 'w' + chr((port_id << 4) + (pin << 1) + val)
            stream.write(data)

            check = stream.read(1)
            assert check == '\x00', repr(check)

        elif cmd in ('set', 'read'):
            port, pin, val = args
            port = port.upper()
            assert port in "BCD"
            pin = int(pin)
            assert 0 <= pin < 8
            assert val in '01'
            val = int(val)

            port_id = PORT_IDS["PORT" + port]

            data = 'w' + chr((port_id << 4) + (pin << 1) + val)
            stream.write(data)

            check = stream.read(1)
            assert check == '\x00', repr(check)

        elif cmd == "read":
            port, = args
            port = port.upper()
            assert port in "BCD"

            port_id = PORT_IDS["PIN" + port]
            data = 'r' + chr(port_id)

            stream.write(data)
            check = stream.read(1)
            assert check == '\x00', repr(check)
            val = ord(stream.read(1))
            print "0b%s" % bin(val)[2:].rjust(8, '0')

        elif cmd == "debug":
            b, = args
            b = int(b, 0)
            stream.write(chr(b))

        else:
            raise Exception(cmd, args)
