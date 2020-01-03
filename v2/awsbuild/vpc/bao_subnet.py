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
#* File           :    bao_subnet.py
#* Description    :    class to perform certain method to AWS subnet
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

class AwsSubnet():
    """ Class to perform certain method to AWS VPC subnets
    """

    def __init__(self, **kwargs):
        """ initial the object """
        self.subnet = None
        self.subnet_id = None
        self.aws_conn = kwargs.get('aws_conn', {})
        self.ec2_client = self.aws_conn['ec2_client']
        self.ec2_resource = self.aws_conn['ec2_resource']
        self.vpc_id = kwargs.get('vpc_id', {})
        self.tag = kwargs.get('tag', {})
        self.ipv6 = kwargs.get('ipv6', False)
        # DANGER WILL ROBINSON : we using wildcard as filter!
        self.tag_filter = '*' + str(self.tag) + '*'
        self.search_filter = [{'Name' : 'tag:Name', 'Values' : [self.tag_filter]}]

    def create_subnet(self, **kwargs):
        """ create a subnet """
        zone_name = kwargs.get('zone_name', {})
        subnet_cidr = kwargs.get('subnet_cidr', {})
        subnet_cidrv6 = kwargs.get('subnet_cidrv6', {})
        subnet_type = kwargs.get('subnet_type', {})
        try:
            if self.ipv6 is True:
                subnet = self.ec2_resource.create_subnet(
                    VpcId=self.vpc_id,
                    AvailabilityZone=zone_name,
                    CidrBlock=subnet_cidr,
                    Ipv6CidrBlock=subnet_cidrv6
                )
            else:
                subnet = self.ec2_resource.create_subnet(
                    VpcId=self.vpc_id,
                    AvailabilityZone=zone_name,
                    CidrBlock=subnet_cidr
                )
        except Exception as err:
            critical('Unable to create the subnet, error {}'.format(err))
            return None
        spin_message(
            message='Waiting {} seconds for the subnet to become available.'.format(WAIT_TIMER),
            seconds=WAIT_TIMER
        )
        self.subnet_id = subnet.id
        set_tag(obj=subnet, tag=self.tag + '-' + zone_name + '-' + subnet_type)
        return subnet.id

    def delete_subnet(self, **kwargs):
        """ delete a subnet """
        self.subnet_id = kwargs.get('subnet_id', {})
        subnet = self.set_subnet_resource()
        if not subnet:
            return False
        try:
            subnet.delete()
            return True
        except Exception as err:
            critical('Unable to delete the subnet , error {}'.format(err))
            return False

    def get_subnet_info(self, **kwargs):
        """ get the subnets info """
        subnet_data_fe = {}
        subnet_data_be = {}
        subnet_data_not_used = {}
        fe_subnet = kwargs.get('fe_subnet', {})
        be_subnet = kwargs.get('be_subnet', {})
        try:
            subnets = self.ec2_client.describe_subnets(
                Filters=self.search_filter
            )
        except Exception as err:
            warning('Unable to get the subnets info, error {}'.format(err))
            return None
        for subnet in subnets['Subnets']:
            zone_name = subnet['AvailabilityZone']
            zone_cidr = subnet['CidrBlock']
            if subnet['CidrBlock'] in fe_subnet:
                subnet_data_fe[subnet['SubnetId']] = {'zone_name': zone_name, 'zone_cidr': zone_cidr}
            elif subnet['CidrBlock'] in be_subnet:
                subnet_data_be[subnet['SubnetId']] = {'zone_name': zone_name, 'zone_cidr': zone_cidr}
            else:
                subnet_data_not_used[subnet['SubnetId']] = {'zone_name': zone_name, 'zone_cidr': zone_cidr}
        return subnet_data_fe, subnet_data_be, subnet_data_not_used

    def set_subnet_resource(self):
        """ get the subnet object """
        try:
            self.subnet = self.ec2_resource.Subnet(self.subnet_id)
            return self.subnet
        except Exception as err:
            critical('Unable to get the subnet resource with id {}, error {}'.format(self.subnet_id, err))
            return None
