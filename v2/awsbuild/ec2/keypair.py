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
        # set filter, requires exact name
        if self.name == '':
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
        """ create a keypair """
        try:
            keypair_session = self.session.get_client_session(service='ec2')
            key_info = keypair_session.import_key_pair(
                KeyName=self.name,
                PublicKeyMaterial=self.cmd_cfg['settings']['keypair'][self.name]['pubkey']
            )
            print('New create keypar: {}'.format(key_info))
            return True
        except Exception as err:
            critical('Unable to add keypair {}. Error: {}'.format(self.name, err))
            return False

    def describe(self):
        """ get the keypair(s) info """
        key_info = self.__get_info(session=self.session,\
            Filters=self.filter)
        if len(key_info['KeyPairs']) == 0:
            print('\n⚬ No keypair found, filter {}'.format(self.filter))
            return
        output = PrettyPrinter(indent=2, width=41, compact=False)
        for info in key_info['KeyPairs']:
            print('\n⚬ KeyPair ID {}'.format(info['KeyPairId']))
            output.pprint(info)

    def get_info(self):
        """ get the keypair(s) info """
        key_info = self.__get_info(session=self.session,\
            Filters=self.filter)
        if len(key_info['KeyPairs']) == 0:
            return None
        return key_info

    def modify(self):
        """ modify a keypair """
        self.destroy()
        self.create()

    def destroy(self):
        """ destroy a keypair """
        try:
            keypair_session = self.session.get_client_session(service='ec2')
            keypair_session.delete_key_pair(
                KeyName=self.name
            )
            print('Keypair {} destroyed.'.format(self.name))
            return True
        except Exception as err:
            critical('Unable to destroy keypair {}. Error: {}'.format(self.name, err))
            return False

    @classmethod
    def __get_info(cls, **kwargs):
        """ get info """
        cls.session = kwargs.get('session', {})
        cls.filters = kwargs.get('filters', {})
        try:
            cls.keypair_session = cls.session.get_client_session(service='ec2')
            key_info = cls.keypair_session.describe_key_pairs(
                Filters=cls.filters
            )
            return key_info
        except Exception as err:
            warning('Unable to get info key, error: {}'.format(err))
            return None
