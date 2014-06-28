TYPE = "QFN"
PIN_COUNT = 48
PITCH = 0.4

# I've seen 1.6mm recommended; I think the more important parameter is how much is sticks out past the end
PAD_LENGTH = {"QFN":1.2, "QFP":1.6}[TYPE]

# From IPC-SM-782
# http://www.tortai-tech.com/upload/download/2011102023233369053.pdf
PITCH_TO_WIDTH = {
        0.8: 0.5,
        0.63: 0.4,
        0.5: 0.3,
        # 0.4: 0.25,
        0.4: 0.2, # IPC-SM-782 recommends 0.25, but that only leaves 6mil clearance, which might not be enough to put soldermask there
        0.3: 0.17
        }

# on both sides; IPC-SM-782 recommends 0.4
PAD_PAST_END = {"QFN":0.7, "QFP":0.5}[TYPE]

# just for drawing purposes:
LEAD_INNER_WIDTH = 5.2
LEAD_OUTER_WIDTH = 6.0
LEAD_WIDTH = 0.20

assert PIN_COUNT % 4 == 0

def sign(x):
    if x >= 0:
        return 1
    return -1

# Hopefully not an issue that we're using floats as dict keys:
pad_width = PITCH_TO_WIDTH[PITCH]

# distance from the inside of one pad to the inside on the other side
pad_outer_width = LEAD_OUTER_WIDTH + 2 * PAD_PAST_END
pad_inner_width = pad_outer_width - 2 * PAD_LENGTH

pad_line_offset = pad_inner_width / 2 + PAD_LENGTH / 2
lead_line_offset = (LEAD_INNER_WIDTH + LEAD_OUTER_WIDTH) / 4.0
lead_length = (LEAD_OUTER_WIDTH - LEAD_INNER_WIDTH) / 2

print """<description>%(PIN_COUNT)d-pin, %(PITCH)smm-pitch %(TYPE)s&lt;br/&gt;
Generated with gen_qfp.py with the following parameters:&lt;br/&gt;
&lt;pre&gt;PAD_LENGTH = %(PAD_LENGTH)s
PAD_PAST_END = %(PAD_PAST_END)s
LEAD_INNER_WIDTH = %(LEAD_INNER_WIDTH)s
LEAD_OUTER_WIDTH = %(LEAD_OUTER_WIDTH)s
LEAD_WIDTH = %(LEAD_WIDTH)s&lt;/pre&gt;</description>""" % globals()

for i in xrange(PIN_COUNT):
    pad_line_idx = i % (PIN_COUNT / 4)
    # pad_line_idx ranges from 0 to (pin_count/4 - 1)
    pad_line_idx -= 0.5 * (PIN_COUNT/4 - 1)
    line_pos = pad_line_idx * PITCH

    which_line = i / (PIN_COUNT / 4)
    if which_line == 0:
        x = -pad_line_offset
        y = -line_pos
        lx = -lead_line_offset
        ly = -line_pos
    elif which_line == 1:
        x = line_pos
        y = -pad_line_offset
        lx = line_pos
        ly = -lead_line_offset
    elif which_line == 2:
        x = pad_line_offset
        y = line_pos
        lx = lead_line_offset
        ly = line_pos
    elif which_line == 3:
        x = -line_pos
        y = pad_line_offset
        lx = -line_pos
        ly = lead_line_offset
    else:
        assert 0

    rot = 'rot="R90" ' if which_line % 2 == 1 else ''

    print """<smd name="%03d" x="%f" y="%f" dx="%f" dy="%f" layer="1" %s/>""" % (i+1, x, y, PAD_LENGTH, pad_width, rot)
    print """<rectangle x1="%f" y1="%f" x2="%f" y2="%f" layer="51" %s/>""" % (lx - lead_length / 2, ly - LEAD_WIDTH / 2, lx + lead_length / 2, ly + LEAD_WIDTH / 2, rot)
