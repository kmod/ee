
cur_x = 0
x_by_bank = {}
y_by_bank = {}

for l in open("s3_256.txt"):
    l = l.split("#")[0].strip()
    if not l:
        continue
    tokens = l.split()
    assert len(tokens) == 5, tokens
    bank, name50, name100, ball, type = tokens
    if name50 == name100:
        name = name50
    else:
        # assert name50 == "N.C." or (name100.startswith("IO") and name50.startswith("IP")) or name100.startswith(name50), (name50, name100)
        name = "%s(50:%s)" % (name100, name50)

    if bank not in x_by_bank:
        x_by_bank[bank] = cur_x
        cur_x += 25.4
        y_by_bank[bank] = 0

    x = x_by_bank[bank]
    y = y_by_bank[bank]
    y_by_bank[bank] += 2.54
    print """<pin name="%(ball)s/%(name)s" x="%(x)s" y="%(y)s" length="middle"/>""" % dict(x=x, y=y, name=name, ball=ball)
