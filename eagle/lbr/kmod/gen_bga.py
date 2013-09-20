# Basic info:
GRID_SIZE = 16
BALL_PITCH = 1.0

# from http://www.xilinx.com/support/documentation/user_guides/ug112.pdf#page=88
SOLDER_LAND = 0.40 
MASK_OPENING = 0.50

ROWNAMES = "ABCDEFGHJKLMNPRT"

for c in xrange(0, GRID_SIZE):
    for r in xrange(0, GRID_SIZE):
        x = -((GRID_SIZE - 1) * 0.5 - c) * BALL_PITCH
        y = ((GRID_SIZE - 1) * 0.5 - r) * BALL_PITCH
        name = "%s%d" % (ROWNAMES[r], c + 1)
        print ("""
<smd name="%(n)s" x="%(x)f" y="%(y)f" dx="%(s)f" dy="%(s)f" layer="1" roundness="100" stop="no"/>
<circle x="%(x)f" y="%(y)f" radius="%(r)f" width="%(w)f" layer="29"/>
        """ % dict(n=name, x=x, y=y, s=SOLDER_LAND, r=MASK_OPENING/4, w=MASK_OPENING/2)).strip()
