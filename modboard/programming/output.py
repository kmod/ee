import cStringIO
import os

from model import RouterDef, SocketDef, JtagEntry, JtagDevice

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
                chain.append((cur_board, jobj))
                cur_board, cur_idx = cur_board, new_idx
            elif isinstance(jobj, JtagDevice):
                chain.append((cur_board, jobj))
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

def _makeXst(router_name):
    return ("""
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
""" % dict(rname=router_name)).strip()

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
    reset_jeds = []

    for rname, router in rn.routers.items():
        base_fn = os.path.join(build_dir, rname)
        routerdef = getRouterDef(rname)

        tmpdir = os.path.join(build_dir, "xst_%s/projnav.tmp" % rname)
        if not os.path.isdir(tmpdir):
            os.makedirs(tmpdir)
        reset_tmpdir = os.path.join(build_dir, "xst_reset_%s/projnav.tmp" % rname)
        if not os.path.isdir(reset_tmpdir):
            os.makedirs(reset_tmpdir)

        # I hate this file/function a lot;
        # TODO reduce the duplication and overall hackery
        print rname, router
        with Rewriter("%s/%s.v" % (build_dir, rname)) as f:
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

        with Rewriter("%s/reset_%s.v" % (build_dir, rname)) as f:
            print >>f, "`timescale 1ns / 1ps"
            print >>f
            print >>f, "module main("

            first = 1
            for target, (source_type, source) in router.iteritems():
                if not first:
                    print >>f, ','
                first = 0
                if source_type == 'p':
                    print >>f, "  output p%s," % source
                print >>f, "  output p%s" % target,
            print >>f, ");"

            print >>f

            for target, (source_type, source) in router.iteritems():
                print >>f, "  assign p%s = 1'bz;" % target
                if source_type == 'p':
                    print >>f, "  assign p%s = 1'bz;" % source

            print >>f, "endmodule"

        with Rewriter("%s/%s.xst" % (build_dir, rname)) as f:
            print >>f, _makeXst(rname)

        with Rewriter("%s/reset_%s.xst" % (build_dir, rname)) as f:
            print >>f, _makeXst("reset_" + rname)

        with Rewriter("%s/%s.prj" % (build_dir, rname)) as f:
            print >>f, 'verilog work "%s.v"' % rname

        with Rewriter("%s/reset_%s.prj" % (build_dir, rname)) as f:
            print >>f, 'verilog work "reset_%s.v"' % rname

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

        template_opts = dict(bd=build_dir, rname=rname, part=routerdef.part)
        template_opts['fit_opts'] = ' '.join(["%s %s" % i for i in fit_opts.items()])

        print >>of
        print >>of, "%(bd)s/%(rname)s.ngc: %(bd)s/%(rname)s.v" % template_opts
        print >>of, "\tcd %(bd)s; $(ISE_BIN)/xst -intstyle ise -ifn %(rname)s.xst" % template_opts
        print >>of, "%(bd)s/reset_%(rname)s.ngc: %(bd)s/reset_%(rname)s.v" % template_opts
        print >>of, "\tcd %(bd)s; $(ISE_BIN)/xst -intstyle ise -ifn reset_%(rname)s.xst" % template_opts
        print >>of, "%(bd)s/%(rname)s.ngd: %(bd)s/%(rname)s.ngc" % template_opts
        print >>of, "\tcd %(bd)s; $(ISE_BIN)/ngdbuild -uc %(rname)s.ucf -p %(part)s %(rname)s.ngc %(rname)s.ngd" % template_opts
        print >>of, "%(bd)s/reset_%(rname)s.ngd: %(bd)s/reset_%(rname)s.ngc" % template_opts
        print >>of, "\tcd %(bd)s; $(ISE_BIN)/ngdbuild -uc %(rname)s.ucf -p %(part)s reset_%(rname)s.ngc reset_%(rname)s.ngd" % template_opts
        print >>of, "%(bd)s/%(rname)s.vm6: %(bd)s/%(rname)s.ngd" % template_opts
        print >>of, "\tcd %(bd)s; $(ISE_BIN)/cpldfit %(fit_opts)s -p %(part)s %(rname)s.ngd" % template_opts
        print >>of, "%(bd)s/reset_%(rname)s.vm6: %(bd)s/reset_%(rname)s.ngd" % template_opts
        print >>of, "\tcd %(bd)s; $(ISE_BIN)/cpldfit %(fit_opts)s -p %(part)s reset_%(rname)s.ngd" % template_opts
        print >>of, "%(bd)s/%(rname)s.jed: %(bd)s/%(rname)s.vm6" % template_opts
        print >>of, "\tcd %(bd)s; $(ISE_BIN)/hprep6 -i %(rname)s.vm6" % template_opts
        print >>of, "%(bd)s/reset_%(rname)s.jed: %(bd)s/reset_%(rname)s.vm6" % template_opts
        print >>of, "\tcd %(bd)s; $(ISE_BIN)/hprep6 -i reset_%(rname)s.vm6" % template_opts
        jeds.append("%(bd)s/%(rname)s.jed" % template_opts)
        reset_jeds.append("%(bd)s/reset_%(rname)s.jed" % template_opts)

