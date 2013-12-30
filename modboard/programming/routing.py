import collections
import re

from model import AssemblyPin, PinDef

class RoutingNetwork(object):
    def __init__(self, assem):
        self.a = assem

        self.used = set()
        self.assignments = {} # maps output -> input

        self.routers = {}
        for boardname in assem.boards:
            boarddef = assem.boards[boardname].boarddef
            for r in boarddef.routers:
                self.routers["%s.%s" % (boardname, r)] = {}

    def available(self, pin):
        return pin not in self.used
        """
        r = self.a.getRouter(pin)
        if not r:
            return True
        print r
        1/0
        return 1
        """

    def addPath(self, path):
        assert len(path) >= 2

        print "adding path", path

        for n in path:
            assert n not in self.used
            self.used.add(n)

        prev = path[0]
        for next in path[1:]:
            if prev.boardname != next.boardname:
                assert prev.pinname == next.pinname
                assert self.a.connections[prev.boardname][prev.socket] == (next.boardname, next.socket)
                prev = next
                continue

            assert prev not in self.assignments
            self.assignments[prev] = next

            rprev = self.a.getRouterPin(prev)
            rnext = self.a.getRouterPin(next)
            assert rprev.routername == rnext.routername

            rname = prev.boardname + '.' + rprev.routername
            ports = self.routers[rname]
            assert rprev.portname not in ports
            ports[rprev.portname] = rnext.portname

            print "For %s, assigning %s (%s) = %s (%s)" % (rname, prev, rprev.portname, next, rnext.portname)

            prev = next
        # print self.assignments
        # print self.routers

class Router(object):
    def __init__(self, output, assem):
        self.o = output
        self.a = assem

    def _mapPin(self, pin):
        board, pin = pin.split('.', 1)
        boarddef = self.a.boards[board].boarddef
        pin = boarddef.pins[pin]
        assert isinstance(pin, PinDef)
        return AssemblyPin(board, pin.socket, pin.name)

    def _flipPin(self, pin):
        assert isinstance(pin, AssemblyPin)
        # boarddef = self.a.boards[pin.boardname].boarddef
        conn = self.a.connections[pin.boardname].get(pin.socket)
        if not conn:
            return None
        nextboard, nextboard_socket = conn
        return AssemblyPin(nextboard, nextboard_socket, pin.pinname)

    def route(self, target_name, source_name):
        target = self._mapPin(target_name)
        source = self._mapPin(source_name)
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
                router = self.a.getRouterDef(last)
                if router:
                    for dest_socket, dest_pin in router.ports.values():
                        add(curpath, AssemblyPin(last.boardname, dest_socket, dest_pin))

        raise Exception("Could not route %s to %s!" % (source_name, target_name))

def route(assem):
    rn = RoutingNetwork(assem)

    r = Router(rn, assem)
    for a in assem.assignments:
        target, source = a
        path = r.route(target, source)
        rn.addPath(path)
    return rn
