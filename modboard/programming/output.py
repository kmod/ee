import cStringIO
import os

from model import RouterDef, SocketDef, JtagEntry

class Rewriter(object):
    def __init__(self, fn):
        self.fn = fn
        self.s = None

    def __enter__(self):
        self.s = cStringIO.StringIO()
        return self.s

    def __exit__(self, type, val, tb):
        if not os.path.exists(self.fn):
            orig = None
        else:
            orig = open(self.fn).read()

        s = self.s.getvalue()
        if s != orig:
            with open(self.fn, 'w') as f:
                f.write(s)
        return False

def getChain(assem):
    jtag_entry_boards = [(boardname, abrd.boarddef.jtag_entry) for boardname, abrd in assem.boards.iteritems() if abrd.boarddef.jtag_entry]

    if len(jtag_entry_boards) == 0:
        raise Exception("Error: no boards have jtag entries so this assembly is not programmable!")
    if len(jtag_entry_boards) > 1:
        raise Exception("Too many jtag entry boards; found %s" % jtag_entry_boards)

    chain = []

    jtag_entry, = jtag_entry_boards

    cur_board = jtag_entry[0]
    cur_idx = jtag_entry[1].jtag

    while True:
        print "At", cur_board, cur_idx
        new_idx = cur_idx + 1

        boarddef = assem.boards[cur_board].boarddef
        if new_idx not in boarddef.jtags:
            # Wrapping around to the main connector:
            assert new_idx == len(boarddef.jtags) + 1
            connections = assem.connections[cur_board]
            if None not in connections:
                print "Skipping connector for %s; it better be bypassed" % cur_board
                cur_board, cur_idx = cur_board, 0
            else:
                new_board, new_board_socket = connections[None]
                new_board_socket = assem.boards[new_board].boarddef.sockets[new_board_socket]
                cur_board, cur_idx = new_board, new_board_socket.jtag
        else:
            jobj = boarddef.jtags[new_idx]
            if isinstance(jobj, RouterDef):
                chain.append("%s.%s" % (cur_board, jobj.name))
                cur_board, cur_idx = cur_board, new_idx
            elif isinstance(jobj, SocketDef):
                # TODO duplicated with the connector code above
                connections = assem.connections[cur_board]
                if jobj.name not in connections:
                    print "Skipping socket %s for %s; it better be bypassed" % (jobj.name, cur_board)
                    cur_board, cur_idx = cur_board, new_idx
                else:
                    new_board, new_board_socket = connections[jobj.name]
                    new_board_socket = assem.boards[new_board].boarddef.sockets[new_board_socket]
                    cur_board, cur_idx = new_board, new_board_socket.jtag
            elif isinstance(jobj, JtagEntry):
                break
            else:
                raise Exception(jobj)
    return chain

