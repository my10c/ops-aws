# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8:noet:tabstop=4:softtabstop=4:shiftwidth=8:expandtab

""" python3 class """

# Copyright (c)  2010 - 2020, © Badassops LLC / Luc Suryo
# All rights reserved.
# BSD 3-Clause License : http://www.freebsd.org/copyright/freebsd-license.html

#from pprint import PrettyPrinter
#from logging import critical, warning


class ELBV2():
    """ Class for the AWS ELBv2
    """

    def __init__(self, **kwargs):
        """ initial the object """
        self.cmd_cfg = kwargs.get('cmd_cfg', {})
        self.session = kwargs.get('session', {})
        self.tag = self.cmd_cfg['tag']

        # DANGER WILL ROBINSON : we using wildcard as filter!
        self.tag_filter = '*' + str(self.tag) + '*'
        self.tag_filter = str(self.tag)
        self.search_filter = [{'Name' : 'tag:Name', 'Values' : [self.tag_filter]}]

    def do_cmd(self):
        """ main command handler """
        if self.cmd_cfg['command'] == 'describe':
            return self.describe()
        if self.cmd_cfg['command'] == 'create':
            return self.create()
        if self.cmd_cfg['command'] == 'modify':
            return self.modify()
        if self.cmd_cfg['command'] == 'destroy':
            return self.destroy()
        return False

    def create(self):
        """ create the elbv2(s)  """
        print('create TODO')

    def describe(self):
        """ get the elbv2(s) info """
        print('describe TODO')

    def modify(self):
        """ modify the elbv2(s) """
        print('modify TODO')

    def destroy(self):
        """ destroy the elbv2(s) """
        print('destroy TODO')
