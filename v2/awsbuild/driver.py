# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8:noet:tabstop=4:softtabstop=4:shiftwidth=8:noexpandtab

""" pyhon3 method """

# Copyright (c)  2010 - 2020, © Badassops LLC / Luc Suryo
# All rights reserved.
# BSD 3-Clause License : http://www.freebsd.org/copyright/freebsd-license.html

#import os
import logging
#from logging import critical
import argparse

import awsbuild.const as const
from awsbuild.misc.signal_handler import install_int_handler
from awsbuild.misc.validator import Validator
from awsbuild.connector.connector import Connector
from awsbuild.ec2.autoscale_group import AutoscaleGroup
from awsbuild.ec2.elbv2 import ELBV2
from awsbuild.vpc.internet_gateway import InternetGateway
from awsbuild.ec2.instance  import Instance
from awsbuild.ec2.keypair import KeyPair
from awsbuild.ec2.launch_template import LaunchTemplate
from awsbuild.vpc.nat_gateway import NATGateway
from awsbuild.aws.region import Region
from awsbuild.vpc.route_table import RouteTable
from awsbuild.ec2.security_group import SecurityGroup
from awsbuild.vpc.subnet import Subnet
from awsbuild.ec2.target_group import TargetGroup
from awsbuild.vpc.vpc import VPC
from awsbuild.aws.zone import Zone
from awsbuild.misc.spinner import dot_message

SERVICE_TO_CALL_MAP = {
    'autoscale_group': AutoscaleGroup,
    'elbv2': ELBV2,
    'internet_gateway': InternetGateway,
    'instance': Instance,
    'keypair': KeyPair,
    'launch_template': LaunchTemplate,
    'nat_gateway': NATGateway,
    'region': Region,
    'route_table': RouteTable,
    'security_group': SecurityGroup,
    'subnet': Subnet,
    'target-group': TargetGroup,
    'vpc': VPC,
    'zone': Zone,
}

def main():
    """ the main method """
    # Install interrupt handler
    install_int_handler()

    # Process giving arguments
    parser = argparse.ArgumentParser(
        usage=const.__usage_txt__, description=const.__description__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        conflict_handler='resolve'
    )
    parser.add_argument('-version', '--version',\
	    action='version', version=const.__info__)
    for arg in const.__valid_args__:
        parser.add_argument(
            '-'+format(arg), '-'+format(arg[:1]),
            action='store', dest=arg, help=argparse.SUPPRESS, required=True
        )
    for arg in const.__optional_args__:
        parser.add_argument(
            '-'+format(arg), '-'+format(arg[:1]),
            action='store', dest=arg, required=False,
            default=const.__optional_args__[arg][0],
            help=const.__optional_args__[arg][1],
        )
    args = parser.parse_args()

    # setup logging
    log_formatter = logging.Formatter("%(asctime)s %(filename)s %(name)s %(levelname)s %(message)s")
    root_logger = logging.getLogger()
    file_handler = logging.FileHandler(const.LOCATION['log_file'])
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)

    # validate the given argument and the nessecary configuration files
    validator = Validator(given_arg=vars(args))
    _ = validator.is_valid()
    cmd_cfg = validator.get_valid()
    dot_message(message='All configuration and given argument validated', seconds=5)

    # create an AWS session connector
    session = Connector(aws=cmd_cfg['settings']['aws']['credentials'],\
        region=cmd_cfg['settings']['vpc']['region'])
    dot_message(message='AWS session created', seconds=5)

    #  create class and then call the common name do_cmd
    service_name = SERVICE_TO_CALL_MAP[cmd_cfg['service']]
    service_object = service_name(cmd_cfg=cmd_cfg, session=session)
    return service_object.do_cmd()
