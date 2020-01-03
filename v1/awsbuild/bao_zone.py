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
#* File           :    bao_zone.py
#* Description    :    class to perform certain method to AWS zone
#* Author         :    Luc Suryo <luc@badassops.com>
#* Version        :    0.2
#* Date           :    Feb 21, 2019
#*
#* History    :
#*     Date:          Author:        Info:
#*    Jun 1, 2010     LIS            First Release
#*    Feb 21, 2019    LIS            refactored

# NOTE: Zone does not have EC2 resource

from logging import warning

class AwsZones():
    """ Class to perform certain method to AWS zones
    """

    def __init__(self, **kwargs):
        """ initial the object """
        self.zones_info = {}
        self.zones_name = []
        self.zones_id = []
        self.aws_conn = kwargs.get('aws_conn', {})
        self.ec2_client = self.aws_conn['ec2_client']
        self._get_zone_info()

    def get_zones_name(self):
        """ get the available zones id """
        for v in self.zones_info['AvailabilityZones']:
            self.zones_name.append(v['ZoneName'])
        return sorted(self.zones_name)

    def get_zones_id(self):
        """ get the available zones id """
        for v in self.zones_info['AvailabilityZones']:
            self.zones_id.append(v['ZoneId'])
        return sorted(self.zones_id)

    def get_zones_cnt(self):
        """ get the available zones count """
        return len(self.zones_info['AvailabilityZones'])

    def _get_zone_info(self):
        """ create a aws session with the given credentials """
        try:
            self.zones_info = self.ec2_client.describe_availability_zones()
        except Exception as err:
            warning('Could not get a AWS session: {}'.format(err))
