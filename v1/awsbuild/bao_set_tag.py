# vim:fileencoding=utf-8:noet

""" python method """

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
#* File           :    bao_set_tag.py
#* Description    :    functions to set tag
#* Author         :    Luc Suryo <luc@badassops.com>
#* Version        :    0.2
#* Date           :    Feb 21, 2019
#*
#* History    :
#*     Date:          Author:        Info:
#*    Jun 1, 2010     LIS            First Release
#*    Feb 28, 2019    LIS            refactored

# NOTE: requires an EC2 resource object

from logging import warning

def set_tag(**kwargs):
    """ set the tag to the given object """
    obj = kwargs.get('obj', {})
    tag = kwargs.get('tag', {})
    tag_name = kwargs.get('tag_name', 'Name')
    try:
        obj.create_tags(
            Tags=[{'Key': tag_name, 'Value': tag},]
        )
    except Exception as err:
        warning('Unable to set the {} tag Error: {}'.format(tag_name, err))

def set_tag_client(**kwargs):
    """ set the tag using the ec2.client """
    ec2_client = kwargs.get('ec2_client', {})
    resource_id = kwargs.get('resource_id', {})
    tag = kwargs.get('tag', {})
    tag_name = kwargs.get('tag_name', 'Name')
    try:
        ec2_client.create_tags(
            Resources=[resource_id],
            Tags=[{'Key': tag_name, 'Value': tag},]
        )
    except Exception as err:
        warning('Unable to set the {} tag Error: {}'.format(tag_name, err))
