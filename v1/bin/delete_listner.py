#!/usr/bin/env python3
""" for testing the module awsbuild """

import sys
import logging
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
                       cfgfile='lb.yaml',\
                       cfgkey='elbs')
    conn = AwsConnector(credentials=config.settings['aws_cfg']['credentials'], region=my_region)
    aws_conn = conn.get_all_conn()
    if not aws_conn:
        print('error AwsConnector\n')
        sys.exit(-1)

    elbv2_conn = aws_conn['elbv2_client']
    if not elbv2_conn:
        print('error AwsConnector for elbv2_client\n')
        sys.exit(-1)

    elbs = elbv2_conn.describe_load_balancers()
    for elb_info in elbs['LoadBalancers']:
        try:
            listners = elbv2_conn.describe_listeners(
                LoadBalancerArn=elb_info['LoadBalancerArn']
            )
            elbv2_conn.delete_listener(
                ListenerArn=listners['ListenerArn']
            )
            print('Listner deleted {}'.format(listners['ListenerArn']))
        except Exception as err:
            print('No listerner or unable to delete listnerm error {}'.format(err))

if __name__ == '__main__':
    main()
