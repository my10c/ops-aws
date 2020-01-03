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
#* File           :    bao_nat_gateway.py
#* Description    :    class to perform certain method to AWS nat gateway
#* Author         :    Luc Suryo <luc@badassops.com>
#* Version        :    0.2
#* Date           :    Feb 21, 2019
#*
#* History    :
#*     Date:          Author:        Info:
#*    Jun 1, 2010     LIS            First Release
#*    Feb 21, 2019    LIS            refactored

# NOTE: Nat Gateway does not have EC2 resource

from logging import critical, warning
from bao_const import WAIT_TIMER
from bao_spinner import spin_message
from bao_set_tag import set_tag_client

class AwsNatGateway():
    """ Class to perform certain method to AWS NAT gateway
    """

    def __init__(self, **kwargs):
        """ initial the object """
        self.aws_conn = kwargs.get('aws_conn', {})
        self.ec2_client = self.aws_conn['ec2_client']
        self.tag = kwargs.get('tag', {})

    def create_nat_gateway(self, **kwargs):
        """ create a internet gateway """
        eip_id = kwargs.get('eip_id', {})
        tag = kwargs.get('tag', {})
        subnet_id = kwargs.get('subnet_id', {})
        try:
            nat_gateway = self.ec2_client.create_nat_gateway(
                AllocationId=eip_id,
                SubnetId=subnet_id
            )
        except Exception as err:
            critical('Unable to create the internet nat, error {}'.format(err))
            return None
        spin_message(
            message='Waiting {} seconds for the NAT gateway to become available.'.format(WAIT_TIMER),
            seconds=WAIT_TIMER
        )
        nat_gateway_id = nat_gateway['NatGateway']['NatGatewayId']
        set_tag_client(ec2_client=self.ec2_client, resource_id=nat_gateway_id, tag=tag)
        return nat_gateway_id

    def delete_nat_gateway(self, **kwargs):
        """ delete the internet gateway """
        nat_gateway_id = kwargs.get('nat_gateway_id', {})
        try:
            self.ec2_client.delete_nat_gateway(
                NatGatewayId=nat_gateway_id
            )
            return True
        except Exception as err:
            critical('Unable to delete the internet gateway, error {}'.format(err))
            return False

    def get_nat_gateway_info(self, **kwargs):
        """ get the nat gateway info of the given vpc """
        vpc_id = kwargs.get('vpc_id', {})
        search_filter = [{'Name' : 'vpc-id', 'Values' : [vpc_id]}]
        # we assume there is only 1 nat gateway with the set tag
        try:
            nat_gateway = self.ec2_client.describe_nat_gateways(
                Filters=search_filter
            )
            return nat_gateway
        except Exception as err:
            warning('Unable to get the nat gateway info, error {}'.format(err))
            return None

    def get_nat_gateways_id(self, **kwargs):
        """ get the nat gateway ids of the given vpc """
        nat_gateway_id = []
        vpc_id = kwargs.get('vpc_id', {})
        nat_gateway = self.get_nat_gateway_info(vpc_id=vpc_id)
        if nat_gateway is None:
            return None
        for k in nat_gateway['NatGateways']:
            if k['NatGatewayId']:
                nat_gateway_id.append(k['NatGatewayId'])
        return nat_gateway_id
