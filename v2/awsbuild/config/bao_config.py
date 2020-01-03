# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8:noet:tabstop=4:softtabstop=4:shiftwidth=8:expandtab

""" python3 class """

# Copyright (c)  2010 - 2020, © Badassops LLC / Luc Suryo
# All rights reserved.
# BSD 3-Clause License : http://www.freebsd.org/copyright/freebsd-license.html

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
