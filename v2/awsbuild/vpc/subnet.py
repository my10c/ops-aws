# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8:noet:tabstop=4:softtabstop=4:shiftwidth=8:expandtab

""" python3 class """

# Copyright (c)  2010 - 2020, © Badassops LLC / Luc Suryo
# All rights reserved.
# BSD 3-Clause License : http://www.freebsd.org/copyright/freebsd-license.html

from pprint import PrettyPrinter
from logging import warning


class Subnet():
    """ Class for the AWS Subnet
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
        """ create a subnet in the vpc  """
        print('create TODO')

    def describe(self):
        """ get the subnets info in the vpc"""
        subnet_info = self.__get_info(session=self.session,\
            filters=self.filter)
        if len(subnet_info['Subnets']) == 0:
            print('\n⚬ No Subnet found, filter {}'.format(self.filter))
            return
        output = PrettyPrinter(indent=2, width=41, compact=False)
        for info in subnet_info['Subnets']:
            print('\n⚬ Subnet ID {}'.format(info['SubnetId']))
            output.pprint(info)

    def modify(self):
        """ modify a subnet in the vpc """
        print('modify TODO')

    def destroy(self):
        """ destroy a subnet in the vpc"""
        print('destroy TODO')

    @classmethod
    def __get_info(cls, **kwargs):
        """ get vpc info """
        cls.session = kwargs.get('session', {})
        cls.filters = kwargs.get('filters', {})
        try:
            cls.subnet_session = cls.session.get_client_session(service='ec2')
            subnet_info = cls.subnet_session.describe_subnets(
                Filters=cls.filters
            )
            return subnet_info
        except Exception as err:
            warning('Unable to get the subnet info, filter {}. error {}'.\
                format(cls.filters, err))
            return None
