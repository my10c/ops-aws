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
                       cfgfile='launch_template.yaml',\
                       cfgkey='launch_template')
    conn = AwsConnector(credentials=config.settings['aws_cfg']['credentials'], region=my_region)
    if not conn:
        print('error AwsConnector\n')
        sys.exit(-1)

    clt_conn = conn.get_clt(service_name='ec2')
    if not clt_conn:
        print('error AwsConnector for clt_client\n')
        sys.exit(-1)

    templates_data = config.settings['launch_template']
    for template in templates_data:
        try:
            clt_conn.delete_launch_template(
                LaunchTemplateName=template
            )
            print('Launch template {} deleted.'.format(template))
        except Exception as err:
            critical('Unable to delete launch template {}, error {}'.format(template, err))

if __name__ == '__main__':
    main()
