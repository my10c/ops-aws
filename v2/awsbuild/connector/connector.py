# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8:noet:tabstop=4:softtabstop=4:shiftwidth=8:expandtab

""" python3 class """

# Copyright (c)  2010 - 2020, © Badassops LLC / Luc Suryo
# All rights reserved.
# BSD 3-Clause License : http://www.freebsd.org/copyright/freebsd-license.html

import sys
from logging import critical
import boto3

class Connector():
    """ Class to create AWS session
    """

    def __init__(self, **kwargs):
        """ initial the object """
        aws = kwargs.get('aws', {})
        self.region = kwargs.get('region', {})
        self.credentials = {}
        self.credentials['aws_access_key_id'] = aws['aws_access_key_id']
        self.credentials['aws_secret_access_key'] = aws['aws_secret_access_key']
        self.credentials['aws_session_token'] = aws['aws_session_token']
        self.session = self._get_session(credentials=self.credentials, region=self.region)

    def get_resource_session(self, **kwargs):
        """ get an resource aws session """
        service = kwargs.get('service', {})
        return self.session.resource(service)

    def get_client_session(self, **kwargs):
        """ get an client aws session """
        service = kwargs.get('service', {})
        return self.session.client(service)

    def get_connector(self, **kwargs):
        """ get connector for given service """
        service = kwargs.get('service', {})
        try:
            connector = boto3.client(
                service_name=service,
                region_name=self.region,
                aws_access_key_id_id=self.credentials['aws_access_key_id'],
                aws_secret_access_key=self.credentials['aws_secret_access_key'],
                aws_session_token=self.credentials['aws_session_token']
            )
        except Exception as err:
            critical('Could not get an AWS connector for the service {}, error {}'.\
                format(service, err))
        if len(self.credentials['aws_session_token']) > 1:
            sts = connector.client('sts')
            try:
                sts.get_caller_identity()
            except Exception as err:
                critical('Could not get a STS AWS session, error {}'.format(err))
                sys.exit(1)
        return connector

    @classmethod
    def _get_session(cls, **kwargs):
        """ create a aws session with the given credentials and region """
        cls.credentials = kwargs.get('credentials', {})
        cls.region = kwargs.get('region', {})
        try:
            cls.session = boto3.Session(
                region_name=cls.region,
                aws_access_key_id=cls.credentials['aws_access_key_id'],
                aws_secret_access_key=cls.credentials['aws_secret_access_key'],
                aws_session_token=cls.credentials['aws_session_token']
            )
            # the only way to check if we realy got a session is to try to call
            # at least one resource or client call
            _ = cls.session.client('ec2').describe_availability_zones()
        except Exception as err:
            critical('Could not get an AWS session, error {}'.format(err))
            sys.exit(1)
        if len(cls.credentials['aws_session_token']) > 1:
            sts = cls.session.client('sts')
            try:
                sts.get_caller_identity()
            except Exception as err:
                critical('Could not get a STS AWS session, error {}'.format(err))
                sys.exit(1)
        return cls.session
