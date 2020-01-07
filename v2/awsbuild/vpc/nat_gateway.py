# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8:noet:tabstop=4:softtabstop=4:shiftwidth=8:expandtab

""" python3 class """

# Copyright (c)  2010 - 2020, © Badassops LLC / Luc Suryo
# All rights reserved.
# BSD 3-Clause License : http://www.freebsd.org/copyright/freebsd-license.html

from pprint import PrettyPrinter
from logging import critical, warning


class NATGateway():
    """ Class for the AWS NAT Gateaway
    """

    def __init__(self, **kwargs):
        """ initial the object """
        self.cmd_cfg = kwargs.get('cmd_cfg', {})
        self.session = kwargs.get('session', {})
        self.tag = self.cmd_cfg['tag']
        self.name = self.cmd_cfg['name']

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
        """ create the NAT gateway  """
        print('create TODO')

    def describe(self):
        """ get the NAT gateway(s) info in the vpc """
        nat_gate_info = self.__get_info(session=self.session,\
            filters=self.filter)
        if len(nat_gate_info['NatGateways']) == 0:
            print('\n⚬ No NAT Gateway found, filter {}'.format(self.filter))
            return
        output = PrettyPrinter(indent=2, width=41, compact=False)
        for info in nat_gate_info['NatGateways']:
            print('\n⚬ NAT Gateway ID {}'.format(info['NatGatewayId']))
            output.pprint(info)

    def get_info(self):
        """ get the internet gateway(s) info in the vpc """
        nat_gate_info = self.__get_info(session=self.session,\
            filters=self.filter)
        if len(nat_gate_info['NatGateways']) == 0:
            return None
        return nat_gate_info

    def modify(self):
        """ modify the NAT gateway """
        print('modify TODO')

    def destroy(self):
        """ destroy the NAT gateway """
        print('destroy TODO')

    @classmethod
    def __get_info(cls, **kwargs):
        """ get info """
        cls.session = kwargs.get('session', {})
        cls.filters = kwargs.get('filters', {})
        try:
            cls.nat_gate_session = cls.session.get_client_session(service='ec2')
            nat_gate_info = cls.nat_gate_session.describe_internet_gateways(
                Filters=cls.filters
            )
            return nat_gate_info
        except Exception as err:
            warning('Unable to get info of the Internet gateway(s), filter {}. Error: {}'.\
                format(cls.filters, err))
            return None
