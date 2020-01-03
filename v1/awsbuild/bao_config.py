# vim:fileencoding=utf-8:noet

""" python class """

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
#* File           :    bao_config.py
#* Description    :    class to get the configuration settings
#* Author         :    Luc Suryo <luc@badassops.com>
#* Version        :    0.2
#* Date           :    Feb 21, 2019
#*
#* History    :
#*     Date:          Author:        Info:
#*    Jun 1, 2010     LIS            First Release
#*    Feb 21, 2019    LIS            refactored

from logging import critical
import sys
import yaml

class AwsConfig():
    """ Class to read the configurtation files and return their values as a dict.
        the file name are hardcoded
    """
    cfgs = {
        'aws_cfg' : 'aws.yaml',
        'dc_cfg'  : 'dc.yaml',
        'sec_cfg' : 'sec.yaml'
    }
    instance_cfg = 'ec2.yaml'

    def __init__(self, **kwargs):
        """ initial the object """
        self.settings = {}
        self.cfgdir = kwargs.get('cfgdir', {})
        self.cfgfile = kwargs.get('cfgfile', self.instance_cfg)
        self.cfgkey = kwargs.get('cfgkey', 'instance_cfg')
        if not self.cfgdir.endswith('/'):
            self.cfgdir = self.cfgdir + '/'
        if not self.cfgfile.startswith('/'):
            self.cfgfile = self.cfgdir + self.cfgfile
        for k in self.cfgs:
            cfg_file = self.cfgdir + self.cfgs[k]
            self.settings[k] = self._read_configs(cfg_file=cfg_file)
        self.settings[self.cfgkey] = self._read_configs(cfg_file=self.cfgfile)

    def get_settings(self):
        """ return the  configuration """
        return self.settings

    def show_settings(self):
        """ show the configuration """
        return self.settings

    @classmethod
    def _read_configs(cls, cfg_file):
        """ read a YAML file and return the content """
        try:
            cfg_file = open(cfg_file, 'r')
            with cfg_file as ymlfile:
                return yaml.load(ymlfile)
        except Exception as err:
            critical('Could not open the file or yaml format issue {}. Error: {}'.format(cfg_file, err))
            sys.exit(1)
