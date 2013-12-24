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
        self.jtag_entry = None

        self.sockets[None] = (-1, {})

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
        self.routers[name] = (jtag, part)

    def addPin(self, args, opts):
        name, = args
        socket = None
        if '.' in name:
            socket, name = name.split('.')
        assert socket in self.sockets

        pins = self.sockets[socket][1]
        assert name not in pins
        pins[name] = opts

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
        self.assignments = {}

    def addBoard(self, args, opts):
        assert not opts
        boardname, id, connection = args
        b = board_defs[boardname]

        if connection != "unconnected":
            if '.' in connection:
                conn_id, conn_socket = connection.split('.')
            else:
                conn_id, conn_socket = connection, None
            assert conn_id in self.boards
            conn_b = self.boards[conn_id][0]
            assert conn_socket in conn_b.sockets
        self.boards[id] = (b, connection)

    def addAssignment(self, args, opts):
        assert opts.pop('') == ''
        assert not opts
        val = ' '.join(args[1:])

        target = args[0]
        board_id, name = target.split('.')
        assert board_id in self.boards

        assert target not in self.assignments
        self.assignments[target] = val

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

    assert len(assemblies) == 1

    of = open(out_fn, 'w')
    print >>of, "%s: %s" % (out_fn, ''.join(p.included_files))
    of.close()
main()

