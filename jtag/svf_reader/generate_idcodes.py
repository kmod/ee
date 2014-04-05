import glob
import os

if __name__ == "__main__":
    bsd_files = []
    bsd_files += glob.glob("/opt/Xilinx/14.7/ISE_DS/ISE/xbr/data/xc2*.bsd")
    # bsd_files += glob.glob("/opt/Xilinx/14.7/ISE_DS/ISE/spartan6/data/xc6slx*.bsd")

    bsd_files.sort()

    for fn in bsd_files:
        bn = os.path.basename(fn)
        if bn.count('_') != 1:
            continue
        if "1532" in bn:
            continue

        with open(fn) as f:
            for l in f:
                if "IDCODE_REGISTER" in l:
                    # print l
                    sp = l.split('"')
                    assert len(sp) == 3, sp
                    bin = sp[1]

                    val = int(bin.replace('X', '0'), 2)
                    mask = int(bin.replace('0', '1').replace('X', '0'), 2)
                    print "(%r, 0x%x, 0x%x)," % (bn[:-4], val, mask)
                    # print "%s: %r," % (hex(val), bn[:-4])

                    break
