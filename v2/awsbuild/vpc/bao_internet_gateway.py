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

class AwsInternetGateway():
    """ Class to perform certain method to AWS internet gateway
    """

    def __init__(self, **kwargs):
        """ initial the object """
        self.internet_gateway_id = None
        self.internet_gateway = None
        self.aws_conn = kwargs.get('aws_conn', {})
        self.ec2_client = self.aws_conn['ec2_client']
        self.ec2_resource = self.aws_conn['ec2_resource']
        self.vpc_id = kwargs.get('vpc_id', {})
        self.tag = kwargs.get('tag', {})
        # DANGER WILL ROBINSON : we using wildcard as filter!
        #self.tag_filter = '*' + str(self.tag) + '*'
        self.tag_filter = str(self.tag)
        self.search_filter = [{'Name' : 'tag:Name', 'Values' : [self.tag_filter]}]

    def create_internet_gateway(self):
        """ create a internet gateway """
        try:
            self.internet_gateway = self.ec2_resource.create_internet_gateway()
        except Exception as err:
            critical('Unable to create the internet gateway, error {}'.format(err))
            return None
        spin_message(
            message='Waiting {} seconds for the internet gateway to become available.'.format(WAIT_TIMER),
            seconds=WAIT_TIMER
        )
        self.internet_gateway_id = self.internet_gateway.id
        set_tag(obj=self.internet_gateway, tag=self.tag)
        return self.internet_gateway_id

    def delete_internet_gateway(self):
        """ delete the internet gateway
        """
        try:
            self.internet_gateway.delete()
            return True
        except Exception as err:
            critical('Unable to delete the internet gateway, error {}'.format(err))
            return False

    def attach_internet_gateway(self):
        """ attach the internet gateway to the given vpc """
        try:
            self.internet_gateway.attach_to_vpc(
                VpcId=self.vpc_id
            )
            return True
        except Exception as err:
            critical('Unable to attach the internet gateway to vpc, error {}'.format(err))
            return False

    def detach_internet_gateway(self):
        """ detach the internet gateway from the given vpc """
        try:
            self.internet_gateway.detach_from_vpc(
                VpcId=self.vpc_id
            )
            return True
        except Exception as err:
            critical('Unable to detach the internet gateway, error {}'.format(err))
            return False

    def get_internet_gateway_info(self):
        """ get the internet gateway info """
        # we assume there is only 1 internat gateway with the set tag
        try:
            internet_gateway = self.ec2_client.describe_internet_gateways(
                Filters=self.search_filter
            )
            return internet_gateway
        except Exception as err:
            warning('Unable to get the internet gateway info, error {}'.format(err))
            return None

    def get_internet_gateways_id(self):
        """ get the internet gateway id """
        if self.internet_gateway_id:
            return self.internet_gateway_id
        internet_gateway = self.get_internet_gateway_info()
        if internet_gateway is None:
            return None
        for k in internet_gateway['InternetGateways']:
            if k['InternetGatewayId']:
                self.internet_gateway_id = k['InternetGatewayId']
            break
        return self.internet_gateway_id

    def set_internet_gateways_resource(self):
        """ set the internet gateway object """
        try:
            self.internet_gateway = self.ec2_resource.InternetGateway(self.internet_gateway_id)
            return True
        except Exception as err:
            critical('Unable to get the internet gateway resource with id {}, err {}'\
                     .format(self.internet_gateway_id, err))
            return False
