# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8:noet:tabstop=4:softtabstop=4:shiftwidth=8:expandtab

""" python3 class """

# Copyright (c)  2010 - 2020, © Badassops LLC / Luc Suryo
# All rights reserved.
# BSD 3-Clause License : http://www.freebsd.org/copyright/freebsd-license.html

from pprint import PrettyPrinter
from logging import critical, warning
import awsbuild.const as const
from awsbuild.misc.spinner import spin_message
from awsbuild.aws.tag import create_resource_id_tag as set_tag

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
        if self.cmd_cfg['command'] == 'destroy':
            return self.destroy()
        return False

    def create(self, **kwargs):
        """ create a NAT gateway  """
        eip = kwargs.get('eip', {})
        subnet = kwargs.get('subnet', {})
        tag = kwargs.get('tag', {})
        try:
            nat_gate_session = self.session.get_client_session(service='ec2')
            obj_nat_gate = nat_gate_session.create_nat_gateway(
                AllocationId=eip,
                SubnetId=subnet
            )
            spin_message(
                message='Waiting {} seconds for the nat gateway to become available'.\
                    format(const.TIMER),
                seconds=const.TIMER
            )
            set_tag(session=nat_gate_session, resource_id=obj_nat_gate['NatGateway']['NatGatewayId'],\
                tag_name='Name', tag_value=tag)
            return obj_nat_gate['NatGateway']['NatGatewayId']
        except Exception as err:
            critical('Unable to create the nat gateway, error {}'.format(err))
            return None

    def describe(self):
        """ get the NAT gateway(s) info """
        nat_gate_info = self.__get_info(session=self.session,\
            filters=self.filter)
        if len(nat_gate_info['NatGateways']) == 0:
            print('\n⚬ No nat gateway found, filter {}'.format(self.filter))
            return
        output = PrettyPrinter(indent=2, width=41, compact=False)
        for info in nat_gate_info['NatGateways']:
            print('\n⚬ NAT gateway ID {}'.format(info['NatGatewayId']))
            output.pprint(info)

    def get_info(self):
        """ get the NAT gateway(s) info """
        nat_gate_info = self.__get_info(session=self.session,\
            filters=self.filter)
        if len(nat_gate_info['NatGateways']) == 0:
            return None
        return nat_gate_info

    def destroy(self, **kwargs):
        """ destroy a NAT gateway """
        nat_gateway_id = kwargs.get('id', {})
        try:
            nat_gate_session = self.session.get_client_session(service='ec2')
            nat_gate_session.delete_nat_gateway(
                NatGatewayId=nat_gateway_id
            )
            return True
        except Exception as err:
            critical('Unable to delete the gateway {}, error {}'.\
                format(nat_gateway_id, err))
            return False

    @classmethod
    def __get_info(cls, **kwargs):
        """ get info """
        cls.session = kwargs.get('session', {})
        cls.filters = kwargs.get('filters', {})
        try:
            cls.nat_gate_session = cls.session.get_client_session(service='ec2')
            nat_gate_info = cls.nat_gate_session.describe_nat_gateways(
                Filters=cls.filters
            )
            return nat_gate_info
        except Exception as err:
            warning('Unable to get info of the nat gateway(s), filter {}. Error: {}'.\
                format(cls.filters, err))
            return None
