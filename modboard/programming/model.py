import collections

JtagEntry = collections.namedtuple("JtagEntry", ["jtag"])
SocketDef = collections.namedtuple("SocketDef", ["name", "jtag", "pins"])
RouterDef = collections.namedtuple("RouterDef", ["name", "jtag", "part", "ports"])
AssemblyBoard = collections.namedtuple("AssemblyBoard", ["name", "boarddef"])
PinDef = collections.namedtuple("PinDef", ["socket", "name", "attrs"])

AssemblyPin = collections.namedtuple("AssemblyPin", ["boardname", "socket", "pinname"])
def pinRepr(pin):
    return repr((pin.boardname, pin.socket, pin.pinname))
AssemblyPin.__repr__ = pinRepr
del pinRepr

RouterPin = collections.namedtuple("RouterPin", ["boardname", "routername", "portname"])

class BoardDef(object):
    def __init__(self, name):
        self.name = name
        self.sockets = {}
        self.routers = {}
        self.pins = {}
        self.jtag_entry = None
        self.jtags = {}

        self.sockets[None] = SocketDef("", 0, {})

    def _setPin(self, name, pin):
        assert isinstance(pin, PinDef)
        assert name not in self.pins, (self.name, name)
        self.pins[name] = pin

    def _addJtag(self, obj, jtag_idx):
        assert jtag_idx == len(self.jtags) + 1, "Please put jtags in order for now"
        self.jtags[jtag_idx] = obj

    def addJtagEntry(self, args, opts):
        assert not args
        jtag = int(opts.pop('jtag'))
        assert jtag > 0

        assert not self.jtag_entry
        self.jtag_entry = JtagEntry(jtag)
        self._addJtag(self.jtag_entry, jtag)

    def addSocket(self, args, opts):
        jtag = int(opts.pop('jtag'))
        assert jtag > 0
        assert not opts, opts

        name, = args
        self.sockets[name] = SocketDef(name, jtag, {})
        self._addJtag(self.sockets[name], jtag)

    def addRouter(self, args, opts):
        jtag = int(opts.pop('jtag'))
        assert jtag > 0
        part = opts.pop('part')
        assert not opts, opts

        name, = args
        self.routers[name] = RouterDef(name, jtag, part, {})
        self._addJtag(self.routers[name], jtag)

    def addPin(self, args, opts):
        fullname, = args
        socket = None

        name = fullname
        if '.' in fullname:
            socket, name = fullname.split('.')

        p = PinDef(socket, name, opts)
        self._setPin(fullname, p)
        if "alias" in opts:
            self._setPin(opts['alias'], p)

        if "port" in opts:
            router_name, router_pin = opts['port'].split('.')
            router = self.routers[router_name]
            assert router_pin not in router.ports
            router.ports[router_pin] = (socket, name)

        assert socket in self.sockets
        pins = self.sockets[socket].pins
        assert name not in pins
        pins[name] = p

class Assembly(object):
    def __init__(self, name, boarddefs):
        self.name = name
        self.boarddefs = boarddefs

        self.boards = {}
        self.assignments = []
        self.connections = {}

    def addBoard(self, args, opts):
        assert not opts
        boardtype, name, connection = args
        assert name not in self.boards

        boarddef = self.boarddefs[boardtype]
        d = self.connections.setdefault(name, {})
        if connection != "unconnected":
            if '.' in connection:
                conn_id, conn_socket = connection.split('.')
            else:
                conn_id, conn_socket = connection, None
            assert conn_id in self.boards, conn_id
            # conn_boarddef = self.getBoardDef(self.boards[conn_id].type)
            # assert conn_socket in conn_boarddef.sockets
            assert conn_socket not in self.connections[conn_id], (boardtype, conn_id, conn_socket)

            d[None] = (conn_id, conn_socket)
            self.connections[conn_id][conn_socket] = (name, None)
        self.boards[name] = AssemblyBoard(name, boarddef)

    def addAssignment(self, args, opts):
        assert opts.pop('') == ''
        assert not opts
        val = ' '.join(args[1:])

        target = args[0]
        board_id, name = target.split('.', 1)
        assert board_id in self.boards

        assert not [1 for (t, s) in self.assignments if t == target]
        self.assignments.append((target, val))

    def getPinAttrs(self, pin):
        assert isinstance(pin, AssemblyPin)
        boarddef = self.boards[pin.boardname].boarddef
        pin_attrs = boarddef.sockets[pin.socket].pins[pin.pinname].attrs
        return pin_attrs

    def getRouterPin(self, pin):
        pin_attrs = self.getPinAttrs(pin)
        if 'port' not in pin_attrs:
            return None
        port = pin_attrs['port']
        rname, portname = port.split('.')
        return RouterPin(pin.boardname, rname, portname)

    def getRouterDef(self, pin):
        pin_attrs = self.getPinAttrs(pin)

        if 'port' not in pin_attrs:
            return None

        router_name, router_pin = pin_attrs['port'].split('.')
        routerdef = self.boards[pin.boardname].boarddef.routers[router_name]
        return routerdef
