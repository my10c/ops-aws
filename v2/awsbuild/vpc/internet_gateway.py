# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8:noet:tabstop=4:softtabstop=4:shiftwidth=8:expandtab

""" python3 class """

# Copyright (c)  2010 - 2020, © Badassops LLC / Luc Suryo
# All rights reserved.
# BSD 3-Clause License : http://www.freebsd.org/copyright/freebsd-license.html

from pprint import PrettyPrinter
from logging import critical, warning


class InternetGateway():
    """ Class for AWS Internet Gateway
    """

    def __init__(self, **kwargs):
        """ initial the object """
        self.cmd_cfg = kwargs.get('cmd_cfg', {})
        self.session = kwargs.get('session', {})
        self.name = self.cmd_cfg['name']
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
        """ create a internet gateway  """
        print('create TODO')

    def describe(self):
        """ get the internet gateway(s) info in the vpc """
        int_gate_info = self.__get_info(session=self.session,\
            filters=self.filter)
        if len(int_gate_info['InternetGateways']) == 0:
            print('\n⚬ No Internet Gateway found, filter {}'.format(self.filter))
            return
        output = PrettyPrinter(indent=2, width=41, compact=False)
        for info in int_gate_info['InternetGateways']:
            print('\n⚬ Internet Gateway ID {}'.format(info['InternetGatewayId']))
            output.pprint(info)

    def get_info(self):
        """ get the internet gateway(s) info in the vpc """
        int_gate_info = self.__get_info(session=self.session,\
            filters=self.filter)
        if len(int_gate_info['InternetGateways']) == 0:
            return None
        return int_gate_info

    def modify(self):
        """ modify the internet gateway """
        print('modify TODO')

    def destroy(self):
        """ destroy the internet gateway"""
        print('destroy TODO')

    @classmethod
    def __get_info(cls, **kwargs):
        """ get info """
        cls.session = kwargs.get('session', {})
        cls.filters = kwargs.get('filters', {})
        try:
            cls.int_gate_session = cls.session.get_client_session(service='ec2')
            int_gate_info = cls.int_gate_session.describe_internet_gateways(
                Filters=cls.filters
            )
            return int_gate_info
        except Exception as err:
            warning('Unable to get info of the Internet gateway(s), filter {}. Error: {}'.\
                format(cls.filters, err))
            return None
