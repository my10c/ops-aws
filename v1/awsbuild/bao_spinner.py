# vim:fileencoding=utf-8:noet

""" python method """

# Copyright (c)  2010 - 2019, © Badassops LLC / Luc Suryo
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#*
#* File           :    bao_spinner.py
#* Description    :    class and function so display a wait spinner (dots or wheel)
#* Author         :    Luc Suryo <luc@badassops.com>
#* Version        :    0.2
#* Date           :    Feb 21, 2019
#*
#* History    :
#*     Date:          Author:        Info:
#*    Jun 1, 2010     LIS            First Release
#*    Feb 21, 2019    LIS            refactored


import os
import sys
import threading
import unicodedata
from time import sleep

class SpinCursor(threading.Thread):
    """ Class and function so display a wait spinner (dots or wheel)
    """

    def __init__(self, msg=None, maxspin=0, minspin=10, speed=5, dots=False):
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
        self.waittime = 1.0/float(speed*4)
        if os.name == 'posix':
            if dots is True:
                self.spinchars = (unicodedata.lookup('FIGURE DASH'), u'. ', u'• ', u'. ', u'• ')
            else:
                self.spinchars = (unicodedata.lookup('FIGURE DASH'), u'\\ ', u'| ', u'/ ')
        else:
            # The unicode dash character does not show
            # up properly in Windows console.
            if dots is True:
                self.spinchars = (u'. ', u'• ', u'. ', u'• ')
            else:
                self.spinchars = (u'-', u'\\ ', u'| ', u'/ ')
        threading.Thread.__init__(self, None, None, "Spin Thread")

    def spin(self):
        """ Perform a single spin """
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
    spin = SpinCursor(msg=message, minspin=seconds, speed=1)
    spin.start()
    sleep(seconds)
    spin.stop()

def dot_message(message=None, seconds=None):
    """ fucntion to print dot while sleeping for the given seconds. """
    spin = SpinCursor(msg=message, minspin=seconds, speed=1, dots=True)
    spin.start()
    sleep(seconds)
    spin.stop()
