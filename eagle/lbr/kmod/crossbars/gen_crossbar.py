ROWS = 24
COLS = 18

# All dimensions in mils
DRILL_DIAM = 13
PAD_DIAM = 35
ROW_TRACE_WIDTH = 6
COL_TRACE_WIDTH = 10
ROW_SPACING = 10
COL_SPACING = 10

col_width = PAD_DIAM + COL_SPACING
row_height = 2 * ROW_TRACE_WIDTH + 3 * ROW_SPACING + PAD_DIAM

MMS_PER_MIL = .0254

print """
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE eagle SYSTEM "eagle.dtd">
<eagle version="6.4">
<drawing>
<settings>
<setting alwaysvectorfont="no"/>
<setting verticaltext="up"/>
</settings>
<grid distance="0.05" unitdist="inch" unit="inch" style="lines" multiple="1" display="yes" altdistance="0.025" altunitdist="inch" altunit="inch"/>
<layers>
<layer number="1" name="Top" color="4" fill="1" visible="yes" active="yes"/>
<layer number="16" name="Bottom" color="1" fill="1" visible="yes" active="yes"/>
<layer number="17" name="Pads" color="2" fill="1" visible="yes" active="yes"/>
<layer number="18" name="Vias" color="2" fill="1" visible="yes" active="yes"/>
<layer number="19" name="Unrouted" color="6" fill="1" visible="yes" active="yes"/>
<layer number="20" name="Dimension" color="15" fill="1" visible="yes" active="yes"/>
<layer number="21" name="tPlace" color="7" fill="1" visible="yes" active="yes"/>
<layer number="22" name="bPlace" color="7" fill="1" visible="yes" active="yes"/>
<layer number="23" name="tOrigins" color="15" fill="1" visible="yes" active="yes"/>
<layer number="24" name="bOrigins" color="15" fill="1" visible="yes" active="yes"/>
<layer number="25" name="tNames" color="7" fill="1" visible="yes" active="yes"/>
<layer number="26" name="bNames" color="7" fill="1" visible="yes" active="yes"/>
<layer number="27" name="tValues" color="7" fill="1" visible="yes" active="yes"/>
<layer number="28" name="bValues" color="7" fill="1" visible="yes" active="yes"/>
<layer number="29" name="tStop" color="7" fill="3" visible="no" active="yes"/>
<layer number="30" name="bStop" color="7" fill="6" visible="no" active="yes"/>
<layer number="31" name="tCream" color="7" fill="4" visible="no" active="yes"/>
<layer number="32" name="bCream" color="7" fill="5" visible="no" active="yes"/>
<layer number="33" name="tFinish" color="6" fill="3" visible="no" active="yes"/>
<layer number="34" name="bFinish" color="6" fill="6" visible="no" active="yes"/>
<layer number="35" name="tGlue" color="7" fill="4" visible="no" active="yes"/>
<layer number="36" name="bGlue" color="7" fill="5" visible="no" active="yes"/>
<layer number="37" name="tTest" color="7" fill="1" visible="no" active="yes"/>
<layer number="38" name="bTest" color="7" fill="1" visible="no" active="yes"/>
<layer number="39" name="tKeepout" color="4" fill="11" visible="yes" active="yes"/>
<layer number="40" name="bKeepout" color="1" fill="11" visible="yes" active="yes"/>
<layer number="41" name="tRestrict" color="4" fill="10" visible="yes" active="yes"/>
<layer number="42" name="bRestrict" color="1" fill="10" visible="yes" active="yes"/>
<layer number="43" name="vRestrict" color="2" fill="10" visible="yes" active="yes"/>
<layer number="44" name="Drills" color="7" fill="1" visible="no" active="yes"/>
<layer number="45" name="Holes" color="7" fill="1" visible="no" active="yes"/>
<layer number="46" name="Milling" color="3" fill="1" visible="no" active="yes"/>
<layer number="47" name="Measures" color="7" fill="1" visible="no" active="yes"/>
<layer number="48" name="Document" color="7" fill="1" visible="yes" active="yes"/>
<layer number="49" name="Reference" color="7" fill="1" visible="yes" active="yes"/>
<layer number="50" name="dxf" color="7" fill="1" visible="no" active="no"/>
<layer number="51" name="tDocu" color="7" fill="1" visible="yes" active="yes"/>
<layer number="52" name="bDocu" color="7" fill="1" visible="yes" active="yes"/>
<layer number="53" name="tGND_GNDA" color="7" fill="9" visible="no" active="no"/>
<layer number="54" name="bGND_GNDA" color="1" fill="9" visible="no" active="no"/>
<layer number="56" name="wert" color="7" fill="1" visible="no" active="no"/>
<layer number="91" name="Nets" color="2" fill="1" visible="yes" active="yes"/>
<layer number="92" name="Busses" color="1" fill="1" visible="yes" active="yes"/>
<layer number="93" name="Pins" color="2" fill="1" visible="yes" active="yes"/>
<layer number="94" name="Symbols" color="4" fill="1" visible="yes" active="yes"/>
<layer number="95" name="Names" color="7" fill="1" visible="yes" active="yes"/>
<layer number="96" name="Values" color="7" fill="1" visible="yes" active="yes"/>
<layer number="97" name="Info" color="7" fill="1" visible="yes" active="yes"/>
<layer number="98" name="Guide" color="6" fill="1" visible="yes" active="yes"/>
<layer number="100" name="Muster" color="7" fill="1" visible="no" active="no"/>
<layer number="101" name="Patch_Top" color="12" fill="4" visible="yes" active="yes"/>
<layer number="102" name="Vscore" color="7" fill="1" visible="yes" active="yes"/>
<layer number="103" name="tMap" color="7" fill="1" visible="yes" active="yes"/>
<layer number="104" name="Name" color="16" fill="1" visible="yes" active="yes"/>
<layer number="105" name="tPlate" color="7" fill="1" visible="yes" active="yes"/>
<layer number="106" name="bPlate" color="7" fill="1" visible="yes" active="yes"/>
<layer number="107" name="Crop" color="7" fill="1" visible="yes" active="yes"/>
<layer number="108" name="tplace-old" color="10" fill="1" visible="yes" active="yes"/>
<layer number="109" name="ref-old" color="11" fill="1" visible="yes" active="yes"/>
<layer number="116" name="Patch_BOT" color="9" fill="4" visible="yes" active="yes"/>
<layer number="121" name="_tsilk" color="7" fill="1" visible="yes" active="yes"/>
<layer number="122" name="_bsilk" color="7" fill="1" visible="yes" active="yes"/>
<layer number="125" name="_tNames" color="7" fill="1" visible="yes" active="yes"/>
<layer number="144" name="Drill_legend" color="7" fill="1" visible="yes" active="yes"/>
<layer number="151" name="HeatSink" color="7" fill="1" visible="yes" active="yes"/>
<layer number="199" name="Contour" color="7" fill="1" visible="yes" active="yes"/>
<layer number="200" name="200bmp" color="1" fill="10" visible="yes" active="yes"/>
<layer number="201" name="201bmp" color="2" fill="10" visible="yes" active="yes"/>
<layer number="202" name="202bmp" color="3" fill="10" visible="yes" active="yes"/>
<layer number="203" name="203bmp" color="4" fill="10" visible="yes" active="yes"/>
<layer number="204" name="204bmp" color="5" fill="10" visible="yes" active="yes"/>
<layer number="205" name="205bmp" color="6" fill="10" visible="yes" active="yes"/>
<layer number="206" name="206bmp" color="7" fill="10" visible="yes" active="yes"/>
<layer number="207" name="207bmp" color="8" fill="10" visible="yes" active="yes"/>
<layer number="208" name="208bmp" color="9" fill="10" visible="yes" active="yes"/>
<layer number="209" name="209bmp" color="7" fill="1" visible="yes" active="yes"/>
<layer number="210" name="210bmp" color="7" fill="1" visible="yes" active="yes"/>
<layer number="211" name="211bmp" color="7" fill="1" visible="yes" active="yes"/>
<layer number="212" name="212bmp" color="7" fill="1" visible="yes" active="yes"/>
<layer number="213" name="213bmp" color="7" fill="1" visible="yes" active="yes"/>
<layer number="214" name="214bmp" color="7" fill="1" visible="yes" active="yes"/>
<layer number="215" name="215bmp" color="7" fill="1" visible="yes" active="yes"/>
<layer number="216" name="216bmp" color="7" fill="1" visible="yes" active="yes"/>
<layer number="217" name="217bmp" color="18" fill="1" visible="no" active="no"/>
<layer number="218" name="218bmp" color="19" fill="1" visible="no" active="no"/>
<layer number="219" name="219bmp" color="20" fill="1" visible="no" active="no"/>
<layer number="220" name="220bmp" color="21" fill="1" visible="no" active="no"/>
<layer number="221" name="221bmp" color="22" fill="1" visible="no" active="no"/>
<layer number="222" name="222bmp" color="23" fill="1" visible="no" active="no"/>
<layer number="223" name="223bmp" color="24" fill="1" visible="no" active="no"/>
<layer number="224" name="224bmp" color="25" fill="1" visible="no" active="no"/>
<layer number="250" name="Descript" color="3" fill="1" visible="no" active="no"/>
<layer number="251" name="SMDround" color="12" fill="11" visible="no" active="no"/>
<layer number="254" name="cooling" color="7" fill="1" visible="yes" active="yes"/>
</layers>
<library>
<packages>
""".strip()

