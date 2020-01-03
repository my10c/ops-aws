#!/usr/bin/env python3
""" for testing the module awsbuild """

import sys
import logging
from logging import critical
from bao_config import AwsConfig
from bao_connector import AwsConnector
from bao_vpc import AwsVPC
#from bao_subnet import AwsSubnet
#from bao_target_group import AwsTargetGroup
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

    groups_data = config.settings['autoscale_group']
    for autoscale_group in groups_data:
        temp_tag_dict = {}
        tags_list = []
        group_data = groups_data[autoscale_group]
        # create tag list
        for tag in group_data['Tags']:
            # set the working dictonary and overwrite or skip as needd
            temp_tag_dict = {'Key': tag, 'Value': group_data['Tags'][tag], 'PropagateAtLaunch': True}
            # we leave hostid empty if set to none
            if tag == 'hostid' and group_data['Tags'][tag] == 'none':
                temp_tag_dict = {'Key': tag, 'Value': '', 'PropagateAtLaunch': True}
            tags_list.append(temp_tag_dict)
        try:
            autoscale_conn.create_auto_scaling_group(
                AutoScalingGroupName=autoscale_group,
                LaunchTemplate={
                    'LaunchTemplateName': group_data['LaunchTemplate']['LaunchTemplateName'],
                    'Version': group_data['LaunchTemplate']['Version']
                },
                MinSize=int(group_data['MinSize']),
                MaxSize=int(group_data['MaxSize']),
                DesiredCapacity=int(group_data['DesiredCapacity']),
                DefaultCooldown=int(group_data['DefaultCooldown']),
                AvailabilityZones=group_data['AvailabilityZones'],
                HealthCheckGracePeriod=group_data['HealthCheckGracePeriod'],
                VPCZoneIdentifier=','.join(group_data['VPCZoneIdentifier']),
                TerminationPolicies=[group_data['TerminationPolicies']],
                Tags=tags_list
            )
            print('Autoscale Group {} created'.format(autoscale_group))
        except Exception as err:
            critical('Unable to create launch group {}, error {}'.format(autoscale_group, err))
            sys.exit(0)


if __name__ == '__main__':
    main()
