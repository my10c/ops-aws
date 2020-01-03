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
    """ Class the object to perform certain method in a AWS VPC
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
            vpc_ids, vpc_info = self.describe()
            if len(vpc_ids) == 0:
                print('No VPC found with the given tag, please be more speciific')
                return
            if len(vpc_ids) > 1:
                print('Found more then on VPC with the given tag, please be more speciific!')
            output = PrettyPrinter(indent=2, width=41, compact=False)
            for info in vpc_info['Vpcs']:
                print('\n⚬ VPC ID {}'.format(info['VpcId']))
                output.pprint(info)

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
            return vpc_ids, vpc_info
        except Exception as err:
            warning('Unable to get the vpc info, error {}'.format(err))
            return None

###->     def create(self):
###->         """ create a VPC, check if we need to setup IPv6 """
###->         try:
###->             self.vpc = self.ec2_resource.create_vpc(
###->                 CidrBlock=self.cidr,
###->                 AmazonProvidedIpv6CidrBlock=self.ipv6
###->             )
###->         except Exception as err:
###->             critical('Unable to create the VPC. Error: {}'.format(err))
###->             return None
###->         spin_message(
###->             message='Waiting {} seconds for the VPC to become available.'.format(WAIT_TIMER),
###->             seconds=WAIT_TIMER
###->         )
###->         self.vpc_id = self.vpc.id
###->         set_tag(obj=self.vpc, tag=self.tag)
###->         self._set_dns_options()
###->         return self.vpc
###-> 
###->     def destroy(self):
###->         """ destroy a VPC, this requires that all component to be destroyed first:
###->             gateways (internet and nat), instances, route tables, subnets and security groups
###->             we need to delete/release the EIP and volumes once the VPC has been destroyed
###->          """
###->         try:
###->             self.vpc.delete()
###->             return True
###->         except Exception as err:
###->             critical('Unable to destroy VPCs info. Error: {}'.format(err))
###-> 

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

    def get_vpcid(self):
        """ get the vpc if from the given vpc tag """
        vpc_ids, _ = self.describe()
        if len(vpc_ids) != 1:
            print('Error, either not found or found more then one VPC with the given tag')
            print('Please be more speciific with the tag, cancelling!')
            return None
        return vpc_ids[0]

###-> 
###->     def get_main_route_table(self):
###->         """ return the main (default) route table of the vpc """
###->         main_route_table = []
###->         for route_table in list(self.vpc.route_tables.all()):
###->             for association in list(route_table.associations):
###->                 if association.main is True:
###->                     main_route_table.append(route_table)
###->         if len(main_route_table) != 1:
###->             critical('cannot get main route table! {}'.format(main_route_table))
###->             return None
###->         return main_route_table[0]
###-> 
###->     def set_vpc_resource(self, **kwargs):
###->         """ set the vpc object """
###->         vpc_id = kwargs.get('vpc_id', {})
###->         try:
###->             self.vpc = self.ec2_resource.Vpc(vpc_id)
###->             return True
###->         except Exception as err:
###->             critical('Unable to get the vpc resource with id {}, error {}'.format(self.vpc_id, err))
###->             return False
###-> 
###->     def  _set_dns_options(self):
###->         """ set the vpc dns options """
###->         # ignore if failes
###->         # we need to modify the DNS options one at the time!
###->         try:
###->             self.vpc.modify_attribute(
###->                 EnableDnsSupport={'Value': True}
###->             )
###->         except Exception as err:
###->             warning('Unable to set DNS support, error {}'.format(err))
###->         try:
###->             self.vpc.modify_attribute(
###->                 EnableDnsHostnames={'Value': True}
###->             )
###->         except Exception as err:
###->             warning('Unable to set DNS hostnames, error {}'.format(err))