print """<package name="CROSSBAR_24X18">"""

assert ROWS % 2 == 0

for j in xrange(COLS):
    y1 = (-ROW_SPACING/2) * MMS_PER_MIL
    y2 = row_height * (ROWS/2) * MMS_PER_MIL + y1
    x = col_width * j * MMS_PER_MIL
    print """<wire x1="%.3f" y1="%.3f" x2="%.3f" y2="%.3f" width="%.3f" layer="16"/>""" % (x, y1, x, y2, COL_TRACE_WIDTH * MMS_PER_MIL)

for i in xrange(ROWS/2):
    x1 = (-PAD_DIAM/2 - COL_SPACING/2) * MMS_PER_MIL
    x2 = col_width * COLS * MMS_PER_MIL + x1

    y = row_height * i * MMS_PER_MIL
    print """<wire x1="%.3f" y1="%.3f" x2="%.3f" y2="%.3f" width="%.3f" layer="1"/>""" % (x1, y, x2, y, ROW_TRACE_WIDTH * MMS_PER_MIL)
    y = (row_height * i + (ROW_TRACE_WIDTH + ROW_SPACING + PAD_DIAM + ROW_SPACING)) * MMS_PER_MIL
    print """<wire x1="%.3f" y1="%.3f" x2="%.3f" y2="%.3f" width="%.3f" layer="1"/>""" % (x1, y, x2, y, ROW_TRACE_WIDTH * MMS_PER_MIL)

