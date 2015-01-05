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
    class Pin(object):
        def __init__(self, ctlr, port, pin_idx):
            self.ctlr = ctlr
            self.port = port
            self.pin_idx = pin_idx

        def mode(self, dir):
            self.ctlr.mode(self.port, self.pin_idx, dir)

        def write(self, val):
            self.ctlr.write(self.port, self.pin_idx, val)

        def read(self):
            val = self.ctlr.read(self.port)
            return (val >> self.pin_idx) & 1

    def __init__(self, hub, max_acks_outstanding=0):
        if isinstance(hub, int):
            # interpreting as a baud rate
            hub = ControllerHub(hub)

        self.ctlr = BitbangController(hub, max_acks_outstanding=max_acks_outstanding)

        self.pins = {}
        for port in "BCD":
            for pin in range(0, 8):
                pin_obj = self.Pin(self, port, pin)
                pin_name = "%s%d" % (port, pin)

                setattr(self, pin_name, pin_obj)
                self.pins[pin_name] = pin_obj

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

    pin = ctlr.B5
    pin.mode('o')
    pin.write(0)
    time.sleep(.1)
    for i in xrange(10):
        pin.write(1)
        time.sleep(0.2)
        pin.write(0)
        time.sleep(0.2)

if __name__ == "__main__":
    main()
