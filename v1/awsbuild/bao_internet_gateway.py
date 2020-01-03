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
#* File           :    bao_internet_gateway.py
#* Description    :    class to perform certain method to AWS internet gateway
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

class AwsInternetGateway():
    """ Class to perform certain method to AWS internet gateway
    """

    def __init__(self, **kwargs):
        """ initial the object """
        self.internet_gateway_id = None
        self.internet_gateway = None
        self.aws_conn = kwargs.get('aws_conn', {})
        self.ec2_client = self.aws_conn['ec2_client']
        self.ec2_resource = self.aws_conn['ec2_resource']
        self.vpc_id = kwargs.get('vpc_id', {})
        self.tag = kwargs.get('tag', {})
        # DANGER WILL ROBINSON : we using wildcard as filter!
        #self.tag_filter = '*' + str(self.tag) + '*'
        self.tag_filter = str(self.tag)
        self.search_filter = [{'Name' : 'tag:Name', 'Values' : [self.tag_filter]}]

    def create_internet_gateway(self):
        """ create a internet gateway """
        try:
            self.internet_gateway = self.ec2_resource.create_internet_gateway()
        except Exception as err:
            critical('Unable to create the internet gateway, error {}'.format(err))
            return None
        spin_message(
            message='Waiting {} seconds for the internet gateway to become available.'.format(WAIT_TIMER),
            seconds=WAIT_TIMER
        )
        self.internet_gateway_id = self.internet_gateway.id
        set_tag(obj=self.internet_gateway, tag=self.tag)
        return self.internet_gateway_id

    def delete_internet_gateway(self):
        """ delete the internet gateway
        """
        try:
            self.internet_gateway.delete()
            return True
        except Exception as err:
            critical('Unable to delete the internet gateway, error {}'.format(err))
            return False

    def attach_internet_gateway(self):
        """ attach the internet gateway to the given vpc """
        try:
            self.internet_gateway.attach_to_vpc(
                VpcId=self.vpc_id
            )
            return True
        except Exception as err:
            critical('Unable to attach the internet gateway to vpc, error {}'.format(err))
            return False

    def detach_internet_gateway(self):
        """ detach the internet gateway from the given vpc """
        try:
            self.internet_gateway.detach_from_vpc(
                VpcId=self.vpc_id
            )
            return True
        except Exception as err:
            critical('Unable to detach the internet gateway, error {}'.format(err))
            return False

    def get_internet_gateway_info(self):
        """ get the internet gateway info """
        # we assume there is only 1 internat gateway with the set tag
        try:
            internet_gateway = self.ec2_client.describe_internet_gateways(
                Filters=self.search_filter
            )
            return internet_gateway
        except Exception as err:
            warning('Unable to get the internet gateway info, error {}'.format(err))
            return None

    def get_internet_gateways_id(self):
        """ get the internet gateway id """
        if self.internet_gateway_id:
            return self.internet_gateway_id
        internet_gateway = self.get_internet_gateway_info()
        if internet_gateway is None:
            return None
        for k in internet_gateway['InternetGateways']:
            if k['InternetGatewayId']:
                self.internet_gateway_id = k['InternetGatewayId']
            break
        return self.internet_gateway_id

    def set_internet_gateways_resource(self):
        """ set the internet gateway object """
        try:
            self.internet_gateway = self.ec2_resource.InternetGateway(self.internet_gateway_id)
            return True
        except Exception as err:
            critical('Unable to get the internet gateway resource with id {}, err {}'\
                     .format(self.internet_gateway_id, err))
            return False
