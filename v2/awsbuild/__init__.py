# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8:noet:tabstop=4:softtabstop=4:shiftwidth=8:expandtab

""" initializer """

# Copyright (c)  2010 - 2020, © Badassops LLC / Luc Suryo
# All rights reserved.
# BSD 3-Clause License : http://www.freebsd.org/copyright/freebsd-license.html

import sys

__major__ = 3
__minor__ = 8

try:
    assert sys.version_info >= (__major__, __minor__)
except Exception:
    print('This script requires Python {}.{} or higher!'.format(__major__, __minor__))
    print('You are using Python {}.{}.'.format(sys.version_info.major, sys.version_info.minor))
    sys.exit(1)
