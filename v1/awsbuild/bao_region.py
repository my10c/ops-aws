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
#* File           :    bao_region.py
#* Description    :    class to perform certain method to AWS region
#* Author         :    Luc Suryo <luc@badassops.com>
#* Version        :    0.2
#* Date           :    Feb 21, 2019
#*
#* History    :
#*     Date:          Author:        Info:
#*    Jun 1, 2010     LIS            First Release
#*    Feb 21, 2019    LIS            refactored

# NOTE: Region does not have EC2 resource

import sys
from logging import warning

class AwsRegions():
    """ Class to perform certain method to AWS regions
    """

    def __init__(self, **kwargs):
        """ initial the object """
        self.region_info = {}
        self.regions_name = []
        self.regions_endpoint = []
        self.aws_conn = kwargs.get('aws_conn', {})
        self.ec2_client = self.aws_conn['ec2_client']
        self._get_region_info()

    def get_regions_name(self):
        """ get the available regions id """
        for k in self.region_info['Regions']:
            self.regions_name.append(k['RegionName'])
        return sorted(self.regions_name)

    def get_region_endpoint(self):
        """ get the available regions endpoint """
        for k in self.region_info['Regions']:
            self.regions_endpoint.append(k['Endpoint'])
        return sorted(self.regions_endpoint)

    def get_regions_cnt(self):
        """ get the available zones count """
        return len(self.region_info['Regions'])

    def _get_region_info(self):
        """ get the regions information """
        try:
            self.region_info = self.ec2_client.describe_regions()
        except Exception as err:
            warning('Unable to get regions information: {}'.format(err))

def show_aws_regions(aws_conn=None, show=None):
    """ get regions name using an aws sesssion since it does not required to provide a region name """
    regions_name = aws_conn['session'].get_available_regions(service_name='ec2')
    if show == 'regions':
        print('Regions names: {}'.format(' - '.join(regions_name)))
        print('Total regions: {}'.format(len(regions_name)))
        sys.exit(0)
    return regions_name
