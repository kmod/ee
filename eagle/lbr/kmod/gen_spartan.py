
cur_x = 0
x_by_bank = {}
y_by_bank = {}

for l in open("tq144.txt"):
    l = l.split("#")[0].strip()
    if not l:
        continue
    tokens = l.split()
    assert len(tokens) == 4
    bank, name, number, bufio2 = tokens
    if bank not in x_by_bank:
        x_by_bank[bank] = cur_x
        cur_x += 25.4
        y_by_bank[bank] = 0

    x = x_by_bank[bank]
    y = y_by_bank[bank]
    y_by_bank[bank] += 2.54
    print """<pin name="%(num)s/%(name)s" x="%(x)s" y="%(y)s" length="middle"/>""" % dict(x=x, y=y, name=name, num=number)
