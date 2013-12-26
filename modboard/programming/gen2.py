import collections
import re
import sys

import parser

class Scope(object):
    def __init__(self, **handlers):
        self.handlers = handlers

    def getHandler(self, name):
        assert name in self.handlers, (self, name, self.handlers.keys())
        return self.handlers[name]

class BoardDef(object):
    def __init__(self, name):
        self.name = name
        self.sockets = {}
        self.routers = {}
        self.pins = {}
        self.jtag_entry = None

        self.sockets[None] = (-1, {})

    def _setPin(self, name, pin):
        assert name not in self.pins, (self.name, name)
        self.pins[name] = pin

    def addJtagEntry(self, args, opts):
        assert not args
        jtag = int(opts.pop('jtag'))
        assert jtag > 0

        assert not self.jtag_entry
        self.jtag_entry = (jtag,)

    def addSocket(self, args, opts):
        jtag = int(opts.pop('jtag'))
        assert jtag > 0
        assert not opts, opts

        name, = args
        self.sockets[name] = (jtag, {})

    def addRouter(self, args, opts):
        jtag = int(opts.pop('jtag'))
        assert jtag > 0
        part = opts.pop('part')
        assert not opts, opts

        name, = args
        self.routers[name] = (jtag, part, {})

    def addPin(self, args, opts):
        fullname, = args
        socket = None

        name = fullname
        if '.' in fullname:
            socket, name = fullname.split('.')

        p = (socket, name, opts)
        self._setPin(fullname, p)
        if "alias" in opts:
            self._setPin(opts['alias'], p)

        if "port" in opts:
            router_name, router_pin = opts['port'].split('.')
            router = self.routers[router_name]
            assert router_pin not in router[2]
            router[2][router_pin] = (socket, name)

        assert socket in self.sockets
        pins = self.sockets[socket][1]
        assert name not in pins
        pins[name] = p

# TODO not as a global
board_defs = {}
def boardHandler(args, opts):
    assert not opts
    name, = args
    assert name not in board_defs, name
    b = BoardDef(name)
    board_defs[name] = b
    return Scope(
            socket=b.addSocket,
            router=b.addRouter,
            pin=b.addPin,
            jtag_entry=b.addJtagEntry,
            )

class Assembly(object):
    def __init__(self, name):
        self.name = name

        self.boards = {}
        self.assignments = []
        self.connections = {}

    def addBoard(self, args, opts):
        assert not opts
        boardname, id, connection = args
        assert id not in self.boards
        b = board_defs[boardname]

        d = self.connections.setdefault(id, {})
        if connection != "unconnected":
            if '.' in connection:
                conn_id, conn_socket = connection.split('.')
            else:
                conn_id, conn_socket = connection, None
            assert conn_id in self.boards
            conn_b = self.boards[conn_id][0]
            assert conn_socket in conn_b.sockets
            assert conn_socket not in self.connections[conn_id], (boardname, conn_id, conn_socket)

            d[None] = (conn_id, conn_socket)
            self.connections[conn_id][conn_socket] = (id, None)
        self.boards[id] = (b,)

    def addAssignment(self, args, opts):
        assert opts.pop('') == ''
        assert not opts
        val = ' '.join(args[1:])

        target = args[0]
        board_id, name = target.split('.', 1)
        assert board_id in self.boards

        assert not [1 for (t, s) in self.assignments if t == target]
        self.assignments.append((target, val))

    def process(self):
        r = Router(self)
        for a in self.assignments:
            target, source = a
            path = r.route(target, source)
            print path

class Router(object):
    def __init__(self, assem):
        self.a = assem

    def _mapPin(self, pin):
        board, pin = pin.split('.', 1)
        boarddef = self.a.boards[board][0]
        pin = boarddef.pins[pin]
        return (board, pin[0], pin[1])

    def _flipPin(self, pin):
        board, socket, pin = pin
        boarddef = self.a.boards[board][0]
        conn = self.a.connections[board].get(socket)
        if not conn:
            return None
        nextboard, nextboard_socket = conn
        return nextboard, nextboard_socket, pin

    def route(self, target, source):
        target = self._mapPin(target)
        source = self._mapPin(source)
        print
        print "Routing", target, "from", source

        seen = set()
        q = collections.deque()
        def add(curpath, next):
            if next is None:
                return
            if next not in seen:
                seen.add(next)
                q.append(curpath + [next])
        add([], target)

        while q:
            curpath = q.popleft()

            # print curpath
            last = curpath[-1]
            if last == source:
                return curpath

            flipped = self._flipPin(last)
            add(curpath, flipped)

            if last[2] not in ('g0', 'grst'):
                assert re.match("[a-e][0-3]", last[2]), last

                boarddef = self.a.boards[last[0]][0]
                pin_attrs = boarddef.sockets[last[1]][1][last[2]][2]
                # print pin_attrs
                if 'port' in pin_attrs:
                    router_name, router_pin = pin_attrs['port'].split('.')
                    router = boarddef.routers[router_name]

                    for dest_socket, dest_pin in router[2].values():
                        add(curpath, (last[0], dest_socket, dest_pin))

        raise Exception("Could not route %s to %s!" % (source, target))

assemblies = []
def assemblyHandler(args, opts):
    assert not opts
    name, = args
    a = Assembly(name)
    assemblies.append(a)
    return Scope(
            board=a.addBoard,
            assign=a.addAssignment,
            )

def main():
    in_fn, out_fn = sys.argv[1:]

    global_scope = Scope(
            board=boardHandler,
            assembly=assemblyHandler,
            )
    p = parser.Parser()
    p.parse(in_fn, global_scope)

    for board_name, b in board_defs.items():
        for sid, sdefs in b.sockets.values():
            for c in "abcde":
                for n in "0123":
                    assert (c+n) in sdefs, (board_name, sid)

    for assem in assemblies:
        print
        print "Processing assembly", assem.name
        assem.process()

    # output(modules, out_fn)

    # of = open(out_fn, 'w')
    # print >>of, "%s: %s" % (out_fn, ''.join(p.included_files))
    # of.close()
main()

