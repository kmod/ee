import os
import re
import sys

class Board(object):
    def __init__(self, name):
        self.name = name
        self.pins = {}

    def line(self, l):
        tokens = l.split()

        conn = None
        if len(tokens) == 3:
            conn = tokens[0]
            del tokens[0]
        assert len(tokens) == 2

        port, name = tokens
        assert port in ("g0", "grst") or re.match("[a-e][0-3]$", port)

        d = self.pins.setdefault(conn, {})
        assert port not in d
        d[port] = name

    def process(self):
        for conn, ports in self.pins.iteritems():
            for c in "abcde":
                for n in "0123":
                    assert (c+n) in ports, (self.name, conn, c+n)

def main():
    # defs_fn = os.path.join(os.path.dirname(__file__), "defs.mb")
    fn = sys.argv[1]

    with open(fn) as f:
        state = None

        while True:
            l = f.readline()
            if not l:
                break
            l = l.rstrip()

            if not l:
                continue

            print repr(l)
            if not l[0].isspace():
                cmd = l.split()[0]
                print cmd

                if cmd == "board":
                    assert l[-1] == ':'
                    cmd, name = l[:-1].split()
                    if state: state.process()
                    state = Board(name)
                else:
                    raise Exception(cmd)
            else:
                state.line(l.strip())
        if state: state.process()

if __name__ == "__main__":
    main()
