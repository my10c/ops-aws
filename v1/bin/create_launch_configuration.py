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
                       cfgfile='launch_configuration.yaml',\
                       cfgkey='autoscale')
    conn = AwsConnector(credentials=config.settings['aws_cfg']['credentials'], region=my_region)
    aws_conn = conn.get_all_conn()
    if not aws_conn:
        print('error AwsConnector\n')
        sys.exit(-1)

    autoscale_conn = aws_conn['autoscaling']
    if not autoscale_conn:
        print('error AwsConnector for autoscaling\n')
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

    autoscale_data = config.settings['autoscale']
    for template in autoscale_data:
        temp_tag_dict = {}
        tags_list = []
        sgs_list = []
        template_data = autoscale_data[template]
        # create tag list
        for tag in template_data['tags']:
            # set the working dictonary and overwrite or skip as needd
            temp_tag_dict = {'Key': tag, 'Value': template_data['tags'][tag]}
            # we leave hostid empty if set to none
            if tag == 'hostid' and template_data['tags'][tag] == 'none':
                temp_tag_dict = {'Key': tag, 'Value': ''}
            # we do not add role if set to none
            if tag == 'role' and template_data['tags'][tag] == 'none':
                continue
            tags_list.append(temp_tag_dict)
        # create security group list
        for sec_group in template_data['SecurityGroups']:
            sec_id = sec_name_dict[sec_group]
            sgs_list.append(sec_id)
        try:
            result = autoscale_conn.create_launch_configuration(
                LaunchConfigurationName=template,
                ImageId=template_data['ImageId'],
                KeyName=template_data['KeyName'],
                InstanceType=template_data['InstanceType'],
                SecurityGroups=sgs_list,
                InstanceMonitoring={'Enabled': template_data['InstanceMonitoring']},
                PlacementTenancy=template_data['PlacementTenancy'],
                BlockDeviceMappings=[{
                    'DeviceName': template_data['BlockDeviceMappings']['DeviceName'],
                    'Ebs': {
                        'VolumeSize' : template_data['BlockDeviceMappings']['VolumeSize'],
                        'DeleteOnTermination': template_data['BlockDeviceMappings']['DeleteOnTermination']
                    }
                }],
                AssociatePublicIpAddress=template_data['AssociatePublicIpAddress'],
                UserData=''.join(template_data['UserData'])
            )
            #autoscale_conn.create_or_update_tags(Tags=tags_list)
            print('{}'.format(result))
        except Exception as err:
            critical('Unable to create launch template {}, error {}'.format(template, err))
            sys.exit(0)

if __name__ == '__main__':
    main()
