# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8:noet:tabstop=4:softtabstop=4:shiftwidth=8:expandtab

""" python3 class """

# Copyright (c)  2010 - 2020, © Badassops LLC / Luc Suryo
# All rights reserved.
# BSD 3-Clause License : http://www.freebsd.org/copyright/freebsd-license.html

# NOTE: Region does not have EC2 resource

from logging import warning
from pprint import PrettyPrinter

class Region():
    """ Class to perform certain method to AWS region
    """

    def __init__(self, **kwargs):
        """ initial the object """
        self.session = kwargs.get('session', {})
        self.cmd_cfg = kwargs.get('cmd_cfg', {})

    def do_cmd(self):
        """ main command handler """
        if self.cmd_cfg['command'] == 'describe':
            self.describe()

    def describe(self):
        """ get the available regions information """
        regions_info = self._describe_region(session=self.session)
        output = PrettyPrinter(indent=2, width=41, compact=False)
        for k in regions_info['Regions']:
            print('\n⚬')
            output.pprint(k)

    def describe_region(self, **kwargs):
        """ get the given regions information """
        region = kwargs.get('region', {})
        regions_info = self._describe_region(session=self.session)
        for i in regions_info['Regions']:
            if i['RegionName'] == region:
                return i
        return None

    @classmethod
    def _describe_region(cls, **kwargs):
        """ get the regions information """
        cls.session = kwargs.get('session', {})
        try:
            cls.region_session = cls.session.get_client_session(service='ec2')
            cls.region_info = cls.region_session.describe_regions()
            return cls.region_info
        except Exception as err:
            warning('Unable to get regions information: {}'.format(err))