for j in xrange(COLS):
    for i in xrange(ROWS/2):
        x = j * col_width
        y = i * row_height + ROW_TRACE_WIDTH / 2 + ROW_SPACING + PAD_DIAM / 2
        x *= MMS_PER_MIL
        y *= MMS_PER_MIL
        print """<pad name="C%02d_%02d" x="%.3f" y="%.3f" drill="%.4f" diameter="%.3f" shape="octagon"/>""" % (
                j, i, x, y, DRILL_DIAM * MMS_PER_MIL, PAD_DIAM * MMS_PER_MIL)

print """</package>"""
print """</packages>"""

print """<symbols>"""

print """<symbol name="CROSSBAR_24X18">"""

PIN_SPACING = 100

def roundup(x, k):
    y = (x / k + 0.99999)
    z = y - (y % 1)
    return z * k
h = max(ROWS + 2, COLS + 2) * PIN_SPACING * MMS_PER_MIL
w = max(20, 0.5 * h)
h = roundup(h, 200 * MMS_PER_MIL)
w = roundup(w, 200 * MMS_PER_MIL)

print """
<wire x1="-%(x).2f" y1="%(y).2f" x2="-%(x).2f" y2="-%(y).2f" width="0.254" layer="94"/>
<wire x1="-%(x).2f" y1="-%(y).2f" x2="%(x).2f" y2="-%(y).2f" width="0.254" layer="94"/>
<wire x1="%(x).2f" y1="-%(y).2f" x2="%(x).2f" y2="%(y).2f" width="0.254" layer="94"/>
<wire x1="%(x).2f" y1="%(y).2f" x2="-%(x).2f" y2="%(y).2f" width="0.254" layer="94"/>
""".strip() % dict(x=w/2, y=h/2)

for i in xrange(ROWS):
    x = -w/2 - 200 * MMS_PER_MIL
    y = (ROWS//2 - i) * PIN_SPACING * MMS_PER_MIL
    print """<pin name="H%d" x="%.1f" y="%.2f" length="middle"/>""" % (i, x, y)

for i in xrange(COLS):
    x = w/2 + 200 * MMS_PER_MIL
    y = (COLS//2 - i) * PIN_SPACING * MMS_PER_MIL
    print """<pin name="V%d" x="%.1f" y="%.2f" length="middle" rot="R180"/>""" % (i, x, y)


print """</symbol>"""
print """</symbols>"""

print """
<devicesets>
<deviceset name="CROSSBAR_24X18">
<gates>
<gate name="G$1" symbol="CROSSBAR_24X18" x="0" y="0"/>
</gates>
<devices>
<device name="" package="CROSSBAR_24X18">
<connects>
""".strip()

for j in xrange(COLS):
    pads = ' '.join(["C%02d_%02d" % (j, i) for i in xrange(ROWS/2)])
    print """<connect gate="G$1" pin="V%d" pad="%s"/>""" % (j, pads)

print """
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
</devicesets>
""".strip()

print """
</library>
</drawing>
</eagle>
""".strip()
