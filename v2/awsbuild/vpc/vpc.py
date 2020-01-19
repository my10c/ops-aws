# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8:noet:tabstop=4:softtabstop=4:shiftwidth=8:expandtab

""" python3 class """

# Copyright (c)  2010 - 2020, © Badassops LLC / Luc Suryo
# All rights reserved.
# BSD 3-Clause License : http://www.freebsd.org/copyright/freebsd-license.html

from pprint import PrettyPrinter
from logging import critical, warning
import awsbuild.const as const
from awsbuild.misc.spinner import spin_message
from awsbuild.aws.tag import create_resource_id_tag as set_tag

class VPC():
    """ class for the aws vpc
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
        cidr = self.cmd_cfg['settings']['vpc']['network'] + '/' + self.cmd_cfg['settings']['vpc']['cidr']
        ipv6 = self.cmd_cfg['settings']['vpc']['ipv6']
        print('{} {}'.format(cidr, ipv6))
        try:
            vpc_session = self.session.get_client_session(service='ec2')
            vpc_info = vpc_session.create_vpc(
                CidrBlock=cidr,
                AmazonProvidedIpv6CidrBlock=ipv6
            )
            spin_message(
                message='Waiting {} seconds for the vpc to become available.'.\
                    format(const.TIMER),
                seconds=const.TIMER
            )
            set_tag(session=vpc_session, resource_id=vpc_info.vpc.id,\
                tag_name='Name', tag_value=self.tag)
            return vpc_info.vpc.id
        except Exception as err:
            critical('Unable to create the vpc info, error {}'.\
                format(err))
            return None

    def describe(self):
        """ get the vpc info """
        # we assume there is only 1 vpc with the set tag
        vpc_info = self.__get_info(session=self.session,\
            filters=self.filter)
        if len(vpc_info['Vpcs']) == 0:
            print('No vpc found with the given tag, please be more speciific')
            return False
        if len(vpc_info['Vpcs']) > 1:
            print('Found more then one vpc with the given tag, please be more speciific')
        output = PrettyPrinter(indent=2, width=41, compact=False)
        for info in vpc_info['Vpcs']:
            print('\n⚬ VPC id {}'.format(info['VpcId']))
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

    def modify(self, **kwargs):
        """ modify the vpc attribute  """
        modify_value = kwargs.get('modify', False)
        vpc_id = kwargs.get('vpc_id', False)
        try:
            vpc_session = self.session.get_client_session(service='ec2')
            vpc_obj = vpc_session.Vpc(vpc_id)
            vpc_obj.modify_attribute(
                EnableDnsSupport={'Value': modify_value}
            )
            vpc_obj.modify_attribute(
                EnableDnsHostnames={'Value': modify_value}
            )
            return True
        except Exception as err:
            warning('Unable to set dns hostnames to {}, error {}'.\
                format(modify_value, err))
            return False

    def get_cidr(self):
        """ get the vpc ipv4 and ipv6 cidr from the given vpc tag """
        vpc_info = self.__get_info(session=self.session,\
            filters=self.filter)
        if len(vpc_info['Vpcs']) != 1:
            print('Error, either not found or found more then one vpc with the given tag')
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

    def destroy(self, **kwargs):
        """ destroy a vpc, it's requires that all component to be destroyed first:
            gateways (internet and nat), instances, route tables, subnets and security groups
            we need to delete/release the eip and volumes once the VPC has been destroyed
        """
        vpc_id = kwargs.get('vpc_id', False)
        try:
            vpc_session = self.session.get_client_session(service='ec2')
            vpc_obj = vpc_session.Vpc(vpc_id)
            vpc_obj.delete()
            return True
        except Exception as err:
            critical('Unable to destroy the vpc with is {}, error {}'.\
                format(vpc_id, err))
            return False

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
            warning('Unable to get the vpc info, filter {}, error {}'.\
                format(cls.filters, err))
            return None
