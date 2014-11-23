import time

from controllers import BitbangController
from hub import ControllerHub

_PORT_IDS = {
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

class Jtagusaur2BitbangController(object):
    def __init__(self, hub):
        self.ctlr = BitbangController(hub)

    def mode(self, port, pin, dir):
        port = port.upper()
        assert port in "BCD"
        pin = int(pin)
        assert 0 <= pin < 8
        assert dir in 'io'
        val = (1 if dir == 'o' else 0)

        port_id = _PORT_IDS["DDR" + port]

        self.ctlr.writeBit(port_id, pin, val)

    def write(self, port, pin, val):
        port = port.upper()
        assert port in "BCD"
        pin = int(pin)
        assert 0 <= pin < 8
        assert val in (0, 1)

        port_id = _PORT_IDS["PORT" + port]

        self.ctlr.writeBit(port_id, pin, val)

    def read(self, port):
        port = port.upper()
        assert port in "BCD"

        port_id = _PORT_IDS["PIN" + port]

        val = self.ctlr.read(port_id)
        return val

def main():
    hub = ControllerHub(br=1000000)
    ctlr = Jtagusaur2BitbangController(hub)
    ctlr.mode("b", 5, 'o')
    ctlr.write('b', 5, 0)
    time.sleep(.1)
    for i in xrange(10):
        ctlr.write('b', 5, 1)
        time.sleep(0.2)
        ctlr.write('b', 5, 0)
        time.sleep(0.2)

if __name__ == "__main__":
    main()
