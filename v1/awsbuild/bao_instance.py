#!/usr/bin/env python3

""" A python script """

# BSD 3-Clause License
#
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
#* File           :    bao_instance.py
#* Description    :    class to perform certain method to AWS EC2 instances
#* Author         :    Luc Suryo <luc@badassops.com>
#* Version        :    0.2
#* Date           :    Feb 21, 2019
#*
#* History    :
#*     Date:          Author:        Info:
#*    Jun 1, 2010     LIS            First Release
#*    March 3, 2019   LIS            refactored

from logging import critical, warning
from bao_const import WAIT_INSTANCE
from bao_spinner import spin_message

class AwsInstance():
    """ Class to perform certain method to AWS EC2 instances """

    def __init__(self, **kwargs):
        """ initial the object """
        self.instances = {}
        self.subnet_fe = {}
        self.subnet_be = {}
        self.instance_id = None
        self.aws_conn = kwargs.get('aws_conn', {})
        self.instance_cfg = kwargs.get('instance_cfg', {})
        self.ec2_client = self.aws_conn['ec2_client']
        self.ec2_resource = self.aws_conn['ec2_resource']
        self.tag = kwargs.get('tag', {})
        self.vpc_id = kwargs.get('vpc_id', {})
        self.subnet_info = kwargs.get('subnet_info', {})
        for v in self.subnet_info:
            if 'fe' in self.subnet_info[v]:
                self.subnet_fe[v] = self.subnet_info[v]
            if 'be' in self.subnet_info[v]:
                self.subnet_be[v] = self.subnet_info[v]

    def create(self):
        """ create instance """
        for instance in self.instance_cfg:
            # Dynamically get the zone/subnet location based on the available zones
            if self.instance_cfg[instance]['vpc_placement'] == 'fe':
                position_id = int(self.instance_cfg[instance]['start_sequence']) % int(len(list(self.subnet_fe)))
                subnet_id = list(self.subnet_fe)[position_id]
                subnet_zone = self.subnet_fe[subnet_id][0]
                self._launch_new_instance(instance_name=instance, instance_detail=self.instance_cfg[instance],
                                          subnet_id=subnet_id, subnet_zone=subnet_zone)
            if self.instance_cfg[instance]['vpc_placement'] == 'be':
                position_id = int(self.instance_cfg[instance]['start_sequence']) % int(len(list(self.subnet_be)))
                subnet_id = list(self.subnet_be)[position_id]
                subnet_zone = self.subnet_be[subnet_id][0]
                self._launch_new_instance(instance_name=instance, instance_detail=self.instance_cfg[instance],
                                          subnet_id=subnet_id, subnet_zone=subnet_zone)
        return True

    def stop(self):
        """ stop instance """
        instances_info = self.get_instances_info()
        for k in instances_info:
            try:
                #instance_conn = self.ec2_resource.Instance(k)
                #instance_conn.stop()
                self._wait_for_it(action='stop')
                self._get_tag_status(instance_id=k, instance_info=instances_info)
            except Exception as err:
                warning('Unable to create instance connection, error {}'.format(err))

    def start(self):
        """ start instances """
        instances_info = self.get_instances_info()
        for k in instances_info:
            try:
                #instance_conn = self.ec2_resource.Instance(k)
                #instance_conn.start()
                self._wait_for_it(action='start')
                self._get_tag_status(instance_id=k, instance_info=instances_info)
            except Exception as err:
                warning('Unable to create instance connection, error {}'.format(err))

    def status(self):
        """ get instances status in the vpc """
        instances_info = self.get_instances_info()
        for k in instances_info:
            self._get_tag_status(instance_id=k, instance_info=instances_info)

    def terminate(self):
        """ terminate instances in the vpc """
        instances_info = self.get_instances_info()
        for k in instances_info:
            try:
                instance_conn = self.ec2_resource.Instance(k)
            except Exception as err:
                warning('Unable to create instance connection, error {}'.format(err))
            try:
                instance_conn.modify_attribute(
                    DisableApiTermination={'Value': False},
                )
            except Exception as err:
                critical('Unable to remove the termination protection, error {}'.format(err))
            try:
                #instance_conn.terminate()
                self._wait_for_it(action='terminate')
                self._get_tag_status(instance_id=k, instance_info=instances_info)
            except Exception as err:
                critical('Unable to termination the instance, error {}'.format(err))

    def get_instances_info(self):
        """ get all the instances in the vpc """
        volumes_info = []
        tags_info = []
        try:
            vpc_conn = self.ec2_resource.Vpc(self.vpc_id)
        except Exception as err:
            critical('Unable to get the vpc resource with id {}, error {}'.format(self.vpc_id, err))
            return None
        try:
            ec2_instances = vpc_conn.instances.all()
        except Exception as err:
            critical('Unable to get the instances all, error {}'.format(err))
            return None
        for instance in ec2_instances:
            try:
                instance_data = self.ec2_resource.Instance(instance.id)
            except Exception as err:
                critical('Unable to get the instance connection, error {}'.format(err))
            if instance_data:
                state_info = instance_data.state['Name']
                volumes_info = []
                for volume_info in instance_data.block_device_mappings:
                    volumes_info.append(volume_info['Ebs']['VolumeId'])
                # reset the name by each pass
                if instance_data.tags:
                    tags_info = []
                    for tag in instance_data.tags:
                        if tag['Key'] == 'DNS':
                            tags_info.append('dns=' + tag['Value'])
                        if tag['Key'] == 'Name':
                            tags_info.append('name=' + tag['Value'].lower())
            self.instances[instance.id] = {'volumes': volumes_info, 'tags' : tags_info, 'state': state_info}
        return self.instances

    @classmethod
    def _get_tag_status(cls, **kwargs):
        """ return the Name tage and the instance state """
        instance_id = kwargs.get('instance_id', {})
        instance_info = kwargs.get('instance_info', {})
        instance_state = instance_info[instance_id]['state']
        for k in instance_info[instance_id]['tags']:
            tag_name = k.split('=')[0]
            if tag_name == 'name':
                host_tag = k.split('=')[1]
        print('ec2 id: {} - Host tag: {} - state {}'.format(instance_id, host_tag, instance_state))
        return True

    @classmethod
    def _wait_for_it(cls, **kwargs):
        """  spinner with wait information """
        action = kwargs.get('action', 'unknown')
        spin_message(
            message='Waiting {} seconds for the instance to {}.'.format(WAIT_INSTANCE, action),
            seconds=WAIT_INSTANCE
        )

    @classmethod
    def _launch_new_instance(cls, **kwargs):
        """
            launch and instance, create volume if required and attach the volume
            to the instance, and tag tbe instance
            we have hardcode config these are
            - count          : how many need to be created
            - start_sequence : hostid to start with
            - tags           : list of tag tobe created, dynamic
            - sec_groups     : list of security group to be assigned to the instance
            - type           : instance type
            - public_ip      : whatever its requires a public ip
            - static_ip      : whatever its requires a statis ip (AWS EIP)
            - vpc_placement  : where the instance need to be created, be == private subnet or fe == public facing subnet
            - data_volume    : list of extra volume to be created and attached
        """
        instance_name = kwargs.get('instance_name', {})
        instance_detail = kwargs.get('instance_detail', {})
        subnet_id = kwargs.get('subnet_id', {})
        subnet_zone = kwargs.get('subnet_zone', {})
        print('{} - {} {} {}\n'.format(instance_name, instance_detail, subnet_id, subnet_zone))
        #try:
