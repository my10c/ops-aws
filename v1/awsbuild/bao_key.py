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
#* File           :    bao_key.py
#* Description    :    class to perform certain method to AWS EC2 key pair
#* Author         :    Luc Suryo <luc@badassops.com>
#* Version        :    0.2
#* Date           :    Feb 21, 2019
#*
#* History    :
#*     Date:          Author:        Info:
#*    Jun 1, 2010     LIS            First Release
#*    Feb 21, 2019    LIS            refactored

# NOTE: Key Pair does not have EC2 resource

from logging import critical, warning

class AwsKey():
    """ Class to perform certain method to AWS EC2 key
    """

    def __init__(self, **kwargs):
        """ initial the object """
        self.aws_conn = kwargs.get('aws_conn', {})
        self.ec2_client = self.aws_conn['ec2_client']
        self.key_name = kwargs.get('key_name', {})
        self.key_value = kwargs.get('key_value', {})

    def add(self):
        """ add a key """
        try:
            key_info = self.ec2_client.import_key_pair(
                KeyName=self.key_name,
                PublicKeyMaterial=self.key_value
            )
            return key_info
        except Exception as err:
            critical('Unable to add key pair named {}. Error: {}'.format(self.key_name, err))
            return None

    def delete(self):
        """ delete a key """
        try:
            self.ec2_client.delete_key_pair(
                KeyName=self.key_name,
            )
            return True
        except Exception as err:
            critical('Unable to delete key pair named {}. Error: {}'.format(self.key_name, err))
            return False

    def replace(self):
        """ replace a key """
        # we ignore the delete, since we doing a replace and the key might not exist
        key_info = self.delete()
        key_info = self.add()
        if key_info is False:
            return None
        return key_info

    def get_key_info(self, **kwargs):
        """ get the given key information """
        key_name = kwargs.get('key_name', {})
        if key_name:
            search_filter = [{'Name' : 'key-name', 'Values' : [key_name]}]
        else:
            search_filter = [{'Name' : 'key-name', 'Values' : [self.key_name]}]
        try:
            key_info = self.ec2_client.describe_key_pairs(
                Filters=search_filter
            )
            return key_info
        except Exception as err:
            warning('Unable to get info of the key pair named {}. Error: {}'.format(self.key_name, err))
            return None
