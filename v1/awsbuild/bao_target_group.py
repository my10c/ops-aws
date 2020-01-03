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
#* File           :    bao_target_group.py
#* Description    :    class to perform certain method to AWS ELBv2 target groups
#* Author         :    Luc Suryo <luc@badassops.com>
#* Version        :    0.2
#* Date           :    Feb 21, 2019
#*
#* History    :
#*     Date:          Author:        Info:
#*    Apr 1, 2019     LIS            First Release

from logging import critical

class AwsTargetGroup():
    """ Class to perform certain method to AWS security groups """

    def __init__(self, **kwargs):
        """ initial the object """
        self.aws_conn = kwargs.get('aws_conn', {})
        self.target_group = kwargs.get('target_group', {})
        self.vpc_id = kwargs.get('vpc_id', {})
        self.tag = kwargs.get('tag', {})
        self.elbv2_client = self.aws_conn['elbv2_client']

    def create(self):
        """ function to create the target groups """
        for target_group in self.target_group:
            target_name = target_group
            if 'suffix' in self.target_group[target_group]:
                target_name += self.target_group[target_group]['suffix']
            try:
                if self.target_group[target_group]['protocol'] == 'TCP':
                    _ = self.elbv2_client.create_target_group(
                        Name=target_name,
                        Protocol=self.target_group[target_group]['protocol'],
                        Port=self.target_group[target_group]['port'],
                        VpcId=self.vpc_id,
                        HealthCheckProtocol=self.target_group[target_group]['healthcheckprotocol'],
                        HealthCheckPort=self.target_group[target_group]['healthcheckport'],
                        HealthCheckEnabled=self.target_group[target_group]['healthcheckenabled'],
                        HealthCheckIntervalSeconds=self.target_group[target_group]['healthcheckintervalseconds'],
                        HealthyThresholdCount=self.target_group[target_group]['healthythresholdcount'],
                        UnhealthyThresholdCount=self.target_group[target_group]['unhealthythresholdcount'],
                        TargetType=self.target_group[target_group]['targettype']
                    )
                else:
                    _ = self.elbv2_client.create_target_group(
                        Name=target_name,
                        Protocol=self.target_group[target_group]['protocol'],
                        Port=self.target_group[target_group]['port'],
                        VpcId=self.vpc_id,
                        HealthCheckProtocol=self.target_group[target_group]['healthcheckprotocol'],
                        HealthCheckPort=self.target_group[target_group]['healthcheckport'],
                        HealthCheckEnabled=self.target_group[target_group]['healthcheckenabled'],
                        HealthCheckPath=self.target_group[target_group]['healthcheckpath'],
                        HealthCheckIntervalSeconds=self.target_group[target_group]['healthcheckintervalseconds'],
                        HealthCheckTimeoutSeconds=self.target_group[target_group]['healthchecktimeoutseconds'],
                        HealthyThresholdCount=self.target_group[target_group]['healthythresholdcount'],
                        UnhealthyThresholdCount=self.target_group[target_group]['unhealthythresholdcount'],
                        Matcher={'HttpCode': self.target_group[target_group]['matcher']['httpcode']},
                        TargetType=self.target_group[target_group]['targettype']
                    )
            except Exception as err:
                critical('Unable to create the target group {}, error {}'.format(target_name, err))
                return False
        return True

    def delete(self, **kwargs):
        """ function to delete all target groups """
        target_arn = kwargs.get('target_arn', {})
        target_name = kwargs.get('target_name', {})
        try:
            result = self.elbv2_client.delete_target_group(TargetGroupArn=target_arn)
        except Exception as err:
            critical('Unable to delete the target group {}, error {}'.format(target_name, err))
            return False
        return result['ResponseMetadata']['HTTPStatusCode']

    def get_target_groups(self, **kwargs):
        """ get current target groups of the VPC """
        named_key = kwargs.get('named_key', False)
        target_groups_info = {}
        try:
            target_groups = self.elbv2_client.describe_target_groups()
        except Exception as err:
            critical('Unable to get the target groups in vpc {}, error {}'.format(self.vpc_id, err))
            return None
        for target_group in target_groups['TargetGroups']:
            if target_group['VpcId'] == self.vpc_id:
                if named_key is True:
                    target_groups_info[target_group['TargetGroupName']] = target_group['TargetGroupArn']
                else:
                    target_groups_info[target_group['TargetGroupArn']] = target_group['TargetGroupName']
        return target_groups_info
