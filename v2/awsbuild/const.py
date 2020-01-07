# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8:noet:tabstop=4:softtabstop=4:shiftwidth=8:expandtab

""" python3 constants """

# Copyright (c)  2010 - 2020, © Badassops LLC / Luc Suryo
# All rights reserved.
# BSD 3-Clause License : http://www.freebsd.org/copyright/freebsd-license.html

import os
from time import strftime

# share to all
#__progname__ = 'awsbuild'
__progname__ = os.path.basename(__file__)
__author__ = 'Luc Suryo'
__copyright__ = 'Copyright 2010 - ' + strftime('%Y') + ' © Badassops LLC / Luc Suryo'
__license__ = 'BSD, http://www.freebsd.org/copyright/freebsd-license.html'
__version__ = '0.3'
__email__ = '<luc@badassops.com>'
__github_url__ = 'https://github.com/my10c/ops-aws'
__info__ = '{} version {}\n{}\nLicense {}\n\nWritten by {} {}\nGithub {}' \
    .format(__progname__, __version__, __copyright__, __license__, __author__, __email__, __github_url__)
__description__ = 'Script to create, modify or destory an basic AWS service/infrastructure.'
__usage_txt__ = (
    '\t[-configdir=<directory>]\n '
    '\t[-tag=<tag name>]\n '
    '\t[-regions=<aws regions]\n '
    '\t[-service=<aws service name>]\n '
    '\t[-command=<service command>]\n '
    '\t[-name=<name>]\n '
    '\t[-help] [-version]'
)
__valid_args__ = [
    'configdir',
    'tag',
    'region',
    'service',
    'command'
]

__optional_args__ = {
    'name': ['', 'Required for the keypair service, other is optional']
}

# Defaults
TIMER = 15
LOCATION = {
    'config_dir': './config/',
    'log_file': '/tmp/awsbuild.log'
}
# What configuration is required by the service:  list
# first element is file name
# after this is the name of service it depends on
CFG_FILES = {
    'aws': ['aws.yaml'],
    'autoscale-group': ['autoscale_group.yaml', 'aws', 'vpc'],
    'elbv2': ['elbv2.yaml', 'aws', 'vpc'],
    'eip': ['none', 'vpc', 'aws'],
    'internet-gateway': ['none', 'vpc', 'aws'],
    'instances': ['instances.yaml', 'aws', 'vpc'],
    'keypair': ['keypair.yaml', 'aws', 'vpc'],
    'launch-template': ['launch_template.yaml', 'aws', 'vpc'],
    'nat-gateway': ['none', 'vpc', 'aws'],
    'region': ['none', 'vpc', 'aws'],
    'route-table': ['none', 'vpc', 'aws'],
    'security-group': ['security_group.yaml', 'aws', 'vpc'],
    'subnet': ['none', 'aws', 'vpc'],
    'target-group': ['target_group.yaml', 'aws', 'vpc'],
    'vpc': ['vpc.yaml', 'aws'],
    'zone': ['none', 'vpc', 'aws']
}
SERVICE_ACTIONS = {
    'autoscale-group': ['create', 'describe', 'modify', 'destroy'],
    'elbv2': ['create', 'describe', 'modify', 'destroy'],
    'eip': ['describe'],
    'internet-gateway': ['describe'],
    'instance': ['create', 'describe', 'start', 'stop', 'destroy'],
    'keypair': ['create', 'describe', 'destroy'],
    'launch-template': ['create', 'describe', 'destroy'],
    'nat-gateway': ['describe'],
    'region': ['describe'],
    'route-table': ['describe'],
    'security-group': ['create', 'describe', 'modify', 'destroy'],
    'subnet': ['describe'],
    'target-group': ['create', 'describe', 'modify', 'destroy'],
    'vpc': ['create', 'describe', 'destroy'],
    'zone': ['describe'],
}
SERVICE_REQUIRE_NAME_WITH_COMMAND = {
    'elbv2': ['create', 'destroy'],
    'keypair': ['create', 'modify', 'destroy'],
    'vpc': ['none']
}