# %.vm6: %.ngd
		# $(ISE_BIN)/cpldfit $(CPLDFIT_FLAGS) -p $(PART) $*.ngd
# %.jed: %.vm6
		# $(ISE_BIN)/hprep6 $(HPREP6_FLAGS) -i $*.vm6

    print >>of, "%s_jeds:" % aname, " ".join(jeds), " ".join(reset_jeds)
    print >>of, "jeds::", " ".join(jeds), " ".join(reset_jeds)


    chain = getChain(assem)

    def bitstreamFor(boardname, jobj):
        assert isinstance(jobj, JtagDevice)
        return assem.boards[boardname].opts["%s.bitstream" % (jobj.name,)]

    def impact_setup(f, ofn, prefix, jdevice_idx):
        print >>f, "setMode -bscan"
        print >>f, "setCable -port svf -file", ofn
        for i, (boardname, jobj) in enumerate(chain):
            # Impact jtag indexes are 1-indexed

            if isinstance(jobj, RouterDef):
                if jdevice_idx is None:
                    print >>f, "addDevice -position %d -file %s%s.jed" % (i+1, prefix, "%s.%s" % (boardname, jobj.name))
                else:
                    part = jobj.part
                    if '-' in part:
                        part = part.split('-')[0]
                    print >>f, "addDevice -position %d -part %s" % (i+1, part)
            elif isinstance(jobj, JtagDevice):
                if jdevice_idx == i:
                    print >>f, "addDevice -position %d -file %s" % (i+1, bitstreamFor(boardname, jobj))
                else:
                    print >>f, "addDevice -position %d -part %s" % (i+1, jobj.part)
            else:
                raise Exception(jobj)
    def impact_prog(f, idx, verify=True):
        assert 0 <= idx < len(chain)
        args = ["program", "-e", "-p", str(idx+1)]
        if verify:
            args.append("-v")
        print >>f, ' '.join(args)
    def impact_end(f):
        print >>f, "quit"

    with Rewriter(os.path.join(build_dir, "prog_all.batch")) as f:
        impact_setup(f, "prog_all.svf", "", None)
        for i, (boardname, jobj) in enumerate(chain):
            if isinstance(jobj, RouterDef):
                impact_prog(f, i)
        impact_end(f)
    print >>of, "%s/prog_all.svf: %s/prog_all.batch %s" % (build_dir, build_dir, ' '.join(jeds))
    print >>of, "\tcd %s; $(ISE_BIN)/impact -batch prog_all.batch || (rm -f prog_all.svf; false)" % (build_dir,)
    print >>of, "prog_%s: %s/prog_all.svf" % (aname, build_dir)
    print >>of, "\tcd %s; python ~/Dropbox/ee/jtag/svf_reader2/svf_reader2.py prog_all.svf" % (build_dir,)

    with Rewriter(os.path.join(build_dir, "prog_reset_all.batch")) as f:
        impact_setup(f, "prog_reset_all.svf", "reset_", None)
        for i in xrange(len(chain)):
            if isinstance(chain[i], RouterDef):
                impact_prog(f, i)
        impact_end(f)
    print >>of, "%s/prog_reset_all.svf: %s/prog_reset_all.batch %s" % (build_dir, build_dir, ' '.join(reset_jeds))
    print >>of, "\tcd %s; $(ISE_BIN)/impact -batch prog_reset_all.batch || (rm -f prog_reset_all.svf; false)" % (build_dir,)
    print >>of, "prog_reset_%s: %s/prog_reset_all.svf" % (aname, build_dir)
    print >>of, "\tcd %s; python ~/Dropbox/ee/jtag/svf_reader2/svf_reader2.py prog_reset_all.svf" % (build_dir,)

    for i, (boardname, jobj) in enumerate(chain):
        if isinstance(jobj, JtagDevice):
            def prog(verify):
                bn = "prog_%s.%s" % (boardname, jobj.name)
                if not verify:
                    bn += "_noverify"
                with Rewriter(os.path.join(build_dir, "%s.batch" % bn)) as f:
                    impact_setup(f, "%s.svf" % bn, None, i)
                    impact_prog(f, i, verify=verify)
                    impact_end(f)

                print >>of, "%s/%s.svf: %s/%s.batch %s" % (build_dir, bn, build_dir, bn, os.path.normpath(os.path.join(build_dir, bitstreamFor(boardname, jobj))))
                print >>of, "\tcd %s; $(ISE_BIN)/impact -batch %s.batch || (rm -f %s.svf; false)" % (build_dir, bn, bn)
                print >>of, "prog_%s_%s.%s%s: %s/%s.svf" % (aname, boardname, jobj.name, "_noverify" if not verify else "", build_dir, bn)
                print >>of, "\tcd %s; python ~/Dropbox/ee/jtag/svf_reader2/svf_reader2.py %s.svf" % (build_dir, bn)
            prog(False)
            prog(True)

    print chain
    print rn.routers


