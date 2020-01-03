#!/usr/bin/env python3
""" for testing the module awsbuild """

import sys
import logging
from bao_config import AwsConfig
from bao_connector import AwsConnector
from bao_vpc import AwsVPC
from bao_target_group import AwsTargetGroup

def main():
    """ main """
    my_logfile = 'logs/awsbuild.log'
    my_region = 'us-east-1'
    my_vpc = 'vpc-xxx'
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
                       cfgfile='target_group.yaml',\
                       cfgkey='target_groups')
    conn = AwsConnector(credentials=config.settings['aws_cfg']['credentials'], region=my_region)
    aws_conn = conn.get_all_conn()
    if not aws_conn:
        print('error AwsConnector\n')
        sys.exit(-1)

    vpc_conn = AwsVPC(aws_conn=aws_conn, tag=my_tag)
    if not vpc_conn:
        print('error AwsVPC\n')
        sys.exit(-1)

    target_grp_conn = AwsTargetGroup(aws_conn=aws_conn, target_group=config.settings['target_groups'], \
        vpc_id=my_vpc, tag=my_tag \
    )
    if not target_grp_conn:
        print('error AwsTargetGroup\n')
        sys.exit(-1)

    target_groups = target_grp_conn.get_target_groups()
    for target_arn in target_groups:
        print('{}'.format(target_grp_conn.delete(target_arn=target_arn, target_name=target_groups[target_arn])))

if __name__ == '__main__':
    main()
