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
#* File           :    bao_vpc.py
#* Description    :    class to perform certain method to AWS vpc
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

class AwsVPC():
    """ Class the object to perform certain method in a AWS VPC
    """

    def __init__(self, **kwargs):
        """ initial the object """
        self.vpc = None
        self.vpc_id = None
        self.aws_conn = kwargs.get('aws_conn', {})
        self.ec2_client = self.aws_conn['ec2_client']
        self.ec2_resource = self.aws_conn['ec2_resource']
        self.cidr = kwargs.get('cidr', {})
        self.tag = kwargs.get('tag', {})
        self.ipv6 = kwargs.get('ipv6', False)
        # DANGER WILL ROBINSON : we using wildcard as filter!
        #self.tag_filter = '*' + str(self.tag) + '*'
        self.tag_filter = str(self.tag)
        self.search_filter = [{'Name' : 'tag:Name', 'Values' : [self.tag_filter]}]

    def create(self):
        """ create a VPC, check if we need to setup IPv6 """
        try:
            self.vpc = self.ec2_resource.create_vpc(
                CidrBlock=self.cidr,
                AmazonProvidedIpv6CidrBlock=self.ipv6
            )
        except Exception as err:
            critical('Unable to create the VPC. Error: {}'.format(err))
            return None
        spin_message(
            message='Waiting {} seconds for the VPC to become available.'.format(WAIT_TIMER),
            seconds=WAIT_TIMER
        )
        self.vpc_id = self.vpc.id
        set_tag(obj=self.vpc, tag=self.tag)
        self._set_dns_options()
        return self.vpc

    def destroy(self):
        """ destroy a VPC, this requires that all component to be destroyed first:
            gateways (internet and nat), instances, route tables, subnets and security groups
            we need to delete/release the EIP and volumes once the VPC has been destroyed
         """
        try:
            self.vpc.delete()
            return True
        except Exception as err:
            critical('Unable to destroy VPCs info. Error: {}'.format(err))

    def get_vpc_info(self):
        """ get the vpc info """
        # we assume there is only 1 vpc with the set tag
        try:
            vpc = self.ec2_client.describe_vpcs(
                Filters=self.search_filter
            )
            return vpc
        except Exception as err:
            warning('Unable to get the vpc info, error {}'.format(err))
            return None

    def get_vpc_cidr(self, **kwargs):
        """ get the vpc ipv4 and ipv6 cidr """
        ip_type = kwargs.get('ip_type', 'v4')
        split_cidr = kwargs.get('split_cidr', False)
        if self.vpc is None:
            critical('VPC is not set')
            if split_cidr is False:
                return None
            return None, None
        if ip_type == 'v4':
            if split_cidr is False:
                return self.vpc.cidr_block
            return self.vpc.cidr_block.split('/')[0], self.vpc.cidr_block.split('/')[1]
        try:
            _ = next(iter(self.vpc.ipv6_cidr_block_association_set), [])
        except Exception:
            warning('No IPv6 was setup in the VPC')
            if split_cidr is False:
                return None
            return None, None
        for k in self.vpc.ipv6_cidr_block_association_set:
            if 'Ipv6CidrBlock' in k:
                if split_cidr is False:
                    return k['Ipv6CidrBlock']
                return k['Ipv6CidrBlock'].split('/')[0], k['Ipv6CidrBlock'].split('/')[1]
        warning('No IPv6 Cidr block found in the VPC')
        return None, None

    def get_vpc_id(self):
        """ return the vpc id """
        if self.vpc_id:
            return self.vpc_id
        vpc = self.get_vpc_info()
        if vpc is None:
            return None
        for k in vpc['Vpcs']:
            if k['VpcId']:
                self.vpc_id = k['VpcId']
            break
        return self.vpc_id

    def get_main_route_table(self):
        """ return the main (default) route table of the vpc """
        main_route_table = []
        for route_table in list(self.vpc.route_tables.all()):
            for association in list(route_table.associations):
                if association.main is True:
                    main_route_table.append(route_table)
        if len(main_route_table) != 1:
            critical('cannot get main route table! {}'.format(main_route_table))
            return None
        return main_route_table[0]

    def set_vpc_resource(self, **kwargs):
        """ set the vpc object """
        vpc_id = kwargs.get('vpc_id', {})
        try:
            self.vpc = self.ec2_resource.Vpc(vpc_id)
            return True
        except Exception as err:
            critical('Unable to get the vpc resource with id {}, error {}'.format(self.vpc_id, err))
            return False

    def  _set_dns_options(self):
        """ set the vpc dns options """
        # ignore if failes
        # we need to modify the DNS options one at the time!
        try:
            self.vpc.modify_attribute(
                EnableDnsSupport={'Value': True}
            )
        except Exception as err:
            warning('Unable to set DNS support, error {}'.format(err))
        try:
            self.vpc.modify_attribute(
                EnableDnsHostnames={'Value': True}
            )
        except Exception as err:
            warning('Unable to set DNS hostnames, error {}'.format(err))
