# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8:noet:tabstop=4:softtabstop=4:shiftwidth=8:expandtab

""" python3 method """

# Copyright (c)  2010 - 2020, © Badassops LLC / Luc Suryo
# All rights reserved.
# BSD 3-Clause License : http://www.freebsd.org/copyright/freebsd-license.html

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
