# vim:fileencoding=utf-8:noet

""" python method """

# BSD 3-Clause License
#
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
#* File           :    bao_validconfig.py
#* Description    :    function to validate configuration
#* Author         :    Luc Suryo <luc@badassops.com>
#* Version        :    0.2
#* Date           :    Feb 21, 2019
#*
#* History    :
#*     Date:          Author:        Info:
#*    Jun 1, 2010     LIS            First Release
#*    Feb 21, 2019    LIS            refactored

from logging import critical

# hardcoded!
__required_aws_global_cfg__ = ['account']
__required_aws_credentials__ = ['aws_access_key_id', 'aws_secret_access_key']
__required_aws_key_cfg__ = ['keyname', 'pubkey']
__required_dc_cfg__ = [
    'dc_region', 'dc_endpoint', 'dc_isocode', 'dc_public_domain', 'dc_domain',
    'dc_network', 'dc_cidr', 'dc_bastion', 'dc_ami', 'dc_zones_names',
    'vpc_network', 'vpc_fe', 'vpc_be', 'vpc_fe_subnets', 'vpc_be_subnets'
]

def validconfig(aws_confg=None, net_config=None):
    """ method to make sure the required configuration key, value are set """
    errors = 0
    for k in __required_aws_global_cfg__:
        if k not in aws_confg['global']:
            critical('the global config is missing the key: {}'.format(k))
            errors += 1
    for k in __required_aws_credentials__:
        if k not in aws_confg['credentials']:
            critical('the credentials config is missing the key :{}'.format(k))
            errors += 1
    for k in __required_aws_key_cfg__:
        if k not in aws_confg['key']:
            critical('the key config is missing the key: {}'.format(k))
            errors += 1
    for k in __required_dc_cfg__:
        if k not in net_config:
            critical('dc_cfg config is missing the key: {}'.format(k))
            errors += 1
    if errors:
        return False
    return True
