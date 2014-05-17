
cur_x = 0
x_by_bank = {}
y_by_bank = {}

seen = set()
pins = {}

for l in open("s6_ft256.txt"):
    l = l.split("#")[0].strip()
    if not l:
        continue
    tokens = l.split(' ', 3)
    assert len(tokens) == 4, tokens
    bank, name, ball, iobuf = tokens

    pins.setdefault(name, []).append(ball)
    if bank != "NA" and "VCC" not in name:
        name = "%s/%s" % (ball, name)
    elif name in seen:
        continue
    seen.add(name)

    if bank not in x_by_bank:
        x_by_bank[bank] = cur_x
        cur_x += 25.4
        y_by_bank[bank] = 0

    x = x_by_bank[bank]
    y = y_by_bank[bank]
    y_by_bank[bank] += 2.54

    print """<pin name="%(name)s" x="%(x)s" y="%(y)s" length="middle"/>""" % dict(x=x, y=y, name=name, ball=ball)

print
print

for name, balls in pins.iteritems():
    print """<connect gate="G$1" pin="%s" pad="%s"/>""" % (name, ' '.join(balls))
