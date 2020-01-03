#!/usr/bin/env python3
""" for testing the module awsbuild """

import sys
import logging
from bao_config import AwsConfig
from bao_connector import AwsConnector
from bao_vpc import AwsVPC
from bao_network import set_network_config
from bao_security_groups import AwsSecGroup

def main():
    """ main """
    my_logfile = 'logs/awsbuild.log'
    my_region = 'us-east-1'
    #my_vpc = 'vpc-xxx'
    my_tag = 'momo-us-east-1'

    # setup logging
    log_formatter = logging.Formatter("%(asctime)s %(filename)s %(name)s %(levelname)s %(message)s")
    root_logger = logging.getLogger()
    file_handler = logging.FileHandler(my_logfile)
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)

    config = AwsConfig(cfgdir='configs',\
                       cfgfile='ec2.yaml')
    conn = AwsConnector(credentials=config.settings['aws_cfg']['credentials'], region=my_region)
    aws_conn = conn.get_all_conn()
    if not aws_conn:
        print('error AwsConnector\n')
        sys.exit(-1)

    vpc_conn = AwsVPC(aws_conn=aws_conn, tag=my_tag)
    if not vpc_conn:
        print('error AwsVPC\n')
        sys.exit(-1)

    vpc_id = vpc_conn.get_vpc_id()
    vpc_conn.set_vpc_resource(vpc_id=vpc_id)
    dc_ipv6 = config.settings['dc_cfg'][my_region]['dc_ipv6']
    networkv6, cidrv6 = vpc_conn.get_vpc_cidr(ip_type='v6', split_cidr=True)

    net_config = set_network_config(dc_cfg=config.settings['dc_cfg'][my_region])
    if not net_config:
        print('error set_network_config\n')
        sys.exit(-1)

    # set the network topoloy first (subnet size)
    net_config.update(config.settings['dc_cfg'][my_region])

    # add the config from the configuration file and the VPC ipv6 settings
    net_config.update(set_network_config(dc_cfg=net_config, \
            dc_cidr_v6=cidrv6, dc_network_v6=networkv6))

    sec_conn = AwsSecGroup(aws_conn=aws_conn, cfgs=config.get_settings(), \
            dc_cfg=net_config, vpc_id=vpc_id, ipv6=dc_ipv6 \
        )
    if not sec_conn:
        print('error\n')
        sys.exit(-1)
    print('sec -> {}\n'.format(sec_conn.create()))

if __name__ == '__main__':
    main()
