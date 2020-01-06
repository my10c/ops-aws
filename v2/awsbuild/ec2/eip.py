# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8:noet:tabstop=4:softtabstop=4:shiftwidth=8:expandtab

""" python3 class """

# Copyright (c)  2010 - 2020, © Badassops LLC / Luc Suryo
# All rights reserved.
# BSD 3-Clause License : http://www.freebsd.org/copyright/freebsd-license.html

from pprint import PrettyPrinter
from logging import critical, warning


class EIP():
    """ Class for the AWS EIP
    """

    def __init__(self, **kwargs):
        """ initial the object """
        self.cmd_cfg = kwargs.get('cmd_cfg', {})
        self.session = kwargs.get('session', {})
        self.tag = self.cmd_cfg['tag']

        # DANGER WILL ROBINSON : we using wildcard as filter!
        self.tag_filter = str('*' + self.tag + '*')
        self.filter = [{'Name' : 'tag:Name', 'Values' : [self.tag_filter]}]

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
        """ create a eip  """
        print('create TODO')

    def describe(self):
        """ get the eip(s) info """
        try:
            eip_session = self.session.get_client_session(service='ec2')
            eip_info = eip_session.describe_addresses(
                Filters=self.filter
            )
            if len(eip_info['Addresses']) == 0:
                print('\n⚬ No EIP found, filter {}'.format(self.filter))
                return True
            output = PrettyPrinter(indent=2, width=41, compact=False)
            for info in eip_info['Addresses']:
                print('\n⚬ EIP ID {}'.format(info['AllocationId']))
                output.pprint(info)
            return True
        except Exception as err:
            warning('Unable to get info EIP. Error: {}'.format(err))
            return None

    def modify(self):
        """ modify the eip(s)"""
        print('modify TODO')

    def destroy(self):
        """ destroy the eip(s) """
        print('destroy TODO')
