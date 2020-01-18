# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8:noet:tabstop=4:softtabstop=4:shiftwidth=8:expandtab

""" python3 class """

# Copyright (c)  2010 - 2020, © Badassops LLC / Luc Suryo
# All rights reserved.
# BSD 3-Clause License : http://www.freebsd.org/copyright/freebsd-license.html

from pprint import PrettyPrinter
from logging import critical, warning


class RouteTable():
    """ Class for the AWS Route Table
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
        """ create a route table in the vpc  """
        print('create TODO')

    def describe(self):
        """ get the route table(s) info in the vpc"""
        route_table_info = self.__get_info(session=self.session,\
              filters=self.filter)
        if len(route_table_info['RouteTables']) == 0:
            print('\n⚬ No route table found, filter {}'.format(self.filter))
            return
        output = PrettyPrinter(indent=2, width=41, compact=False)
        for info in route_table_info['RouteTables']:
            print('\n⚬ Route table id {}'.format(info['RouteTableId']))
            output.pprint(info)

    def get_info(self):
        """ get the internet gateway(s) info in the vpc """
        route_table_info = self.__get_info(session=self.session,\
              filters=self.filter)
        if len(route_table_info['RouteTables']) == 0:
            return None
        return route_table_info

    def modify(self):
        """ modify a route table in the vpc """
        print('modify TODO')

    def destroy(self):
        """ destroy a route table in the vpc"""
        print('destroy TODO')

    @classmethod
    def __get_info(cls, **kwargs):
        """ get info """
        cls.session = kwargs.get('session', {})
        cls.filters = kwargs.get('filters', {})
        try:
            cls.route_table_session = cls.session.get_client_session(service='ec2')
            route_table_info = cls.route_table_session.describe_route_tables(
                Filters=cls.filters
            )
            return route_table_info
        except Exception as err:
            warning('Unable to get info of the route table filter {}, error: {}'.\
                  format(cls.filters, err))
            return None
