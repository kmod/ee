import functools
import os

from model import Assembly, BoardDef

class Parser(object):
    def __init__(self):
        self.included_files = []

    def parse(self, fn, scope, f=None):
        if f is None:
            f = open(fn)

        for l in f:
            l = l.strip()

            if '#' in l:
                l = l[:l.index('#')]

            if not l:
                continue

            newscope = False
            if l.endswith(':'):
                newscope = True
                l = l[:-1]

            args = l.split()
            cmd = args[0]
            del args[0]

            opts = dict(s.split('=') for s in args if '=' in s)
            args = [s for s in args if '=' not in s]

            print cmd, args, opts

            if cmd == 'end':
                return
            if cmd == 'include':
                relpath, = args
                assert not opts
                new_fn = os.path.join(os.path.dirname(fn), relpath)
                self.included_files.append(new_fn)
                self.parse(new_fn, scope)
                continue

            handler = scope.getHandler(cmd)
            r = handler(args, opts)
            if newscope:
                self.parse(fn, r, f)

class Scope(object):
    def __init__(self, **handlers):
        self.handlers = handlers

    def getHandler(self, name):
        assert name in self.handlers, (self, name, self.handlers.keys())
        return self.handlers[name]

class GlobalScope(Scope):
    def __init__(self):
        self.assemblies = []
        self.board_defs = {}

        super(GlobalScope, self).__init__(
                board=self.boardHandler,
                assembly=self.assemblyHandler,
                )

    def assemblyHandler(self, args, opts):
        assert not opts
        name, = args
        a = Assembly(name)
        self.assemblies.append(a)
        return Scope(
                board=functools.partial(a.addBoard, self.board_defs),
                assign=a.addAssignment,
                )

    def boardHandler(self, args, opts):
        assert not opts
        name, = args
        assert name not in self.board_defs, name
        b = BoardDef(name)
        self.board_defs[name] = b
        return Scope(
                socket=b.addSocket,
                router=b.addRouter,
                pin=b.addPin,
                jtag_entry=b.addJtagEntry,
                )

def parse(fn):
    global_scope = GlobalScope()
    p = Parser()
    p.parse(fn, global_scope)
    return global_scope.board_defs, global_scope.assemblies, p.included_files
