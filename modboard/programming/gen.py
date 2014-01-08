#!/usr/bin/env python

import cStringIO
import collections
import re
import sys

from model import AssemblyPin, PinDef
from output import doOutput, Rewriter
from routing import route
import parser

def main():
    in_fn, out_fn = sys.argv[1:]

    board_defs, assemblies, included_files = parser.parse(in_fn)

    for board_name, b in board_defs.items():
        for sname, sid, sdefs in b.sockets.values():
            for c in "abcde":
                for n in "0123":
                    assert (c+n) in sdefs, (c+n, board_name, sid)

    of = cStringIO.StringIO()
    print >>of, "%s: %s" % (out_fn, ''.join(included_files))

    for assem in assemblies:
        print
        print "Processing assembly", assem.name
        rn = route(assem)
        doOutput(assem, rn, of)

    output = of.getvalue()

    with Rewriter(out_fn) as of:
        of.write(output)
main()

