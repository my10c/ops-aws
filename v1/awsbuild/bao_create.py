# vim:fileencoding=utf-8:noet

""" python function """

# Copyright (c)  2010 - 2019, © Badassops LLC / Luc Suryo
#  All rights reserved.
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
#* File           :    bao_create.py
#* Description    :    python class to create or delete a VPC and it components
#* Author         :    Luc Suryo <luc@badassops.com>
#* Version        :    0.2
#* Date           :    Feb 21, 2019
#*
#* History    :
#*     Date:          Author:        Info:
#*    Jun 1, 2010     LIS            First Release
#*    Mar 30, 2019    LIS            refactored

import sys
from time import strftime
from bao_network import set_network_config, get_cidr
from bao_vpc import AwsVPC
from bao_eip import AwsEIP
from bao_subnet import AwsSubnet
from bao_internet_gateway import AwsInternetGateway
from bao_nat_gateway import AwsNatGateway
from bao_route_table import AwsRouteTable

class BaoCreate():
    """ Class to create or delete a VPC and it components
    """

    def __init__(self, **kwargs):
        """ initial the object """
        self.aws_conn = kwargs.get('aws_conn', {})
        self.net_config = kwargs.get('net_config', {})
        self.tag = kwargs.get('tag', {})
        self.ipv6 = kwargs.get('ipv6', False)
        self.vpc_conn = None
        self.vpc_id = None
        self.vpc_route_table = None
        self.subnet_conn = None
        self.subnets_fe_id = []
        self.subnets_be_id = {}
        self.int_gate_id = None
        self.nat_gate_info = {}

    def _create_vpc(self):
        """ create the VPC and update the network configuration with the ipv6 detail """
        # for create we only need to know the CIDR block first
        vpc_cidr = get_cidr(dc_cfg=self.net_config)
        self.vpc_conn = AwsVPC(aws_conn=self.aws_conn, tag=self.tag, cidr=vpc_cidr)
        if not self.vpc_conn:
            print('error AwsVPC\n')
            sys.exit(-1)
        # there should be no ID yet
        if self.vpc_conn.get_vpc_id() is not None:
            print('There is already a VPC with the given tag: {}, aborted.'.format(self.tag))
            sys.exit(-1)
        print('\t--< Start creating the VPC: {} >--'.format(strftime("%c")))
        if self.vpc_conn.create() is None:
            print('error creating the VPC\n')
            sys.exit(-1)
        # get the vpc id and ipv6 details and update the net_config dict
        self.vpc_id = self.vpc_conn.get_vpc_id()
        networkv6, cidrv6 = self.vpc_conn.get_vpc_cidr(ip_type='v6', split_cidr=True)
        self.net_config.update(set_network_config(dc_cfg=self.net_config, \
            dc_cidr_v6=cidrv6, dc_network_v6=networkv6))

        # get the main route table
        self.vpc_route_table = self.vpc_conn.get_main_route_table()
        if self.vpc_route_table is None:
            print('error getting main route of the VPC\n')
            sys.exit(-1)

    def _create_subnets(self):
        """ create the subnets and  keep list of their id """
        print('\t--< create the VPC\'s subnet >--')
        self.subnet_conn = AwsSubnet(aws_conn=self.aws_conn, tag=self.tag, vpc_id=self.vpc_id)
        if not self.subnet_conn:
            print('error AwsSubnet\n')
            sys.exit(-1)
        subnet_position = 0
        for _ in self.net_config['vpc_fe_subnets']:
            subnet_id = self.subnet_conn.create_subnet(
                zone_name=self.net_config['dc_zones_names'][subnet_position], \
                subnet_cidr=self.net_config['vpc_fe_subnets'][subnet_position], \
                subnet_cidrv6=self.net_config['vpc_fe_subnets_v6'][subnet_position], \
                subnet_type='fe',
                ipv6=self.ipv6
            )
            if subnet_id is None:
                sys.exit(-1)
            subnet_position += 1
            self.subnets_fe_id.append(subnet_id)
        subnet_position = 0
        for _ in self.net_config['vpc_be_subnets']:
            subnet_id = self.subnet_conn.create_subnet(
                zone_name=self.net_config['dc_zones_names'][subnet_position], \
                subnet_cidr=self.net_config['vpc_be_subnets'][subnet_position], \
                subnet_cidrv6=self.net_config['vpc_be_subnets_v6'][subnet_position], \
                subnet_type='be',
                ipv6=self.ipv6
            )
            if subnet_id is None:
                sys.exit(-1)
            self.subnets_be_id[self.net_config['dc_zones_names'][subnet_position]] = {'subnet_id': subnet_id}
            subnet_position += 1

    def _create_internet_gateway(self):
        """ create the internet gateway and attach to VPC """
        print('\t--< create the internet gateway and attach to the VPC >--')
        int_gate_conn = AwsInternetGateway(aws_conn=self.aws_conn, tag=self.tag, vpc_id=self.vpc_id)
        if not int_gate_conn:
            print('error AwsInternetGateway\n')
            sys.exit(-1)
        self.int_gate_id = int_gate_conn.create_internet_gateway()
        if self.int_gate_id is None:
            sys.exit(-1)
        result = int_gate_conn.attach_internet_gateway()
        if result is None:
            sys.exit(-1)

    def _create_nat_gateways(self):
        """ create the NAT gateways and attach one to each fe-subnet with it own EIP """
        # get the subnet ids
        subnet_data_fe, _, _ = self.subnet_conn.get_subnet_info(fe_subnet=self.net_config['vpc_fe_subnets'], \
                           be_subnet=self.net_config['vpc_be_subnets'])
        print('\t--< create the NAT gateway and attach to each fe-subnet with it own EIP >--')
        nat_gate_conn = AwsNatGateway(aws_conn=self.aws_conn, tag=self.tag)
        if not nat_gate_conn:
            print('error nat_gate_conn\n')
            sys.exit(-1)
        eip_conn = AwsEIP(aws_conn=self.aws_conn)
        if not eip_conn:
            print('error AwsEIP\n')
            sys.exit(-1)
        for subnet_id in subnet_data_fe:
            zone_name = subnet_data_fe[subnet_id]['zone_name']
            eip_id = eip_conn.create_eip(tag=self.tag + '-' + 'nat_gate' + '-' + zone_name)
            if eip_id is None:
                sys.exit(-1)
            nat_gateway_id = nat_gate_conn.create_nat_gateway(eip_id=eip_id, subnet_id=subnet_id, \
                tag=self.tag + '-' + zone_name)
            if nat_gateway_id is None:
                sys.exit(-1)
            self.nat_gate_info[zone_name] = nat_gateway_id

    def _create_routes(self):
        """
            create the route for the fe-subnets
            create the route for the be-subnets, each subnet get it own route and own NAT gateway
        """
        print('\t--< create the route for the fe-subnets >--')
        route_conn = AwsRouteTable(aws_conn=self.aws_conn, vpc_id=self.vpc_id, tag=self.tag)
        if not route_conn:
            print('error AwsRouteTable\n')
            sys.exit(-1)
        if route_conn.create_fe_route_table(subnets_id=self.subnets_fe_id, \
                internet_gateway=self.int_gate_id, main_route_table=self.vpc_route_table) is False:
            sys.exit(1)
        print('\t--< create the route for the be-subnets, 1 route per subnet with it own NAT gateway >--')
        for subnet in self.subnets_be_id:
            zone_name = subnet
            subnet_id = self.subnets_be_id[zone_name]['subnet_id']
            nat_gate_id = self.nat_gate_info[zone_name]
            if route_conn.create_be_route_table(subnet_id=subnet_id, \
                nat_gateway=nat_gate_id, zone_name=zone_name) is False:
                sys.exit(1)

    def create(self):
        """ create tge VPC and is components """
        # start the creation process
        self._create_vpc()
        self._create_subnets()
        self._create_internet_gateway()
        self._create_nat_gateways()
        self._create_routes()

    def get_vpc_detail(self):
        """ get the new vpc detail """
        vpc_detail = {}
        vpc_detail['vpc_id'] = self.vpc_id
        vpc_detail['subnets_fe'] = self.subnets_fe_id
        vpc_detail['subnets_be'] = self.subnets_be_id
        vpc_detail['vpc_int_gate'] = self.int_gate_id
        vpc_detail['vpc_nat_gate'] = self.nat_gate_info
        vpc_detail['vpc_route_table'] = self.vpc_route_table
        return vpc_detail
