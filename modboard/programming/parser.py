import os

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
