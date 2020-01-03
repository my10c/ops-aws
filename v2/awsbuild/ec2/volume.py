# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8:noet:tabstop=4:softtabstop=4:shiftwidth=8:expandtab

""" python3 class """

# Copyright (c)  2010 - 2020, © Badassops LLC / Luc Suryo
# All rights reserved.
# BSD 3-Clause License : http://www.freebsd.org/copyright/freebsd-license.html

from logging import critical, warning
from bao_const import WAIT_TIMER
from bao_spinner import spin_message
from bao_set_tag import set_tag

class AwsVolume():
    """ Class to perform certain method to AWS EBS Volume
    """

    def __init__(self, **kwargs):
        """ initial the object """
        self.volume = None
        self.volume_id = None
        self.aws_conn = kwargs.get('aws_conn', {})
        self.ec2_client = self.aws_conn['ec2_client']
        self.ec2_resource = self.aws_conn['ec2_resource']
        self.tag = kwargs.get('tag', {})

    def create_volume(self, **kwargs):
        """ create a volume in the given zone and given size """
        volume_size = int(kwargs.get('volume_size', {}))
        volume_zone = kwargs.get('volume_zone', {})
        volume_tag = kwargs.get('volume_tag', {})
        try:
            volume = self.ec2_resource.create_volume(
                Size=volume_size,
                AvailabilityZone=volume_zone,
            )
        except Exception as err:
            critical('Unable to create_volume, error {}'.format(err))
            return None
        spin_message(
            message='Waiting {} seconds for the volume to become available.'.format(WAIT_TIMER),
            seconds=WAIT_TIMER
        )
        self.volume_id = volume.id
        set_tag(obj=volume, tag=volume_tag)
        return volume

    def delete_volume(self, **kwargs):
        """ delete the volume with the given volume_id """
        self.volume_id = kwargs.get('volume_id', {})
        volume = self.set_volume_resource()
        if not volume:
            return False
        try:
            volume.delete()
            return True
        except Exception as err:
            critical('Unable to delete the volume, error {}'.format(err))
            return False

    def attach_volume(self, **kwargs):
        """ attach the given volume id to the given instance id
           NOTE: default device is /dev/sdd
        """
        self.volume_id = kwargs.get('volume_id', {})
        instance_id = kwargs.get('instance_id', {})
        device_name = kwargs.get('device_name', '/dev/sdd')
        volume = self.set_volume_resource()
        if not volume:
            return False
        try:
            volume.attach_to_instance(
                Device=device_name,
                InstanceId=instance_id
            )
            return True
        except Exception as err:
            warning('Unable to attach volumes, error {}'.format(err))
            return None

    def detach_volume(self, **kwargs):
        """ detach the given volume id, default to force mode
        """
        self.volume_id = kwargs.get('volume_id', {})
        force = kwargs.get('force', True)
        volume = self.set_volume_resource()
        if not volume:
            return False
        try:
            volume.detach_from_instance(Force=force)
            return True
        except Exception as err:
            warning('Unable to detach volumes, error {}'.format(err))
            return None

    def get_volume_info(self):
        """ get all the volumes info """
        volume_data = {}
        try:
            volumes = self.ec2_client.describe_volumes()
            for v in volumes['Volumes']:
                volume_instance = 'none'
                volume_id = v['VolumeId']
                volume_state = v['State']
                for k in v['Attachments']:
                    volume_instance = k['InstanceId']
                for k1 in v['Tags']:
                    if k1['Key'] == 'Name':
                        volume_tag = k1['Value']
                volume_data[volume_id] = [volume_state, volume_instance, volume_tag]
            return volume_data
        except Exception as err:
            warning('Unable to get the volumes info, error {}'.format(err))
            return None

    def search_volume(self, **kwargs):
        """ return the volume id with the given tag  """
        tag = kwargs.get('tag', {})
        tag_filter = '*' + str(tag) + '*'
        search_filter = [{'Name' : 'tag:Name', 'Values' : [tag_filter]}]
        volume_list = {}
        try:
            volumes_status = self.ec2_client.describe_volumes(
                Filters=search_filter
            )
            for k in volumes_status['Volumes']:
                for k1 in k['Tags']:
                    volume_tag = 'not-set'
                    if k1['Key'] == 'Name':
                        volume_tag = k1['Value']
                volume_list[k['VolumeId']] = volume_tag
        except Exception as err:
            warning('Unable to get the volumes status, error {}'.format(err))
            return None
        return volume_list

    def status_volume(self):
        """ return the status the set volumes id """
        try:
            volumes_status = self.ec2_client.describe_volumes(
                VolumeIds=[self.volume_id]
            )
            for v in volumes_status['Volumes']:
                return v['State']
        except Exception as err:
            warning('Unable to get the volumes status, error {}'.format(err))
            return None

    def set_volume_resource(self):
        """ get the volume object """
        try:
            self.volume = self.ec2_resource.Volume(self.volume_id)
            return self.volume
        except Exception as err:
            critical('Unable to get the volume resource with id {}, error {}'.format(self.volume_id, err))
            return False
