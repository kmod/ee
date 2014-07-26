import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import Queue
import time

from debugger.controller import Controller

q = Queue.Queue()
def on_read(c):
    # sys.stdout.write("\033[34m%02x\033[0m " % ord(c))
    # sys.stdout.flush()
    q.put(c)

def main():
    ctlr = Controller()
    ctlr.on_read.append(on_read)

    TDO = 5
    TCK = 4
    TMS = 3
    TDI = 2
    DBG1 = 6
    DBG2 = 7

    ctlr.pinMode(TDO, "input")
    ctlr.pinMode(TCK, "output")
    ctlr.pinMode(TMS, "output")
    ctlr.pinMode(TDI, "output")
    ctlr.pinMode(DBG1, "output")
    ctlr.pinMode(DBG2, "output")

    def pulse(tms, tdi):
        DELAY = 0.0
        ctlr.digitalWrite(TMS, tms)
        ctlr.digitalWrite(TDI, tdi)
        time.sleep(DELAY)

        ctlr.digitalWrite(TCK, 1)
        time.sleep(DELAY)
        ctlr.digitalWrite(TCK, 0)
        time.sleep(DELAY)

        ctlr.digitalRead(TDO)
        b = ord(q.get())
        print "pulse", tms, tdi, b
        return b

    def idcode1():
        # Move to Test-Logic Reset
        print "Resetting"
        for i in xrange(5):
            pulse(1, 0)

        # Move to shift-IR:
        print "moving to shift-IR"
        pulse(0, 0)
        pulse(1, 0)
        pulse(1, 0)
        pulse(0, 0)
        pulse(0, 0)

        # shift in 0x0001:
        print "shifting in IDCODE"
        pulse(0, 1)
        pulse(0, 0)
        pulse(0, 0)
        pulse(0, 0)
        pulse(0, 0)
        pulse(0, 0)
        pulse(0, 0)
        pulse(1, 0) # move to exit-IR

        # Move to shift-DR:
        print "moving to shift-DR"
        pulse(1, 0)
        pulse(1, 0)
        pulse(0, 0)
        pulse(0, 0)

        print "shifting out DR"
        ctlr.digitalWrite(DBG1, 1)
        for i in xrange(31):
            pulse(0, i&1)
        pulse(0, 0)
        ctlr.digitalWrite(DBG1, 0)

    def idcode2():
        # Move to Test-Logic Reset
        print "Resetting"
        for i in xrange(5):
            pulse(1, 0)

        print "moving to shift-DR"
        pulse(0, 0)
        pulse(1, 0)
        pulse(0, 0)
        pulse(0, 0)

        print "shifting out DR"
        ctlr.digitalWrite(DBG1, 1)
        for i in xrange(31):
            pulse(0, i&1)
        pulse(0, 0)
        ctlr.digitalWrite(DBG1, 0)

    def reset():
        # Move to Test-Logic Reset
        print "Resetting"
        for i in xrange(5):
            pulse(1, 0)
        # Move to run-test/idle
        pulse(0, 0)

    def extest(val):
        # Move to shift-IR:
        print "moving to shift-IR"
        pulse(0, 0)
        pulse(1, 0)
        pulse(1, 0)
        pulse(0, 0)
        pulse(0, 0)

        # shift in 0x0001:
        print "shifting in EXTEST"
        pulse(0, 0)
        pulse(0, 0)
        pulse(0, 0)
        pulse(0, 0)
        pulse(0, 0)
        pulse(0, 0)
        pulse(0, 0)
        pulse(1, 0) # move to exit-IR

        # Move to shift-DR:
        print "moving to shift-DR"
        pulse(1, 0)
        pulse(1, 0)
        pulse(0, 0)
        b = pulse(0, 0)

        print "shifting out DR"
        ctlr.digitalWrite(DBG1, 1)

        data = [0] * 97
        data[25] = 1 # enable pin 2 output
        data[26] = val # drive pin 2 high

        for i in xrange(97):
            print i, "%02x" % b
            b = pulse(1 if i == 96 else 0, data[i])
        ctlr.digitalWrite(DBG1, 0)

        pulse(1, 0) # move to Update-DR
        # pulse(1, 0) # move to Run-Test/Idle


    idcode1()
    # reset()
    # extest(0)
    # extest(1)


if __name__ == "__main__":
    main()

