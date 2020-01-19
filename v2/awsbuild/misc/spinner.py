# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8:noet:tabstop=4:softtabstop=4:shiftwidth=8:expandtab

""" python3 method """

# Copyright (c)  2010 - 2020, © Badassops LLC / Luc Suryo
# All rights reserved.
# BSD 3-Clause License : http://www.freebsd.org/copyright/freebsd-license.html

import sys
import threading
from time import sleep

class SpinCursor(threading.Thread):
    """ class and function so display a wait spinner (dots or wheel)
    """

    def __init__(self, msg=None, maxspin=0, minspin=10, speed=5, mode=None):
        # Count of a spin
        self.count = 0
        self.out = sys.stdout
        self.flag = False
        self.max = maxspin
        self.min = minspin
        # Any message to print first ?
        self.msg = msg
        # Complete printed string
        self.string = None
        # Speed is given as number of spins a second
        # Use it to calculate spin wait time
        self.waittime = 1.0/float(speed*10)
        if mode == 'dots':
            self.spinchars = (u'◦ ', u'○ ', u'◎ ', u'◉ ')
        if mode == 'count-down':
            self.spinchars = (u'9 ', u'8 ', u'7 ', u'6 ', u'5 ', u'4 ', u'3 ', u'2 ', u'1 ', u'0 ')
        if mode == 'wheel':
            self.spinchars = (u'-', u'\\ ', u'| ', u'/ ')
        threading.Thread.__init__(self, None, None, "Spin Thread")

    def spin(self):
        """ perform a single spin """
        for spinchar in self.spinchars:
            if self.msg:
                self.string = self.msg + '...\t' + spinchar + '\r'
            else:
                self.string = '...\t' + spinchar + '\r'
            #self.string = self.msg + '...\t' + spinchar + '\r'
            self.out.write(self.string)
            self.out.flush()
            sleep(self.waittime)

    def run(self):
        """ run spinning """
        while (not self.flag) and ((self.count < self.min) or (self.count < self.max)):
            self.spin()
            self.count += 1
        # Clean up display...
        #self.out.write(' '*(len(self.string) + len('...\t')))
        self.out.write('\033[2K')

    def stop(self):
        """ stop spinning """
        self.flag = True

def spin_message(message=None, seconds=None):
    """ print the given message and wait for the given seconds """
    spin = SpinCursor(msg=message, minspin=seconds, speed=1, mode='wheel')
    spin.start()
    sleep(seconds)
    spin.stop()

def dot_message(message=None, seconds=None):
    """ print dots while and wait for the given seconds """
    spin = SpinCursor(msg=message, minspin=seconds, speed=1, mode='dots')
    spin.start()
    sleep(seconds)
    spin.stop()

def count_down_message(message=None, seconds=None):
    """ print the given message and wait for the given seconds """
    spin = SpinCursor(msg=message, minspin=seconds, speed=1, mode='count-down')
    spin.start()
    sleep(seconds)
    spin.stop()