def doOutput(assem, rn, of):
    print assem, rn, of

    aname = assem.name
    build_dir = aname + ".mbbuild"
    if not os.path.isdir(build_dir):
        os.makedirs(build_dir)

    def getRouterDef(rname):
        boardname, rname = rname.split('.')
        boarddef = assem.boards[boardname].boarddef
        return boarddef.routers[rname]

    jeds = []

    for rname, router in rn.routers.items():
        base_fn = os.path.join(build_dir, rname)
        routerdef = getRouterDef(rname)

        tmpdir = os.path.join(build_dir, "xst_%s/projnav.tmp" % rname)
        if not os.path.isdir(tmpdir):
            os.makedirs(tmpdir)

        print rname, router
        with Rewriter("%s.v" % base_fn) as f:
            print >>f, "`timescale 1ns / 1ps"
            print >>f
            print >>f, "module main("

            first = 1
            for target, (source_type, source) in router.iteritems():
                if not first:
                    print >>f, ','
                first = 0
                if source_type == 'p':
                    print >>f, "  input p%s," % source
                print >>f, "  output p%s" % target,
            print >>f, ");"

            print >>f

            for target, (source_type, source) in router.iteritems():
                if source_type == 'p':
                    print >>f, "  assign p%s = p%s;" % (target, source)
                elif source_type == 's':
                    print >>f, "  assign p%s = %s;" % (target, source)
                else:
                    raise Exception(source_type)

            print >>f, "endmodule"

        with Rewriter("%s.xst" % base_fn) as f:
            print >>f, ("""
set -tmpdir "xst_%(rname)s/projnav.tmp"
set -xsthdpdir "xst_%(rname)s"
run
-ifn %(rname)s.prj
-ifmt mixed
-ofn %(rname)s.ngc
-ofmt NGC
-p xbr
-top main
-opt_mode Speed
-opt_level 1
-iuc NO
-keep_hierarchy Yes
-netlist_hierarchy As_Optimized
-rtlview Yes
-hierarchy_separator /
-bus_delimiter <>
-case Maintain
-verilog2001 YES
-fsm_extract YES -fsm_encoding Auto
-safe_implementation No
-mux_extract Yes
-resource_sharing YES
-iobuf YES
-pld_mp YES
-pld_xp YES
-pld_ce YES
-wysiwyg NO
-equivalent_register_removal YES
""" % dict(rname=rname)).strip()

            with Rewriter("%s.prj" % base_fn) as f:
                print >>f, 'verilog work "%s.v"' % rname

            with Rewriter("%s.ucf" % base_fn) as f:
                pins = []
                for target, (source_type, source) in router.iteritems():
                    if source_type == 'p':
                        pins.append(source)
                    pins.append(target)

                for pin in pins:
                    print >>f, 'net "p%s" LOC="%s" | IOSTANDARD = "LVCMOS33";' % (pin, pin)

        translate_opts = {
        }
        fit_opts = {
                '-keepio': '',
                '-iostd': 'LVCMOS33',
                '-unused': 'float',
                '-terminate': 'float',
        }
        print >>of
        print >>of, "%s.ngc: %s.v" % (base_fn, base_fn)
        print >>of, "\tcd %s; $(ISE_BIN)/xst -intstyle ise -ifn %s.xst" % (build_dir, rname)
        print >>of, "%s.ngd: %s.ngc" % (base_fn, base_fn)
        print >>of, "\tcd %s; $(ISE_BIN)/ngdbuild -uc %s.ucf -p %s %s.ngc %s.ngd" % (build_dir, rname, routerdef.part, rname, rname)
        print >>of, "%s.vm6: %s.ngd" % (base_fn, base_fn)
        print >>of, "\tcd %s; $(ISE_BIN)/cpldfit %s -p %s %s.ngd" % (build_dir, ' '.join('%s %s' % i for i in fit_opts.items()), routerdef.part, rname)
        print >>of, "%s.jed: %s.vm6" % (base_fn, base_fn)
        print >>of, "\tcd %s; $(ISE_BIN)/hprep6 -i %s.vm6" % (build_dir, rname)
        jeds.append(base_fn + ".jed")

# %.vm6: %.ngd
		# $(ISE_BIN)/cpldfit $(CPLDFIT_FLAGS) -p $(PART) $*.ngd
# %.jed: %.vm6
		# $(ISE_BIN)/hprep6 $(HPREP6_FLAGS) -i $*.vm6



    chain = getChain(assem)
    assert len(chain) == len(rn.routers)

    def impact_setup(f, ofn):
        print >>f, "setMode -bscan"
        print >>f, "setCable -port svf -file", ofn
        for i, rname in enumerate(chain):
            # Impact jtag indexes are 1-indexed:
            print >>f, "addDevice -position %d -file %s.jed" % (i+1, rname)
    def impact_prog(f, idx):
        assert 0 <= idx < len(chain)
        print >>f, "program -e -v -p %d" % (idx + 1)
    def impact_end(f):
        print >>f, "quit"

    with Rewriter(os.path.join(build_dir, "prog_all.batch")) as f:
        impact_setup(f, "prog_all.svf")
        for i in xrange(len(chain)):
            impact_prog(f, i)
        impact_end(f)

    print >>of, "%s/prog_all.svf: %s" % (build_dir, ' '.join(jeds))
    print >>of, "\tcd %s; $(ISE_BIN)/impact -batch prog_all.batch" % (build_dir,)
    print >>of, "prog_%s: %s/prog_all.svf" % (aname, build_dir)
    print >>of, "\tcd %s; python ~/Dropbox/ee/jtag/svf_reader/svf_reader.py prog_all.svf" % (build_dir,)

    print chain
    print rn.routers


