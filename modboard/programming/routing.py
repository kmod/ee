import collections
import re

from model import AssemblyPin, PinDef, RouterPin

class RoutingNetwork(object):
    def __init__(self, assem):
        self.a = assem

        self.used = set()

        self.routers = {}
        for boardname in assem.boards:
            boarddef = assem.boards[boardname].boarddef
            for r in boarddef.routers:
                self.routers["%s.%s" % (boardname, r)] = {} # maps output -> input

    def isAvailable(self, pin):
        assert isinstance(pin, AssemblyPin)
        return pin not in self.used

    def assign(self, rout, rin):
        assert isinstance(rout, RouterPin)

        rname = "%s.%s" % (rout.boardname, rout.routername)

        ports = self.routers[rname]
        assert rout.portname not in ports, rout

        if isinstance(rin, RouterPin):
            ports[rout.portname] = ('p', rin.portname)
        else:
            assert isinstance(rin, str)
            ports[rout.portname] = ('s', rin)

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

            rprev = self.a.getRouterPin(prev)
            rnext = self.a.getRouterPin(next)
            assert rprev.routername == rnext.routername

            rname = prev.boardname + '.' + rprev.routername
            self.assign(rprev, rnext)

            print "For %s, assigning %s (%s) = %s (%s)" % (rname, prev, rprev.portname, next, rnext.portname)

            prev = next
        # print self.routers

class Router(object):
    def __init__(self, output, assem):
        self.o = output
        self.a = assem

    def mapPin(self, pin):
        board, pin = pin.split('.', 1)
        boarddef = self.a.boards[board].boarddef
        pin = boarddef.pins[pin]
        assert isinstance(pin, PinDef)
        return AssemblyPin(board, pin.socket, pin.name)

    def flipPin(self, pin):
        assert isinstance(pin, AssemblyPin)
        # boarddef = self.a.boards[pin.boardname].boarddef
        conn = self.a.connections[pin.boardname].get(pin.socket)
        if not conn:
            return None
        nextboard, nextboard_socket = conn
        return AssemblyPin(nextboard, nextboard_socket, pin.pinname)

    def route(self, target_name, source_name):
        target = self.mapPin(target_name)
        source = self.mapPin(source_name)
        print
        print "Routing", target, "from", source

        seen = set()
        q = collections.deque()
        def add(curpath, next):
            if next is None:
                return
            assert isinstance(next, AssemblyPin)
            if not self.o.isAvailable(next):
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

            flipped = self.flipPin(last)
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

    router = Router(rn, assem)

    # Route user-specified signals:
    for a in assem.assignments:
        target, source = a
        if '.' in source:
            path = router.route(target, source)
            rn.addPath(path)
        else:
            assert source in ('0', '1'), source
            apin = router.mapPin(target)
            assert apin
            other = router.flipPin(apin)
            assert other
            rpin = assem.getRouterPin(other)
            assert rpin

            assert rn.isAvailable(apin)
            assert rn.isAvailable(other)
            rn.used.add(apin)
            rn.used.add(other)
            rn.assign(rpin, "1'b" + source)

    # Match the 'default' attribute of all non-router pins:
    for boardname in assem.boards:
        boarddef = assem.boards[boardname].boarddef
        for sdef in boarddef.sockets.itervalues():
            for pdef in sdef.pins.itervalues():
                if 'port' in pdef.attrs:
                    continue
                # print pdef

                apin = AssemblyPin(boardname, pdef.socket, pdef.name)
                if not rn.isAvailable(apin):
                    continue

                default = pdef.attrs.get('default', 'z')
                if default == '0z':
                    default = 'z'
                # print apin, default

                otherpin = router.flipPin(apin)
                if otherpin is None:
                    assert default == 'z', (default, apin)
                    continue
                assert rn.isAvailable(otherpin)
                rn.used.add(apin)
                rn.used.add(otherpin)

                rpin = assem.getRouterPin(otherpin)
                if not rpin:
                    assert default == 'z'
                    otherdefault = assem.boards[otherpin.boardname].boarddef.sockets[otherpin.socket].pins[otherpin.pinname].attrs.get('default', 'z')
                    assert otherdefault == 'z' or otherdefault == '0z', (otherpin, otherdefault)
                    continue
                # print otherpin, rpin

                assert len(default) == 1
                verilog_default = "1'b" + default

                print "Setting %s to its default of %s, using its connection at %s" % (apin, default, rpin)
                rn.assign(rpin, verilog_default)

    # Set all router pins that are left to high-z:
    for boardname in assem.boards:
        boarddef = assem.boards[boardname].boarddef
        for rname, r in boarddef.routers.items():
            for socket, pinname in r.ports.values():
                apin = AssemblyPin(boardname, socket, pinname)
                if not rn.isAvailable(apin):
                    continue
                rn.used.add(apin)

                rpin = assem.getRouterPin(apin)
                assert rpin
                rn.assign(rpin, "1'bz")

    return rn

