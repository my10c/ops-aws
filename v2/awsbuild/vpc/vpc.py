# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8:noet:tabstop=4:softtabstop=4:shiftwidth=8:expandtab

""" python3 class """

# Copyright (c)  2010 - 2020, © Badassops LLC / Luc Suryo
# All rights reserved.
# BSD 3-Clause License : http://www.freebsd.org/copyright/freebsd-license.html

from pprint import PrettyPrinter
from logging import critical, warning

class VPC():
    """ Class for the AWS VPC
    """

    def __init__(self, **kwargs):
        """ initial the object """
        self.vpc = None
        self.vpc_id = None
        self.cmd_cfg = kwargs.get('cmd_cfg', {})
        self.session = kwargs.get('session', {})
        self.tag = self.cmd_cfg['tag']

        # DANGER WILL ROBINSON : we using wildcard as filter!
        self.tag_filter = str('*' + self.tag + '*')
        self.filter = [{'Name' : 'tag:Name', 'Values' : [self.tag_filter]}]

    def do_cmd(self):
        """ main command handler """
        if self.cmd_cfg['command'] == 'describe':
            return self.describe()
        if self.cmd_cfg['command'] == 'create':
            return self.create()
        if self.cmd_cfg['command'] == 'modify':
            return self.modify()
        if self.cmd_cfg['command'] == 'destroy':
            return self.destroy()
        return False

    def create(self):
        """ create the vpc  """
        print('create TODO')

    def describe(self):
        """ get the vpc info """
        # we assume there is only 1 vpc with the set tag
        vpc_info = self.__get_info(session=self.session,\
            filters=self.filter)
        if len(vpc_info['Vpcs']) == 0:
            print('No VPC found with the given tag, please be more speciific')
            return False
        if len(vpc_info['Vpcs']) > 1:
            print('Found more then on VPC with the given tag, please be more speciific')
        output = PrettyPrinter(indent=2, width=41, compact=False)
        for info in vpc_info['Vpcs']:
            print('\n⚬ VPC ID {}'.format(info['VpcId']))
            output.pprint(info)
            return True

    def get_info(self):
        """ get the vpc info """
        # we assume there is only 1 vpc with the set tag
        vpc_info = self.__get_info(session=self.session,\
            filters=self.filter)
        if len(vpc_info['Vpcs']) == 0:
            return None
        if len(vpc_info['Vpcs']) > 1:
            return None
        return vpc_info

    def modify(self):
        """ create the vpc attribute  """
        print('create TODO')

    def get_cidr(self):
        """ get the vpc ipv4 and ipv6 cidr from the given vpc tag """
        vpc_info = self.__get_info(session=self.session,\
            filters=self.filter)
        if len(vpc_info['Vpcs']) != 1:
            print('Error, either not found or found more then one VPC with the given tag')
            print('Please be more speciific with the tag, cancelling!')
            return None
        vpc_cidr = {}
        for i in vpc_info['Vpcs']:
            if i['CidrBlockAssociationSet']:
                for k in i['CidrBlockAssociationSet']:
                    vpc_cidr['ipv4'] = k['CidrBlock']
            try:
                if i['Ipv6CidrBlockAssociationSet']:
                    for k in i['Ipv6CidrBlockAssociationSet']:
                        vpc_cidr['ipv6'] = k['Ipv6CidrBlock']
            except Exception:
                pass
        print('{}'.format(vpc_cidr))
        return vpc_cidr

    def destroy(self):
        """ destroy the vpc """
        print('destroy TODO')

    @classmethod
    def __get_info(cls, **kwargs):
        """ get vpc info """
        cls.session = kwargs.get('session', {})
        cls.filters = kwargs.get('filters', {})
        try:
            cls.vpc_session = cls.session.get_client_session(service='ec2')
            vpc_info = cls.vpc_session.describe_vpcs(
                Filters=cls.filters
            )
            return vpc_info
        except Exception as err:
            warning('Unable to get the vpc info, filter {}. error {}'.\
                format(cls.filters, err))
            return None
