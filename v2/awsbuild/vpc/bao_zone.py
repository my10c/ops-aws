# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8:noet:tabstop=4:softtabstop=4:shiftwidth=8:expandtab

""" python3 class """

# Copyright (c)  2010 - 2020, © Badassops LLC / Luc Suryo
# All rights reserved.
# BSD 3-Clause License : http://www.freebsd.org/copyright/freebsd-license.html

# NOTE: Zone does not have EC2 resource

from logging import warning

class AwsZones():
    """ Class to perform certain method to AWS zones
    """

    def __init__(self, **kwargs):
        """ initial the object """
        self.zones_info = {}
        self.zones_name = []
        self.zones_id = []
        self.aws_conn = kwargs.get('aws_conn', {})
        self.ec2_client = self.aws_conn['ec2_client']
        self._get_zone_info()

    def get_zones_name(self):
        """ get the available zones id """
        for v in self.zones_info['AvailabilityZones']:
            self.zones_name.append(v['ZoneName'])
        return sorted(self.zones_name)

    def get_zones_id(self):
        """ get the available zones id """
        for v in self.zones_info['AvailabilityZones']:
            self.zones_id.append(v['ZoneId'])
        return sorted(self.zones_id)

    def get_zones_cnt(self):
        """ get the available zones count """
        return len(self.zones_info['AvailabilityZones'])

    def _get_zone_info(self):
        """ create a aws session with the given credentials """
        try:
            self.zones_info = self.ec2_client.describe_availability_zones()
        except Exception as err:
            warning('Could not get a AWS session: {}'.format(err))
