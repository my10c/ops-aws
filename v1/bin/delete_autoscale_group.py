#!/usr/bin/env python3
""" for testing the module awsbuild """

import sys
import logging
from logging import critical
from bao_config import AwsConfig
from bao_connector import AwsConnector

def main():
    """ main """
    my_logfile = 'logs/awsbuild.log'
    my_region = 'us-east-1'
    #my_vpc = 'vpc-xxx'
    #my_tag = 'momo-us-east-1'

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
                       cfgfile='auto_scaling_group.yaml',\
                       cfgkey='autoscale_group')
    conn = AwsConnector(credentials=config.settings['aws_cfg']['credentials'], region=my_region)
    aws_conn = conn.get_all_conn()
    if not aws_conn:
        print('error AwsConnector\n')
        sys.exit(-1)

    autoscale_conn = aws_conn['autoscaling']
    if not autoscale_conn:
        print('error AwsConnector for autoscaling\n')
        sys.exit(-1)

    groups_data = config.settings['autoscale_group']
    for autoscale_group in groups_data:
        try:
            autoscale_conn.delete_auto_scaling_group(
                AutoScalingGroupName=autoscale_group,
                ForceDelete=True
            )
            print('Autoscale Group {} deleted'.format(autoscale_group))
        except Exception as err:
            critical('Unable to create launch group {}, error {}'.format(autoscale_group, err))

if __name__ == '__main__':
    main()
