PIN_COUNT = 66
PITCH = 0.65
PAD_CENTER_WIDTH = 11.7 # distance from the center of one pad to the center of one on the opposite side

def sign(x):
    if x >= 0:
        return 1
    return -1

for i in xrange(PIN_COUNT):
    y = PAD_CENTER_WIDTH/2
    if i < PIN_COUNT/2:
        y = -y

    x = (i+1 - (PIN_COUNT/2 + 1) * 0.5) * PITCH
    if i >= PIN_COUNT/2:
        x = -(x - PITCH * PIN_COUNT * 0.5)

    print """<smd name="%d" x="%f" y="%f" dx="0.4" dy="1.3" layer="1" />""" % (i+1, x, y)
    print """<rectangle x1="%f" y1="%f" x2="%f" y2="%f" layer="51"/>""" % (x - 0.16, y - sign(y) * 0.77, x + 0.16, y + sign(y) *0.1)
