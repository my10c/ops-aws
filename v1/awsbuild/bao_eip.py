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
#* File           :    bao_eip.py
#* Description    :    class to perform certain methode to AWS EIP
#* Author         :    Luc Suryo <luc@badassops.com>
#* Version        :    0.2
#* Date           :    Feb 21, 2019
#*
#* History    :
#*     Date:          Author:        Info:
#*    Jun 1, 2010     LIS            First Release
#*    Feb 21, 2019    LIS            refactored

# NOTE: EIP does not have EC2 resource

from logging import critical, warning
from bao_const import WAIT_TIMER
from bao_spinner import spin_message
from bao_set_tag import set_tag_client

class AwsEIP():
    """ Class to perform certain method to AWS EIP
    """

    def __init__(self, **kwargs):
        """ initial the object """
        self.vpc_conn = None
        self.aws_conn = kwargs.get('aws_conn', {})
        self.ec2_client = self.aws_conn['ec2_client']

    def create_eip(self, **kwargs):
        """ allocate an public IP """
        tag = kwargs.get('tag', {})
        try:
            ip_info = self.ec2_client.allocate_address(
                Domain='vpc'
            )
        except Exception as err:
            critical('Unable allocate_address, ignored, error {}'.format(err))
            return None
        # need to for the ip to be come available!
        spin_message(
            message='Waiting {} seconds for the EIP to become available.'.format(WAIT_TIMER),
            seconds=WAIT_TIMER
        )
        set_tag_client(ec2_client=self.ec2_client, resource_id=ip_info['AllocationId'], tag=tag)
        return ip_info['AllocationId']

    def delete_eip(self, **kwargs):
        """ delete the EIPs """
        eips_list = kwargs.get('eips_list', [])
        state_ok = True
        # we ignore any issue, we just log the issue
        for allocation_id in eips_list:
            try:
                self.ec2_client.release_address(
                    AllocationId=allocation_id
                )
            except Exception as err:
                warning('Unable to release elastic ip, ignored, error {}'.format(err))
                state_ok = False
        return state_ok

    def associate_eip(self, **kwargs):
        """ associate the given EIP (id) to the given instance """
        instance_id = kwargs.get('instance_id', {})
        eip_id = kwargs.get('eip_id', {})
        try:
            self.ec2_client.associate_address(
                InstanceId=instance_id,
                AllocationId=eip_id
            )
            return True
        except Exception as err:
            warning('Unable to associate the EIP, error {}'.format(err))
            return False

    def disassociate_eip(self, **kwargs):
        """ disassociate the given EIP (id) """
        eip_id = kwargs.get('eip_id', {})
        try:
            self.ec2_client.disassociate_address(
                AllocationId=eip_id
            )
        except Exception as err:
            warning('Unable to disassociate the EIP, ignored, error {}'.format(err))
        try:
            self.ec2_client.release_address(
                AllocationId=eip_id
            )
            return True
        except Exception as err:
            warning('Unable to release the EIP, error {}'.format(err))
            return False

    def get_eip_info(self, **kwargs):
        """ get all the elastic ips """
        eip_list = []
        filter_name = kwargs.get('filter_name', {})
        filter_value = kwargs.get('filter_value', {})
        search_filter = [{'Name' : filter_name, 'Values' : [filter_value]}]
        try:
            eips = self.ec2_client.describe_addresses(
                Filters=search_filter
            )
        except Exception as err:
            warning('Unable to get the EIPs info error {}'.format(err))
            return None
        for elastic_ip in eips['Addresses']:
            for elastic_info in elastic_ip:
                if elastic_info == 'AllocationId':
                    eip_list.append(elastic_ip[elastic_info])
        return eip_list
