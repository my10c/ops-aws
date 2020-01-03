# vim:fileencoding=utf-8:noet

""" python constants """

# BSD 3-Clause License
#
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
#* File           :    bao_const.py
#* Description    :    constants definition file
#* Author         :    Luc Suryo <luc@badassops.com>
#* Version        :    0.2
#* Date           :    Feb 21, 2019
#*
#* History    :
#*     Date:          Author:        Info:
#*    Jun 1, 2010     LIS            First Release
#*    Feb 21, 2019    LIS            refactored

# Defaults
WAIT_TIMER = 15
WAIT_SEC_GROUP = 5
WAIT_INSTANCE = 10
CFGS_FILES = ['aws.yaml', 'dc.yaml', 'sec.yaml']
CFG_DIR = '/Users/luc/projects/ops-aws/config/'
EC2_CFG_FILE = CFG_DIR + 'ec2.yaml'
ACTION_CHOICE = ['create', 'destroy', 'start', 'stop', 'status', 'add', 'terminate', 'regions', 'key', 'explain']
ACTION_NEED_CFG = ['add', 'terminate', 'regions']
LOG_FILE = '/Users/luc/projects/ops-aws/logs/awsbuild.log'
REGION = 'us-east-1'

# Help messages
CFG_DIR_HELP = 'directory where to find the configuration files; names are hardcoded, ' +\
               'these are files name {}, by default the files are under the directory {}'\
               .format(' - '.join(CFGS_FILES), CFG_DIR)
CFG_FILES_HELP = 'yaml file containt the instances information that need to be added or terminated, ' +\
                 'used by the actions \'add\' or \'terminate\', default to {}'.format(EC2_CFG_FILE)
ACTION_HELP = 'action to be preformed to the selected AWS region, use action \'regions\' to show availabe regions.'
REGION_HELP = 'the AWS region of the VPC'
TAG_HELP = 'the tag name of the VPC'
LOG_FILES_HELP = 'log file to be used, default to {} in current directory'.format(LOG_FILE)

CONFIG_EXPLAINED = \
  'entry in the yaml file use in the actions add or terminate\n\n' +\
  '{name}:                        name, use something that make sense such as webserver\n' +\
  '  count: {count}               how many instance need to be created\n' +\
  '  start_sequence: {id}         the sequence id for instance\'s tag, so if we set the tag_base to webserver\n' +\
  '                                 set start to and 2 were requested (count) then the instances will be tagged\n' +\
  '                                 webserver1 and webserver2\n' +\
  '  tag_base: {tag base}         tag base, example bastion, webserver\n' +\
  '  tag_prefix: {tag prefix}     prefix for tag, example prod- or dev-\n' +\
  '  tag_component: {tag type}    the component tag is used to group instances so its makes cost analytics easy,\n' +\
  '                                 example ops or db\n' +\
  '  tag_master: {tag master)     for future use, can be ommited\n' +\
  '  sec_groups:\n' +\
  '    - {sec group name}         security group(s) to assign to the instance, one group per line\n' +\
  '  type: {ec2 instance type}    ec2 instance type, example t2.small\n' +\
  '  public_ip: [True|False]      instance needs a public ip assigned, ignored if placement in be\n' +\
  '  static_ip: [True|False]      instance needs a static ip address (eip), ignored if placement in ib be\n' +\
  '  vpc_placement: {[fe|be]}     placement in vpc, fe == public and be == private\n' +\
  '  data_volume: {size in GB}    create and attach extra ebs volume of the given size\n' +\
  '\n\tvalue in {}, need to be  enclose with single quotes\n' +\
  '\tvalue in [], exacate as shown and select one, not enclose with single quotes\n'
