# vim:fileencoding=utf-8:noet

""" python class """

# Copyright (c)  2010 - 2019, © Badassops LLC / Luc Suryo
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#*
#* File           :    bao_route_table.py
#* Description    :    class to perform certain method to AWS route table
#* Author         :    Luc Suryo <luc@badassops.com>
#* Version        :    0.2
#* Date           :    Feb 21, 2019
#*
#* History    :
#*     Date:          Author:        Info:
#*    Jun 1, 2010     LIS            First Release
#*    Feb 21, 2019    LIS            refactored

from logging import critical, warning
from bao_const import WAIT_TIMER
from bao_spinner import spin_message
from bao_set_tag import set_tag

class AwsRouteTable():
    """ Class to perform certain method to AWS route table
    """

    def __init__(self, **kwargs):
        """ initial the object """
        # The route are always used as default route
        self.dest_cidr = '0.0.0.0/0'
        self.dest_cidrv6 = '::/0'
        self.route_table = None
        self.route_table_id = None
        self.route_table_id_main = None
        self.aws_conn = kwargs.get('aws_conn', {})
        self.ec2_client = self.aws_conn['ec2_client']
        self.ec2_resource = self.aws_conn['ec2_resource']
        self.vpc_id = kwargs.get('vpc_id', {})
        self.tag = kwargs.get('tag', {})
        self.ipv6 = kwargs.get('ipv6', False)
        # DANGER WILL ROBINSON : we using wildcard as filter!
        self.tag_filter = '*' + str(self.tag) + '*'
        self.search_filter = [{'Name' : 'tag:Name', 'Values' : [self.tag_filter]}]

    def create_fe_route_table(self, **kwargs):
        """ create the route table for the fe network """
        tag = self.tag + '-fe'
        subnets_id = kwargs.get('subnets_id', [])
        internet_gateway = kwargs.get('internet_gateway', {})
        main_route_table = kwargs.get('main_route_table', {})
        # setup route to use the internet gateway as the default gateway, first ipv4
        try:
            main_route_table.create_route(
                DestinationCidrBlock=self.dest_cidr,
                GatewayId=internet_gateway
            )
        except Exception as err:
            critical('Unable to create the default route for the fe ipv4 network, error {}'.format(err))
            return None
        if self.ipv6 is True:
            # setup route to use the internet gateway as the default gateway, now ipv6
            try:
                main_route_table.create_route(
                    DestinationIpv6CidrBlock=self.dest_cidrv6,
                    GatewayId=internet_gateway
                )
            except Exception as err:
                critical('Unable to create the default route for the fe ipv6 network, error {}'.format(err))
                return None
        for subnet_id in subnets_id:
            if not self._route_associate_subnet(route_table=main_route_table, subnet_id=subnet_id):
                return False
        set_tag(obj=main_route_table, tag=tag)
        return True

    def create_be_route_table(self, **kwargs):
        """ create the route for the be network """
        subnet_id = kwargs.get('subnet_id')
        nat_gateway = kwargs.get('nat_gateway', {})
        zone_name = kwargs.get('zone_name', {})
        tag = self.tag + '-' + zone_name + '-be'
        be_route_table = self._create_route_table(tag=tag)
        if not be_route_table:
            critical('Unable to create the route resource for the be network')
            return False
        # setup route to use the NAT gateway as the default gateway, only ipv4
        try:
            be_route_table.create_route(
                DestinationCidrBlock=self.dest_cidr,
                NatGatewayId=nat_gateway
            )
        except Exception as err:
            critical('Unable to create the route for the be network, error {}'.format(err))
            return None
        if not self._route_associate_subnet(route_table=be_route_table, subnet_id=subnet_id):
            return False
        return True

    def delete_route_table(self, **kwargs):
        """ delete a route """
        self.route_table_id = kwargs.get('route_table_id', None)
        subnets = kwargs.get('subnets', None)
        route_table = self.set_route_resource()
        if not route_table:
            return False
        try:
            self._route_table_dissociate_subnet(route_table=route_table, subnets=subnets)
            route_table.delete()
            return True
        except Exception as err:
            critical('Unable to delete the route , error {}'.format(err))
            return False

    def get_default_route(self):
        """ return the main (default) route table """
        if self.route_table_id_main:
            return self.route_table_id_main
        routes = self.get_route_info()
        if not routes:
            return None
        return self.route_table_id_main

    def get_route_info(self):
        """ get the routes info """
        routes_data = {}
        try:
            routes = self.ec2_client.describe_route_tables(
                Filters=self.search_filter
            )
            for k in routes['RouteTables']:
                for k1 in k['Associations']:
                    if k1['Main']:
                        self.route_table_id_main = k1['RouteTableId']
                if k['RouteTableId'] == self.route_table_id_main:
                    routes_data[k['RouteTableId']] = 'main'
                else:
                    routes_data[k['RouteTableId']] = 'local'
            return routes_data
        except Exception as err:
            warning('Unable to get the route info, error {}'.format(err))
            return None

    def set_route_resource(self):
        """ get the route object """
        try:
            self.route_table = self.ec2_resource.Route(self.route_table_id, self.dest_cidr)
            return self.route_table
        except Exception as err:
            critical('Unable to get the route resource with id {}, error {}'.format(self.route_table_id, err))
            return None

    def _create_route_table(self, **kwargs):
        """ create a routing table """
        route_table_tag = kwargs.get('tag', {})
        try:
            route_table = self.ec2_resource.create_route_table(
                VpcId=self.vpc_id
            )
        except Exception as err:
            critical('Unable to create the route, error {}'.format(err))
            return None
        spin_message(
            message='Waiting {} seconds for the routing table to become available.'.format(WAIT_TIMER),
            seconds=WAIT_TIMER
        )
        set_tag(obj=route_table, tag=route_table_tag)
        return route_table

    @classmethod
    def _route_associate_subnet(cls, **kwargs):
        """ associate subnet to route table """
        associate_state = True
        route_table = kwargs.get('route_table', None)
        subnet_id = kwargs.get('subnet_id')
        try:
            route_table.associate_with_subnet(
                SubnetId=subnet_id
            )
        except Exception as err:
            warning('Unable to associate the subnet with the route table, error {}'.format(err))
            associate_state = False
        return associate_state

    @classmethod
    def _route_table_dissociate_subnet(cls, **kwargs):
        """ dissociate subnet to route table """
        disassociate_state = True
        route_table = kwargs.get('route_table', None)
        subnet_id = kwargs.get('subnet_id')
        try:
            route_table.disassociate_route_table(
                SubnetId=subnet_id
            )
        except Exception as err:
            warning('Unable to disassociate the subnet with the route table, error {}'.format(err))
            disassociate_state = False
        return disassociate_state
