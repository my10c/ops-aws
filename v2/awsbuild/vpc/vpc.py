# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8:noet:tabstop=4:softtabstop=4:shiftwidth=8:expandtab

""" python3 class """

# Copyright (c)  2010 - 2020, © Badassops LLC / Luc Suryo
# All rights reserved.
# BSD 3-Clause License : http://www.freebsd.org/copyright/freebsd-license.html

from pprint import PrettyPrinter
from logging import critical, warning
#from bao_const import WAIT_TIMER
#from bao_spinner import spin_message
#from bao_set_tag import set_tag


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
        self.tag_filter = '*' + str(self.tag) + '*'
        self.tag_filter = str(self.tag)
        self.search_filter = [{'Name' : 'tag:Name', 'Values' : [self.tag_filter]}]

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

    def describe(self):
        """ get the vpc info """
        # we assume there is only 1 vpc with the set tag
        try:
            vpc_session = self.session.get_client_session(service='ec2')
            vpc_info = vpc_session.describe_vpcs(
                Filters=self.search_filter
            )
            vpc_ids = []
            for k in vpc_info['Vpcs']:
                if k['VpcId']:
                    vpc_ids.append(k['VpcId'])
        except Exception as err:
            warning('Unable to get the vpc info, error {}'.format(err))
            return False
        if len(vpc_ids) == 0:
            print('No VPC found with the given tag, please be more speciific')
            return False
        if len(vpc_ids) > 1:
            print('Found more then on VPC with the given tag, please be more speciific!')
        output = PrettyPrinter(indent=2, width=41, compact=False)
        for info in vpc_info['Vpcs']:
            print('\n⚬ VPC ID {}'.format(info['VpcId']))
            output.pprint(info)
            return True

    def get_cidr(self):
        """ get the vpc ipv4 and ipv6 cidr from the given vpc tag """
        vpc_ids, vpc_info = self.describe()
        if len(vpc_ids) != 1:
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

    def create(self):
        """ create the vpc  """
        print('create TODO')

    def modify(self):
        """ create the vpc attribute  """
        print('create TODO')

    def destroy(self):
        """ destroy the vpc """
        print('destroy TODO')

    def getid(self):
        """ get the vpc if from the given vpc tag """
        vpc_ids, _ = self.describe()
        if len(vpc_ids) != 1:
            print('Error, either not found or found more then one VPC with the given tag')
            print('Please be more speciific with the tag, cancelling!')
            return None
        return vpc_ids[0]
