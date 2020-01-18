# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8:noet:tabstop=4:softtabstop=4:shiftwidth=8:expandtab

""" python3 method """

# Copyright (c)  2010 - 2020, © Badassops LLC / Luc Suryo
# All rights reserved.
# BSD 3-Clause License : http://www.freebsd.org/copyright/freebsd-license.html

import signal
import sys

def signal_handler(signum, frame):
    """ signal/interrupts handler
    """
    if signum is int(signal.SIGHUP):
        print('Received -HUP, app does not support reload. {}'.format(frame))
    elif signum is int(signal.SIGINT):
        print('Received ctrl-c, aborted on your request. {}'.format(frame))
    elif signum is int(signal.SIGTERM):
        print('Received -TERM, terminating. {}'.format(frame))
    else:
        print('Received unknwon interrupt : {}'.format(signum))
    sys.exit(128 + signum)

def install_int_handler():
    """ Install signal/interrupts handler, we capture only SIGHUP, SIGINT and TERM
    """
    signal.signal(signal.SIGHUP, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
