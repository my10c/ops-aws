# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8:noet:tabstop=4:softtabstop=4:shiftwidth=8:expandtab

""" python3 class """

# Copyright (c)  2010 - 2020, © Badassops LLC / Luc Suryo
# All rights reserved.
# BSD 3-Clause License : http://www.freebsd.org/copyright/freebsd-license.html

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
