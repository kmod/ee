import cStringIO
import collections
import re
import sys

from model import AssemblyPin
import parser

class RoutingNetwork(object):
    def __init__(self, assem):
        self.a = assem

        self.assignments = {}
        # self.routers = {}
        # for boardname in assem.boards:
            # boarddef = assem.boards[boardname][0]
            # for r in boarddef.routers:
                # self.routers["%s.%s" % (boardname, r)] = {}

    def available(self, pin):
        return pin not in self.assignments
        r = self.a.getRouter(pin)
        if not r:
            return True
        print r
        1/0
        return 1

    def addPath(self, path):
        print path
        1/0

class Router(object):
    def __init__(self, output, assem):
        self.o = output
        self.a = assem

    def _mapPin(self, pin):
        board, pin = pin.split('.', 1)
        boarddef = self.a.boards[board][0]
        pin = boarddef.pins[pin]
        return AssemblyPin(board, pin[0], pin[1])

    def _flipPin(self, pin):
        assert isinstance(pin, AssemblyPin)
        # boarddef = self.a.boards[pin.boardname][0]
        conn = self.a.connections[pin.boardname].get(pin.socket)
        if not conn:
            return None
        nextboard, nextboard_socket = conn
        return AssemblyPin(nextboard, nextboard_socket, pin.pinname)

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
            assert isinstance(next, AssemblyPin)
            if not self.o.available(next):
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

            if last.pinname not in ('g0', 'grst'):
                assert re.match("[a-e][0-3]", last.pinname), last

                # print pin_attrs
                # if 'port' in pin_attrs:
                router = self.a.getRouter(last)
                if router:
                    for dest_socket, dest_pin in router[2].values():
                        add(curpath, AssemblyPin(last.boardname, dest_socket, dest_pin))

        raise Exception("Could not route %s to %s!" % (source, target))

def process(assem):
    rn = RoutingNetwork(assem)

    r = Router(rn, assem)
    for a in assem.assignments:
        target, source = a
        path = r.route(target, source)
        rn.addPath(path)
    return rn

def main():
    in_fn, out_fn = sys.argv[1:]

    board_defs, assemblies, included_files = parser.parse(in_fn)

    for board_name, b in board_defs.items():
        for sid, sdefs in b.sockets.values():
            for c in "abcde":
                for n in "0123":
                    assert (c+n) in sdefs, (board_name, sid)

    of = cStringIO.StringIO()
    print >>of, "%s: %s" % (out_fn, ''.join(included_files))

    for assem in assemblies:
        print
        print "Processing assembly", assem.name
        rn = process(assem)
        doOutput(rn, of)

    output = of.str()

    with open(out_fn, 'w') as of:
        of.write(output)
main()

