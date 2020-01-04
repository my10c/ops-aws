# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8:noet:tabstop=4:softtabstop=4:shiftwidth=8:expandtab

""" python3 class """

# Copyright (c)  2010 - 2020, © Badassops LLC / Luc Suryo
# All rights reserved.
# BSD 3-Clause License : http://www.freebsd.org/copyright/freebsd-license.html

# NOTE: Region does not have EC2 resource

from logging import warning
from pprint import PrettyPrinter

class Zone():
    """ Class to perform certain method to AWS Zone
    """

    def __init__(self, **kwargs):
        """ initial the object """
        self.session = kwargs.get('session', {})
        self.cmd_cfg = kwargs.get('cmd_cfg', {})

    def do_cmd(self):
        """ main command handler """
        if self.cmd_cfg['command'] == 'describe':
            self.describe()
            self.available_zones()

    def describe(self):
        """ get the available zone information """
        zones_info = self._describe_zone(session=self.session)
        output = PrettyPrinter(indent=2, width=41, compact=False)
        print('Total zones: {}'.format(len(zones_info['AvailabilityZones'])))
        for k in zones_info['AvailabilityZones']:
            print('\n⚬ Zone Id {}'.format(k['ZoneId']))
            output.pprint(k)

    def describe_zone(self, **kwargs):
        """ get the given zones information """
        zone = kwargs.get('zone', {})
        zones_info = self._describe_zone(session=self.session)
        for i in zones_info['AvailabilityZones']:
            if i['ZoneName'] == zone:
                return i
            if zone in i['ZoneId']:
                return i
        return None

    def available_zones(self):
        """ get the given zones information """
        zones_info = self._describe_zone(session=self.session)
        return len(zones_info['AvailabilityZones'])

    @classmethod
    def _describe_zone(cls, **kwargs):
        """ get the regions information """
        cls.session = kwargs.get('session', {})
        try:
            cls.zone_session = cls.session.get_client_session(service='ec2')
            cls.zone_info = cls.zone_session.describe_availability_zones()
            return cls.zone_info
        except Exception as err:
            warning('Unable to get regions information: {}'.format(err))
