# vim:fileencoding=utf-8:noet

""" python class """

# Copyright (c)  2010 - 2019, © Badassops LLC / Luc Suryo
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#*
#* File           :    bao_connector.py
#* Description    :    class to create the connectors to the various AWS service
#* Author         :    Luc Suryo <luc@badassops.com>
#* Version        :    0.3
#* Date           :    May 21, 2019
#*
#* History    :
#*     Date:          Author:        Info:
#*    Jun 1, 2010     LIS            First Release
#*    Feb 21, 2019    LIS            refactored
#*    May 21, 2019    LIS            adding autoscaling and generic client connector

from logging import critical
import sys
import boto3

class AwsConnector():
    """ Class to create the connectors to the various AWS service
    """

    def __init__(self, **kwargs):
        """ initial the object """
        self.conns = {}
        self.credentials = kwargs.get('credentials', {})
        self.region = kwargs.get('region', {})
        self.session = self._connect_aws(credentials=self.credentials, region=self.region)
        self.conns['session'] = self.session
        self.conns['ec2_resource'] = self.session.resource('ec2')
        self.conns['ec2_client'] = self.session.client('ec2')
        self.conns['r53_client'] = self.session.client('route53')
        self.conns['elbv2_client'] = self.session.client('elbv2')
        self.conns['autoscaling'] = self.session.client('autoscaling')

    def get_ec2_rsc(self):
        """ get the ec2 resource connector """
        return self.conns['ec2_resource']

    def get_ec2_clt(self):
        """ get the ec2 client connector """
        return self.conns['ec2_client']

    def get_r53_clt(self):
        """ get the route53 connector """
        return self.conns['r53_client']

    def get_elbv2_clt(self):
        """ get the elbv2 connector """
        return self.conns['elbv2_client']

    def get_autoscaling_clt(self):
        """ get the autoscaling connector """
        return self.conns['autoscaling']

    def get_clt(self, **kwargs):
        """ get the client connector """
        service_name = kwargs.get('service_name', {})
        region = kwargs.get('region', {})
        if not region:
           region = self.region
        try:
            return boto3.client(
                service_name=service_name,
                region_name=region,
                aws_access_key_id=self.credentials['aws_access_key_id'],
                aws_secret_access_key=self.credentials['aws_secret_access_key'],
                aws_session_token=self.credentials['aws_session_token']
            )
        except Exception as err:
            critical('Could not get a AWS client for the service {}, error {}'.format(service_name, err))

    def get_all_conn(self):
        """ get dict with all the connectors """
        return self.conns

    @classmethod
    def _connect_aws(cls, **kwargs):
        """ create a aws session with the given credentials and region """
        credentials = kwargs.get('credentials', {})
        region = kwargs.get('region', {})
        try:
            conn = boto3.session.Session(
                region_name=region,
                aws_access_key_id=credentials['aws_access_key_id'],
                aws_secret_access_key=credentials['aws_secret_access_key'],
                aws_session_token=credentials['aws_session_token']
            )
        except Exception as err:
            critical('Could not get a AWS session, error {}'.format(err))
            sys.exit(1)
        if len(credentials['aws_session_token']) > 1:
            sts = conn.client('sts')
            try:
                sts.get_caller_identity()
            except Exception as err:
                critical('Could not get a AWS session, error {}'.format(err))
                sys.exit(1)
        return conn
