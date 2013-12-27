import collections
import re
import sys

import parser

class Output(object):
    def __init__(self, assem):
        self.a = assem

        self.routers = {}
        for boardname in assem.boards:
            boarddef = assem.boards[boardname][0]
            for r in boarddef.routers:
                self.routers["%s.%s" % (boardname, r)] = {}

    def available(self, (boardname, socket, pinname)):
        r = self.a.getRouter((boardname, socket, pinname))
        if not r:
            return True
        print r
        1/0
        return 1

class Router(object):
    def __init__(self, output, assem):
        self.o = output
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

            if last[2] not in ('g0', 'grst'):
                assert re.match("[a-e][0-3]", last[2]), last

                # print pin_attrs
                # if 'port' in pin_attrs:
                router = self.a.getRouter(last)
                if router:
                    for dest_socket, dest_pin in router[2].values():
                        add(curpath, (last[0], dest_socket, dest_pin))

        raise Exception("Could not route %s to %s!" % (source, target))

def process(assem):
    o = Output(assem)

    r = Router(o, assem)
    for a in assem.assignments:
        target, source = a
        path = r.route(target, source)
        print path
    return o

def main():
    in_fn, out_fn = sys.argv[1:]

    board_defs, assemblies = parser.parse(in_fn)

    for board_name, b in board_defs.items():
        for sid, sdefs in b.sockets.values():
            for c in "abcde":
                for n in "0123":
                    assert (c+n) in sdefs, (board_name, sid)

    for assem in assemblies:
        print
        print "Processing assembly", assem.name
        process(assem)

    # output(modules, out_fn)

    # of = open(out_fn, 'w')
    # print >>of, "%s: %s" % (out_fn, ''.join(p.included_files))
    # of.close()
main()

