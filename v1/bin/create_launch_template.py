#!/usr/bin/env python3
""" for testing the module awsbuild """

import sys
import logging
from logging import critical
from bao_config import AwsConfig
from bao_connector import AwsConnector
from bao_vpc import AwsVPC
from bao_security_groups import AwsSecGroup
from bao_network import set_network_config

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
                       cfgfile='launch_template.yaml',\
                       cfgkey='launch_template')
    conn = AwsConnector(credentials=config.settings['aws_cfg']['credentials'], region=my_region)
    aws_conn = conn.get_all_conn()
    if not aws_conn:
        print('error AwsConnector\n')
        sys.exit(-1)

    ec2_conn = aws_conn['ec2_client']
    if not ec2_conn:
        print('error AwsConnector for ec2_client\n')
        sys.exit(-1)

    vpc_conn = AwsVPC(aws_conn=aws_conn, tag=my_tag)
    if not vpc_conn:
        print('error AwsVPC\n')
        sys.exit(-1)

    #vpc_id = vpc_conn.get_vpc_id()
    vpc_conn.set_vpc_resource(vpc_id=my_vpc)

    net_config = set_network_config(dc_cfg=config.settings['dc_cfg'][my_region])
    if not net_config:
        print('error set_network_config\n')
        sys.exit(-1)

    sec_conn = AwsSecGroup(aws_conn=aws_conn, cfgs=config.get_settings(), \
        dc_cfg=net_config, vpc_id=my_vpc, ipv6=False\
    )
    if not sec_conn:
        print('error\n')
    sec_name_dict = sec_conn.get(vpc_id=my_vpc)

    templates_data = config.settings['launch_template']
    for template in templates_data:
        temp_tag_dict = {}
        tags_list = []
        sgs_list = []
        template_data = templates_data[template]
        # create tag list
        for tag in template_data['TagSpecifications']:
            # set the working dictonary and overwrite or skip as needd
            temp_tag_dict = {'Key': tag, 'Value': template_data['TagSpecifications'][tag]}
            # we leave hostid empty if set to none
            if tag == 'hostid' and template_data['TagSpecifications'][tag] == 'none':
                temp_tag_dict = {'Key': tag, 'Value': ''}
            # we do not add role if set to none
            if tag == 'role' and template_data['TagSpecifications'][tag] == 'none':
                continue
            tags_list.append(temp_tag_dict)
        # create security group list
        for sec_group in template_data['SecurityGroupIds']:
            sec_id = sec_name_dict[sec_group]
            sgs_list.append(sec_id)
        try:
            result = ec2_conn.create_launch_template(
                LaunchTemplateName=template,
                VersionDescription=template_data['VersionDescription'],
                LaunchTemplateData={
                    'IamInstanceProfile': {
                        'Arn': template_data['IamInstanceProfile']
                    },
                    'BlockDeviceMappings': [{
                        'DeviceName': template_data['BlockDeviceMappings']['DeviceName'],
                        'Ebs': {
                            'DeleteOnTermination': template_data['BlockDeviceMappings']['Ebs']['DeleteOnTermination'],
                            'VolumeSize': int(template_data['BlockDeviceMappings']['Ebs']['VolumeSize'])
                        }
                    }],
                    'ImageId': template_data['ImageId'],
                    'InstanceType': template_data['InstanceType'],
                    'KeyName': template_data['KeyName'],
                    'Monitoring': {
                        'Enabled': template_data['Monitoring'],
                    },
                    'Placement': {
                        'Tenancy': template_data['Placement']['Tenancy']
                    },
                    'InstanceInitiatedShutdownBehavior': template_data['InstanceInitiatedShutdownBehavior'],
                    'UserData': ''.join(template_data['UserData']),
                    'TagSpecifications': [
                        {
                            'ResourceType': 'instance',
                            'Tags':  tags_list
                        },
                        {
                            'ResourceType': 'volume',
                            'Tags':  tags_list
                        }
                    ],
                    'SecurityGroupIds': sgs_list
                }
            )
            print('Launch template {} created, result {}.'.format(template, result))
        except Exception as err:
            critical('Unable to create launch template {}, error {}'.format(template, err))
            sys.exit(0)

if __name__ == '__main__':
    main()
