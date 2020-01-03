# vim:fileencoding=utf-8:noet

""" python class """

# Copyright (c)  2010 - 2019, © Badassops LLC / Luc Suryo
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#*
#* File           :    bao_security_groups.py
#* Description    :    class to perform certain method to AWS security groups
#* Author         :    Luc Suryo <luc@badassops.com>
#* Version        :    0.3
#* Date           :    Mat 3, 2019
#*
#* History    :
#*     Date:          Author:        Info:
#*    Jun 1, 2010     LIS            First Release
#*    March 3, 2019   LIS            refactored
#*    Mat 3, 2019     LIS            adding modify (replace all current rules)

from logging import critical, warning
from bao_const import WAIT_SEC_GROUP
from bao_spinner import spin_message
from bao_network import ip_info
from bao_set_tag import set_tag

class AwsSecGroup():
    """ Class to perform certain method to AWS security groups """

    def __init__(self, **kwargs):
        """ initial the object """
        self.rule_value = {}
        self.dc_network = {}
        self.aws_conn = kwargs.get('aws_conn', {})
        self.cfgs = kwargs.get('cfgs', {})
        self.dc_cfg = kwargs.get('dc_cfg', {})
        self.vpc_id = kwargs.get('vpc_id', {})
        self.tag = kwargs.get('tag', {})
        self.ipv6 = kwargs.get('ipv6', False)
        self.ec2_resource = self.aws_conn['ec2_resource']
        self.aws_cfg = self.cfgs['aws_cfg']
        self.sec_cfg = self.cfgs['sec_cfg']
        # these are rquired to setup rules
        self.aws_account = self.aws_cfg['global']['account']
        # IPv4
        self.dc_network['net'] = self.dc_cfg['vpc_network']
        self.dc_network['fe'] = self.dc_cfg['vpc_fe']
        self.dc_network['be'] = self.dc_cfg['vpc_be']
        if self.ipv6 is True:
            # IPv6
            self.dc_network['net_v6'] = self.dc_cfg['vpc_network_v6']
            self.dc_network['fe_v6'] = self.dc_cfg['vpc_fe_v6']
            self.dc_network['be_v6'] = self.dc_cfg['vpc_be_v6']

    def create(self, **kwargs):
        """ function to setup security, groups and rules """
        modify = kwargs.get('modify', False)
        sec_groups_list = {}
        if modify is False:
            sec_groups_list = self._create_sec_groups()
        else:
            sec_groups_list = self.get()
        if not sec_groups_list:
            return None
        sec_groups = self.sec_cfg['security_groups']
        for sec_group in sec_groups:
            try:
                sec_group_conn = self.ec2_resource.SecurityGroup(sec_groups_list[sec_group])
                for rule_type in ['in_rules', 'out_rules']:
                    try:
                        self._add_rule(
                            sec_group_conn=sec_group_conn,
                            sec_group=sec_group,
                            rule_type=rule_type,
                            sec_groups_list=sec_groups_list
                        )
                        print('\t\t...')
                    except Exception:
                        print('\t\tSecurity group {} has error {}, error in yaml/typo/no-rule?'.\
                            format(sec_group, rule_type))
                        continue
            except Exception as err:
                critical('Unable to create a SecurityGroup connection, error {}'.format(err))
                continue
        return sec_groups_list

    def destroy(self, **kwargs):
        """ function to delete all security groups
            if modify is given and set to true then
            it will not delete tee security groups
        """
        delete_group = kwargs.get('delete_group', False)
        exclude_group = kwargs.get('exclude_group', [])
        sec_group_ids = self._get_current_security_group()
        if not sec_group_ids:
            return None
        for sec_id in sec_group_ids:
            try:
                sec_group_conn = self.ec2_resource.SecurityGroup(sec_id)
            except Exception as err:
                critical('Unable to create a SecurityGroup connection, error {}'.format(err))
            if sec_group_conn.group_name not in ('default') and sec_group_conn.group_name not in exclude_group:
                print('\t\t ... Deleting in-rule for group {}'.format(sec_group_conn.group_name))
                for in_rule in sec_group_conn.ip_permissions:
                    try:
                        sec_group_conn.revoke_ingress(IpPermissions=[in_rule])
                    except Exception as err:
                        warning('Unable to delete in-rule: {}, errror {}'.format(in_rule, err))
                print('\t\t ... Deleting out-rule for group {}'.format(sec_group_conn.group_name))
                for out_rule in sec_group_conn.ip_permissions_egress:
                    try:
                        sec_group_conn.revoke_egress(IpPermissions=[out_rule])
                    except Exception as err:
                        warning('Unable to delete out-rule: {}, error {}'.format(out_rule, err))
            else:
                print('\t\t ... *** no rules will be deleted for group {}'.format(sec_group_conn.group_name))
        if delete_group is True:
            return self._delete_current_security_groups()
        return True

    def modify(self, **kwargs):
        """ - if a new security group, then add to the 'new' list
            - if a security group no longer is both in the yaml and vpc,
                then add to the 'delete' list
            - if group exist in both the yaml and vpc,
                then add to the 'modify' list
            - remove all ingress and egress rules from 'modify' list
                 but exclude  the exclude_list
            - delete groups if delete_old was set to true (delete list)
            - create the new groups (new list)
            - add ingress and egress rules to groups in the 'new' and
                'modify' list
        """
        modify_group_list = []
        new_group_list = []
        delete_group_list = {}
        exclude_list= []
        vpc_id = kwargs.get('vpc_id', {})
        delete_old = kwargs.get('delete_old', False)
        if not vpc_id:
            vpc_id = self.vpc_id
        # current security groups
        sec_groups_names = self.get(vpc_id=vpc_id)
        # create the new, modify and delete lists
        for in_config in self.sec_cfg['security_groups']:
            if in_config not in sec_groups_names:
                print('New Security Group {} has been tagged to be created!'.format(in_config))
                new_group_list.append(in_config)
            if in_config in sec_groups_names:
                print('Modify Security Group {} has been tagged to be modified!'.format(in_config))
                modify_group_list.append(in_config)
        for curr_group in sec_groups_names:
            if curr_group not in self.sec_cfg and curr_group != 'default':
                print('Remove Security Group {} has been tagged to be removed is {}!'.\
                    format(curr_group, delete_old))
                if delete_old:
                    delete_group_list[curr_group] = sec_groups_names[curr_group]
                else:
                    exclude_list.append(curr_group)
        # destoy all ingress and egress rules
        if self.destroy(delete_group=False, exclude_group=exclude_list):
            spin_message(
                message='Waiting {} seconds for the rules to be deleted.'.format(WAIT_SEC_GROUP),
                seconds=WAIT_SEC_GROUP
            )
        # create the new group
        for new_group in new_group_list:
            self._create_sec_group(sec_group=new_group, description=self.sec_cfg[new_group]['description'])
        # delete the group now there are empty and delete was requested
        if delete_old:
            for delete_group in delete_group_list:
                self._delete_security_group(sec_id=delete_group_list[delete_group])
        # add all rules back to the groups
        spin_message(
            message='Waiting {} seconds for the new security group to become available.'.format(WAIT_SEC_GROUP),
            seconds=WAIT_SEC_GROUP
        )
        return self.create(modify=True)

    def get(self, **kwargs):
        """ get current security groups of the VPC
            if vpc_id was given then use the given vpc
        """
        sec_groups_names = {}
        vpc_id = kwargs.get('vpc_id', {})
        if not vpc_id:
            vpc_id = self.vpc_id
        try:
            vpc_conn = self.ec2_resource.Vpc(vpc_id)
        except Exception as err:
            critical('Unable to create a connection to the vpc {}, error {}'.format(vpc_id, err))
            return None
        for sec_group in vpc_conn.security_groups.all():
            sec_groups_names[sec_group.group_name] = sec_group.id
        return sec_groups_names

    def get_rules(self, **kwargs):
        """ get the ingress and egress rule of the given security group  """
        sec_group = kwargs.get('sec_group', {})
        vpc_id = kwargs.get('vpc_id', {})
        if not sec_group:
            print('Missing security group name, aborting')
            return None
        if not vpc_id:
            vpc_id = self.vpc_id
        rules = {}
        sec_groups_list = self.get(vpc_id=vpc_id)
        if sec_groups_list is None:
            return None
        try:
            sec_group_conn = self.ec2_resource.SecurityGroup(sec_groups_list[sec_group])
            rules['ingress'] = sec_group_conn.ip_permissions
            rules['egress'] = sec_group_conn.ip_permissions_egress
            return rules
        except Exception as err:
            critical('Unable to create a connection to the security group {}, error {}'.format(sec_group, err))
            return None

    def _add_all_cidr_rule(self, func=None, ip_type=4):
        """ add an allow ALL rule with a CIDR as destination
            the function returns None so we so we return True is there
            was no error, since this should be an indication all OK
        """
        if self.rule_value['protocol'] == 'TCP' or self.rule_value['protocol'] == 'UDP':
            all_port_start = 0
            all_port_end = 65535
        else:
            all_port_start = -1
            all_port_end = -1
        if ip_type == 4:
            ip_permissions = [{
                'FromPort' : all_port_start,
                'ToPort' : all_port_end,
                'IpProtocol' : self.rule_value['protocol'],
                'IpRanges': [{
                    'CidrIp': self.rule_value['cidrip'],
                }],
            }]
        else:
            ip_permissions = [{
                'FromPort' : all_port_start,
                'ToPort' : all_port_end,
                'IpProtocol' : self.rule_value['protocol'],
                'Ipv6Ranges': [{
                    'CidrIpv6': self.rule_value['cidrip'],
                }],
            }]
        try:
            func(IpPermissions=ip_permissions)
        except Exception as err:
            critical('Unable to add rule, error {}'.format(err))
            return False
        return True

    def _add_all_group_rule(self, func=None, **kwargs):
        """ add an allow ALL rule with a security group as destination
            the function returns None so we so we return True is there
            was no error, since this should be an indication all OK
        """
        ip_permissions = [{
            'IpProtocol' : self.rule_value['protocol'],
            'UserIdGroupPairs': [{
                'GroupId': kwargs.get('group_id'),
                'UserId': self.aws_account,
            }],
        }]
        try:
            func(IpPermissions=ip_permissions)
        except Exception as err:
            critical('Unable to add rule, error {}'.format(err))
            return False
        return True

    def _add_range_cidr_rule(self, func=None, ip_type=4):
        """ add an allow based on port and protocal rule with a CIDR as destination
            the function returns None so we so we return True is there
            was no error, since this should be an indication all OK
        """
        if ip_type == 4:
            ip_permissions = [{
                'FromPort' : int(self.rule_value['start_port']),
                'ToPort' : int(self.rule_value['end_port']),
                'IpProtocol' : self.rule_value['protocol'],
                'IpRanges': [{
                    'CidrIp': self.rule_value['cidrip'],
                }],
            }]
        else:
            ip_permissions = [{
                'FromPort' : int(self.rule_value['start_port']),
                'ToPort' : int(self.rule_value['end_port']),
                'IpProtocol' : self.rule_value['protocol'],
                'Ipv6Ranges': [{
                    'CidrIpv6': self.rule_value['cidrip'],
                }],
            }]
        try:
            func(IpPermissions=ip_permissions)
        except Exception as err:
            critical('Unable to add rule, error {}'.format(err))
            return False
        return True

    def _add_range_group_rule(self, func=None, **kwargs):
        """ add an allow based on port and protocal rule with a security group as destination
            the function returns None so we so we return True is there
            was no error, since this should be an indication all OK
        """
        # set up the arguments to pass to the function
        ip_permissions = [{
            'FromPort' : int(self.rule_value['start_port']),
            'ToPort' : int(self.rule_value['end_port']),
            'IpProtocol' : self.rule_value['protocol'],
            'UserIdGroupPairs': [{
                'GroupId': kwargs.get('group_id'),
                'UserId': self.aws_account
            }],
        }]
        try:
            func(IpPermissions=ip_permissions)
        except Exception as err:
            critical('Unable to add rule, error {}'.format(err))
            return None
        return True

    def _set_rule_values(self, rule=None):
        """ setup the rules values, lowercase """
        values = rule.split()
        # Initialize the rule values, need to be initialized each pass
        self.rule_value['protocol'] = values[0].lower()
        self.rule_value['start_port'] = values[1].lower()
        self.rule_value['end_port'] = values[2].lower()
        self.rule_value['cidrip'] = values[3].lower()
        self.rule_value['all_port'] = False
        self.rule_value['use_group'] = False
        cidrip = values[3].lower()

        # Set if ALL port is requested, initialize to false
        if self.rule_value['start_port'] == 'all' or self.rule_value['end_port'] == 'all':
            self.rule_value['all_port'] = True

        # Set if ALL protocol is requested
        if self.rule_value['protocol'] == 'all':
            self.rule_value['protocol'] = '-1'

        # CIDR is defined as a network in the VPC or subnet
        # IPv4
        if cidrip == 'vpc_net':
            self.rule_value['cidrip'] = self.dc_network['net']
        if cidrip == 'vpc_fe':
            self.rule_value['cidrip'] = self.dc_network['fe']
        if cidrip == 'vpc_be':
            self.rule_value['cidrip'] = self.dc_network['be']
        if '/' in cidrip:
            self.rule_value['cidrip'] = cidrip
        if self.ipv6 is True:
            # IPv6
            if cidrip == 'vpc_net_v6':
                self.rule_value['cidrip'] = self.dc_network['net_v6']
            if cidrip == 'vpc_fe_v6':
                self.rule_value['cidrip'] = self.dc_network['fe_v6']
            if cidrip == 'vpc_be_v6':
                self.rule_value['cidrip'] = self.dc_network['be_v6']
        # CIDR is a group if this group exist as a key in
        # the security configuration
        if cidrip in self.sec_cfg:
            self.rule_value['use_group'] = True

    def _add_rule(self, **kwargs):
        """ main function to add a rule, it sets all the needed variable and then calls
            the correct sub rule function
        """
        sec_group_conn = kwargs.get('sec_group_conn', {})
        sec_group = kwargs.get('sec_group', {})
        rule_type = kwargs.get('rule_type', {})
        sec_groups_list = kwargs.get('sec_groups_list', {})
        # only add if there was a rule setup
        print('\t\t\tStart adding the {} rule to security group {}'.format(rule_type, sec_group))
        for rule in self.sec_cfg[sec_group][rule_type]:
            if 'none' not in rule and rule:
                self._set_rule_values(rule=rule)
                if self.rule_value['use_group'] is True:
                    group_id = sec_groups_list[self.rule_value['cidrip']]
                if rule_type == 'in_rules':
                    func = sec_group_conn.authorize_ingress
                if rule_type == 'out_rules':
                    func = sec_group_conn.authorize_egress
                # not using group
                if self.rule_value['use_group'] is False:
                    type_ip = int(ip_info(address=self.rule_value['cidrip']))
                    if self.rule_value['all_port'] is True:
                        add_result = self._add_all_cidr_rule(func=func, ip_type=type_ip)
                    else:
                        add_result = self._add_range_cidr_rule(func=func, ip_type=type_ip)
                # we use group
                else:
                    if self.rule_value['all_port'] is True:
                        add_result = self._add_all_group_rule(func=func, group_id=group_id)
                    else:
                        add_result = self._add_range_group_rule(func=func, group_id=group_id)
                if add_result is not True:
                    print('\t*** issue with {} rule for group {}\n\t-> {}'
                          .format(rule_type, sec_group, self.rule_value))

    def _create_sec_groups(self):
        """ create the security groups and make sure to remove the default egress rule
            by default there is no igress rule
        """
        sec_groups = {}
        # create all security groups and make sure the default egress rule is removed
        for sec_group in self.sec_cfg['security_groups']:
            # if there is no description then create on based on the security group name
            try:
                description = self.sec_cfg[sec_group]['description']
            except Exception:
                description = sec_group
            print('\t\tCreating security group {}'.format(sec_group))
            try:
                sec_group_resource = self.ec2_resource.create_security_group(
                    GroupName=sec_group,
                    Description=description,
                    VpcId=self.vpc_id
                )
            except Exception as err:
                critical('Unable to create security group {}, error {}'.format(sec_group, err))
                return None
            spin_message(
                message='Waiting {} seconds for the new security group to become available.'.format(WAIT_SEC_GROUP),
                seconds=WAIT_SEC_GROUP
            )
            # remove the default outbound rule, hardcoded by AWS
            if sec_group_resource:
                sec_groups[sec_group] = sec_group_resource.group_id
                try:
                    sec_group_resource.revoke_egress(
                        IpPermissions=[{
                            'IpProtocol' :'-1',
                            'IpRanges': [{
                                'CidrIp': '0.0.0.0/0'
                            }],
                        }],
                    )
                    sec_group_resource.revoke_egress(
                        IpPermissions=[{
                            'IpProtocol' :'-1',
                            'Ipv6Ranges': [{
                                'CidrIpv6': '::/0'
                            }],
                        }],
                    )
                except Exception as err:
                    warning('Unable to revoke_egress, default rule, error {}'.format(err))
            set_tag(obj=sec_group_resource, tag=sec_group)
        return sec_groups

    def _create_sec_group(self, **kwargs):
        """ create a  single security group """
        sec_group = kwargs.get('sec_group', {})
        description = kwargs.get('description', {})
        if not description:
            description = sec_group
        print('\t\tCreating security group {}'.format(sec_group))
        try:
            sec_group_resource = self.ec2_resource.create_security_group(
                GroupName=sec_group,
                Description=description,
                VpcId=self.vpc_id
            )
            set_tag(obj=sec_group_resource, tag=sec_group)
            return True
        except Exception as err:
            critical('Unable to create security group {}, error {}'.format(sec_group, err))
            return False

    def _delete_current_security_groups(self):
        """ delete all security groups """
        state_ok = True
        sec_groups_ids = self._get_current_security_group()
        if not sec_groups_ids:
            return False
        for sec_id in sec_groups_ids:
            try:
                sec_group_conn = self.ec2_resource.SecurityGroup(sec_id)
            except Exception as err:
                critical('Unable to create a SecurityGroup connection, error {}'.format(err))
                state_ok = False
            if sec_group_conn.group_name != 'default':
                print('\t\tDeleting security group {}'.format(sec_group_conn.group_name))
                try:
                    sec_group_conn.delete()
                except Exception as err:
                    critical('Unable to delete security group {}, error {}'.format(sec_group_conn.group_name, err))
                    state_ok = False
        return state_ok

    def _delete_security_group(self, **kwargs):
        """ delete given security group """
        sec_id = kwargs.get('sec_id', {})
        try:
            sec_group_conn = self.ec2_resource.SecurityGroup(sec_id)
            sec_group_conn.delete()
            return True
        except Exception as err:
            critical('Unable to delete security group, error {}'.format(err))
            return False

    def _get_current_security_group(self):
        """ get current security groups of the VPC """
        sec_groups_ids = []
        try:
            vpc_conn = self.ec2_resource.Vpc(self.vpc_id)
        except Exception as err:
            critical('Unable to create a connection to the vpc {}, error {}'.format(self.vpc_id, err))
            return None
        for sec_group in vpc_conn.security_groups.all():
            sec_groups_ids.append(sec_group.id)
        return sec_groups_ids
