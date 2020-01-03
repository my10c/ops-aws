# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8:noet:tabstop=4:softtabstop=4:shiftwidth=8:expandtab

""" python3 class """

# Copyright (c)  2010 - 2020, © Badassops LLC / Luc Suryo
# All rights reserved.
# BSD 3-Clause License : http://www.freebsd.org/copyright/freebsd-license.html

# NOTE: Key Pair does not have EC2 resource

from logging import critical, warning

class AwsKey():
    """ Class to perform certain method to AWS EC2 key
    """

    def __init__(self, **kwargs):
        """ initial the object """
        self.aws_conn = kwargs.get('aws_conn', {})
        self.ec2_client = self.aws_conn['ec2_client']
        self.key_name = kwargs.get('key_name', {})
        self.key_value = kwargs.get('key_value', {})

    def do_cmd(self):
        """ main command handler """
          if self.cmd_cfg['command'] == 'describe':
              vpc_ids, vpc_info = self.describe()
              if len(vpc_ids) == 0:
                  print('No VPC found with the given tag, please be more speciific')
                  return
              if len(vpc_ids) > 1:
                  print('Found more then on VPC with the given tag, please be more speciific!')
              output = PrettyPrinter(indent=2, width=41, compact=False)
              for info in vpc_info['Vpcs']:
                  print('\n⚬ VPC ID {}'.format(info['VpcId']))
                  output.pprint(info)

    def add(self):
        """ add a key """
        try:
            key_info = self.ec2_client.import_key_pair(
                KeyName=self.key_name,
                PublicKeyMaterial=self.key_value
            )
            return key_info
        except Exception as err:
            critical('Unable to add key pair named {}. Error: {}'.format(self.key_name, err))
            return None

    def delete(self):
        """ delete a key """
        try:
            self.ec2_client.delete_key_pair(
                KeyName=self.key_name,
            )
            return True
        except Exception as err:
            critical('Unable to delete key pair named {}. Error: {}'.format(self.key_name, err))
            return False

    def replace(self):
        """ replace a key """
        # we ignore the delete, since we doing a replace and the key might not exist
        key_info = self.delete()
        key_info = self.add()
        if key_info is False:
            return None
        return key_info

    def get_key_info(self, **kwargs):
        """ get the given key information """
        key_name = kwargs.get('key_name', {})
        if key_name:
            search_filter = [{'Name' : 'key-name', 'Values' : [key_name]}]
        else:
            search_filter = [{'Name' : 'key-name', 'Values' : [self.key_name]}]
        try:
            key_info = self.ec2_client.describe_key_pairs(
                Filters=search_filter
            )
            return key_info
        except Exception as err:
            warning('Unable to get info of the key pair named {}. Error: {}'.format(self.key_name, err))
            return None
