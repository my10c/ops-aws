# vim:fileencoding=utf-8:noet

""" pyhon method """

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
#* File           :    bao_main.py
#* Description    :    the main function
#* Author         :    Luc Suryo <luc@badassops.com>
#* Version        :    0.2
#* Date           :    Feb 21, 2019
#*
#* History    :
#*     Date:          Author:        Info:
#*    Jun 1, 2010     LIS            First Release
#*    Feb 21, 2019    LIS            refactored

import os
import logging
from logging import critical
import argparse
from time import strftime

import bao_const
from bao_config import AwsConfig
from bao_validconfig  import validconfig
from bao_network import set_network_config
from bao_connector import AwsConnector

from bao_region import show_aws_regions
from bao_zone import AwsZones
from bao_key import AwsKey

from bao_create import BaoCreate
#from bao_destroy import destroy_vpc
#from bao_add import add_instances
#from bao_start import start_instances
#from bao_stop import stop_instances
#from bao_terminate import terminate_instances
#from bao_status import status_instances

from bao_signal_handler import install_int_handler

# Script info variable
__progname__ = os.path.basename(__file__)
__author__ = 'Luc Suryo'
__copyright__ = 'Copyright 2010 - ' + strftime('%Y') + ' © Badassops LLC / Luc Suryo'
__license__ = 'BSD, http://www.freebsd.org/copyright/freebsd-license.html'
__version__ = '0.2'
__email__ = '<luc@badassops.com>'
__github_url__ = 'https://github.com/my10c/ops-aws'
__info__ = '{} version {}\n{}\nLicense {}\n\nWritten by {} {}\nGithub {}' \
    .format(__progname__, __version__, __copyright__, __license__, __author__, __email__, __github_url__)
__usage_txt__ = '[-action=<action>] '          +\
                '[-cfgdir=<directory>] '       +\
                '[-config=<config file>] '     +\
                '[-tag=<tag name>] '           +\
                '[-region=<AWS region name>] ' +\
                '[-help] [-version]'
__description__ = 'script to create/destory a VPC ' +\
                  'and to stop/start/terminate/get status/add instances in the VPC'

def main():
    """ the main method """
    # Working variable
    #sec_info = {}

    # Install interrupt handler
    install_int_handler()

    # Process giving arguments
    parser = argparse.ArgumentParser(
        usage=__usage_txt__, description=__description__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        conflict_handler='resolve'
    )
    parser.add_argument('-version', action='version', version=__info__)
    parser.add_argument(
        '-config', action='store', dest='cfgfile', help=bao_const.CFG_FILES_HELP, default=bao_const.EC2_CFG_FILE
    )
    parser.add_argument(
        '-cfgdir', action='store', dest='cfgdir', help=bao_const.CFG_DIR_HELP, default=bao_const.CFG_DIR
    )
    parser.add_argument(
        '-action', action='store', dest='action', help=bao_const.ACTION_HELP, choices=bao_const.ACTION_CHOICE,
        required=True
    )
    parser.add_argument(
        '-region', action='store', dest='region', help=bao_const.REGION_HELP, default=None
    )
    parser.add_argument(
        '-tag', action='store', dest='tag', help=bao_const.TAG_HELP, default=None
    )
    parser.add_argument(
        '-log', action='store', dest='logfile', help=bao_const.LOG_FILES_HELP, default=bao_const.LOG_FILE
    )

    # get the given argument
    given_args = parser.parse_args()

    # set shortname for the option
    cfgfile = given_args.cfgfile
    cfgdir = given_args.cfgdir
    action = given_args.action
    region = given_args.region
    tag = given_args.tag
    if  given_args.logfile:
        logfile = given_args.logfile

    # setup logging
    log_formatter = logging.Formatter("%(asctime)s %(filename)s %(name)s %(levelname)s %(message)s")
    root_logger = logging.getLogger()
    file_handler = logging.FileHandler(logfile)
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)

    if action == 'explain':
        os.system('clear')
        print('{}'.format(bao_const.CONFIG_EXPLAINED))
        return 0

    # Need to handle args here since we have odd combination that is not available the parser
    if action == 'regions':
        region = bao_const.REGION
        tag = 'region'
    else:
        if region is None or tag is None:
            print('action {} requires region, given {} and tag, given {}'.format(action, region, tag))
            return 1

    print('--< AwsConfig >--')
    config = AwsConfig(cfgdir=cfgdir, cfgfile=cfgfile)

    print('--< netConfig >--')
    if region not in config.settings['dc_cfg']:
        critical('Error regions {} has no configuration.'.format(region))
        return 1
    net_config = set_network_config(dc_cfg=config.settings['dc_cfg'][region])
    if not net_config:
        return 1

    print('--< AwsConnectionManager >--')
    conn = AwsConnector(credentials=config.settings['aws_cfg']['credentials'], region=region)
    aws_conn = conn.get_all_conn()
    if not aws_conn:
        return 1

    print('--< AwsZones >--')
    zones = AwsZones(aws_conn=aws_conn)
    if not zones:
        return 1
    net_config['dc_zones_names'] = zones.get_zones_name()
    net_config['dc_zones_id'] = zones.get_zones_id()
    net_config['dc_zones'] = zones.get_zones_cnt()
    net_config.update(config.settings['dc_cfg'][region])

    print('--< validConfig >--')
    if validconfig(aws_confg=config.settings['aws_cfg'], net_config=net_config) is False:
        return 1
    # set keys values early
    key_name = config.settings['aws_cfg']['key']['keyname']
    key_value = config.settings['aws_cfg']['key']['pubkey']

    print('--< AwsRegion >--')
    current_regions = show_aws_regions(aws_conn=aws_conn, show=action)
    if region not in current_regions:
        print('Given region {} in invalid.'.format(region))
        print('Valid regions:  {}'.format(' - '.join(current_regions)))
        return 0

    time_started = strftime("%c")

