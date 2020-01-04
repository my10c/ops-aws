# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8:noet:tabstop=4:softtabstop=4:shiftwidth=8:expandtab

""" python3 class """

# Copyright (c)  2010 - 2020, © Badassops LLC / Luc Suryo
# All rights reserved.
# BSD 3-Clause License : http://www.freebsd.org/copyright/freebsd-license.html

from pprint import PrettyPrinter
from logging import critical, warning


class KeyPair():
    """ Class for the AWS KeyPair
    """

    def __init__(self, **kwargs):
        """ initial the object """
        self.cmd_cfg = kwargs.get('cmd_cfg', {})
        self.session = kwargs.get('session', {})
        self.tag = self.cmd_cfg['tag']
        self.name = self.cmd_cfg['name']

        # DANGER WILL ROBINSON : we using wildcard as filter!
        if self.name == 'none' :
            self.filter = [{}]
        else:
            self.filter = [{'Name' : 'key-name', 'Values' : [self.name]}]

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
        """ create a KeyPair  """

    def describe(self):
        """ get the keypair(s) info """
        try:
            keypair_session = self.session.get_client_session(service='ec2')
            key_info = keypair_session.describe_key_pairs(
                Filters=self.filter
            )
            output = PrettyPrinter(indent=2, width=41, compact=False)
            for info in key_info['KeyPairs']:
                print('\n⚬ KeyPair ID {}'.format(info['KeyPairId']))
                output.pprint(info)
            return True
        except Exception as err:
            warning('Unable to get info of the key pair named {}. Error: {}'.format(self.name, err))
            return None

    def modify(self):
        """ modify the """
        print('modify TODO')

    def destroy(self):
        """ destroy the """
        print('destroy TODO')
