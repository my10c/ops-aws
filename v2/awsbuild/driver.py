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
from awsbuild.vpc.vpc import VPC
from awsbuild.aws.region import Region
from awsbuild.misc.spinner import spin_message, dot_message

def main():
    """ the main method """
    # Working variable
    #sec_info = {}

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
    # name is optional
    parser.add_argument(
        '-name', '-n', action='store', dest='name', required=False,
        default='None', help='required for keypair for other optional'
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

#    if cmd_cfg['service'] == 'autoscale-group':
#        autoscale_group = AutoscaleGroup(cmd_cfg=cmd_cfg, session=session)
#        return autoscale_group.do_cmd()

#    if cmd_cfg['service'] == 'elbv2':
#        elbv2 = ELBv2(cmd_cfg=cmd_cfg, session=session)
#        return elbv2.do_cmd()

#    if cmd_cfg['service'] == 'instance':
#        instance = Instance(cmd_cfg=cmd_cfg, session=session)
#       return instancevpc.do_cmd()

#    if cmd_cfg['service'] == 'internet-gateway':
#        internet-gateway = InternetGateway(cmd_cfg=cmd_cfg, session=session)
#        return internet-gateway.do_cmd()

#    if cmd_cfg['service'] == 'keypair':
#        keypair = KeyPair(cmd_cfg=cmd_cfg, session=session)
#        return keypair.do_cmd()

#    if cmd_cfg['service'] == 'launch-template':
#        launch_template = LaunchTemplate(cmd_cfg=cmd_cfg, session=session)
#        return launch_template.do_cmd()

#    if cmd_cfg['service'] == 'nat-gateway':
#        nat_gateway = NATGateway(cmd_cfg=cmd_cfg, session=session)
#        return nat_gateway.do_cmd()

    if cmd_cfg['service'] == 'region':
        region = Region(cmd_cfg=cmd_cfg, session=session)
        return region.do_cmd()

#    if cmd_cfg['service'] == 'target-group':
#        target_group = TargetGroup(cmd_cfg=cmd_cfg, session=session)
#        return target_group.do_cmd()

#    if cmd_cfg['service'] == 'security-group':
#        security_group = SecurityGroup(cmd_cfg=cmd_cfg, session=session)
#        return security_group.do_cmd()

#    if cmd_cfg['service'] == 'subnet':
#        subnet = Subnet(cmd_cfg=cmd_cfg, session=session)
#        return subnet.do_cmd()

#    if cmd_cfg['service'] == 'target_group':
#        target_group = TargetGroup(cmd_cfg=cmd_cfg, session=session)
#        return target_group.do_cmd()

    if cmd_cfg['service'] == 'vpc':
        vpc = VPC(cmd_cfg=cmd_cfg, session=session)
        return vpc.do_cmd()

    return 0