#--------------------------------------------------------------------------------------#

    # add EC2 key
    if action == 'key':
        print('--< AwsKey >--')
        key = AwsKey(aws_conn=aws_conn, key_name=key_name, key_value=key_value)
        if not key:
            return 1
        if key.replace() is None:
            return 1

#--------------------------------------------------------------------------------------#

    # Building a new VPC
    if action == 'create':
        print('--< create >--')
        create_conn = BaoCreate(aws_conn=aws_conn, net_config=net_config, tag=tag, region=region)
        create_conn.create()

#--------------------------------------------------------------------------------------#

    # Destroy a VPC
    if action == 'destroy':
        print('--< destroy >--')
        print('todo: destroy_vpc(aws_conn=aws_conn, net_config=net_config, tag=tag, region=region)')

#--------------------------------------------------------------------------------------#

    # Start all instances in a VPC
    if action == 'start':
        print('--< start >--')
        print('todo: start_instances(aws_conn=aws_conn, net_config=net_config, tag=tag, region=region)')

#--------------------------------------------------------------------------------------#

    # Stop all instances in a VPC
    if action == 'stop':
        print('--< stop >--')
        print('todo: stop_instances(aws_conn=aws_conn, net_config=net_config, tag=tag, region=region)')

#--------------------------------------------------------------------------------------#

    # Show status all instances in a VPC
    if action == 'status':
        print('--< status >--')
        print('todo: status_instances(aws_conn=aws_conn, net_config=net_config, tag=tag, region=region)')

#--------------------------------------------------------------------------------------#

    # Terminate all instances in a VPC
    if action == 'terminate':
        print('--< terminate >--')
        print('todo: terminate_instances(aws_conn=aws_conn, net_config=net_config, tag=tag, region=region)')

#--------------------------------------------------------------------------------------#

    # Add instance in a VPC
    if action == 'add':
        print('--< add >--')
        print('todo: add_instances(aws_conn=aws_conn, net_config=net_config, tag=tag, region=region)')

#--------------------------------------------------------------------------------------#

    print('Process started:   {}'.format(time_started))
    print('Process completed: {}'.format(strftime("%c")))
    return 0
