# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8:noet:tabstop=4:softtabstop=4:shiftwidth=8:expandtab

""" python3 class """

# Copyright (c)  2010 - 2020, © Badassops LLC / Luc Suryo
# All rights reserved.
# BSD 3-Clause License : http://www.freebsd.org/copyright/freebsd-license.html

import sys
from logging import critical
from pathlib import Path
import yaml
import awsbuild.const as const

class Validator():
    """  make sure everyting is valid
    """

    def __init__(self, **kwargs):
        """ initial the object """
        given_args = kwargs.get('given_arg', {})
        self.configdir = given_args['configdir']
        self.region = given_args['region']
        self.service = given_args['service']
        self.command = given_args['command']
        self.tag = given_args['tag']
        self.name = given_args['name']
        self.valid = {}
        self.settings = {}
        # check given configuration directory
        self._valid_dir(fqpn=self.configdir)

    def get_valid(self):
        """ get the valid configuration
        """
        services = self._get_service_dependancy(service=self.service)
        region_cfg = self._valid_region(region=self.region,\
            fqpn=self.configdir + '/' + const.CFG_FILES['vpc'][0])
        for service in services:
            if const.CFG_FILES[service][0] != 'none':
                service_cfg = self.configdir + '/' +\
                    const.CFG_FILES[service][0]
                if service == 'vpc':
                    self.settings['vpc'] = region_cfg
                else:
                    self.settings[service] = self._valid_yaml(
                        fqpn=service_cfg)
        self.valid = {
            'region': self.region,
            'service': self.service,
            'command': self.command,
            'settings': self.settings,
            'tag': self.tag,
            'name': self.name
        }
        return self.valid

    def is_valid(self):
        """ validate arguments and configuration files
        """
        self._valid_service_command_name(service=self.service,\
            command=self.command, name=self.name)
        self._valid_region(region=self.region,\
            fqpn=self.configdir + '/' + const.CFG_FILES['vpc'][0])
        services = self._get_service_dependancy(service=self.service)
        # check service configuration is a valid yaml
        for service in services:
            if const.CFG_FILES[service][0] != 'none':
                self._valid_yaml(fqpn=self.configdir + '/' +\
                    const.CFG_FILES[service][0])
        return True

    @classmethod
    def _get_service_dependancy(cls, **kwargs):
        """ get all services required for the given service
        """
        cls.services = []
        cls.service = kwargs.get('service', {})
        cls.services.append(cls.service)
        for extra in const.CFG_FILES[cls.service][1:]:
            cls.services.append(extra)
        return cls.services

    @classmethod
    def _valid_region(cls, **kwargs):
        """ check service and command
        """
        cls.region = kwargs.get('region', {})
        cls.fqpn = kwargs.get('fqpn', {})
        regions_cfg = cls._valid_yaml(fqpn=cls.fqpn)
        # try full region name
        for k in regions_cfg:
            try:
                if k == cls.region:
                    regions_cfg[k]['region'] = k
                    return regions_cfg[k]
            except Exception:
                pass
        # now try zone name
        for k in regions_cfg:
            if regions_cfg[k]['zone'] == cls.region:
                regions_cfg[k]['region'] = k
                return regions_cfg[k]
        critical('Region {} is not configured or does not exist'.format(cls.region))
        sys.exit(1)

    @classmethod
    def _valid_service_command_name(cls, **kwargs):
        """ check service and command
        """
        cls.service = kwargs.get('service', {})
        cls.command = kwargs.get('command', {})
        cls.name = kwargs.get('name', {})
        # check service is supported
        if cls.service not in const.SERVICE_ACTIONS:
            critical('Given service {} is not supported'.format(cls.service))
            print('Valid services:')
            for k in const.SERVICE_ACTIONS:
                print('\t◦ {}'.format(k))
            sys.exit(1)
        # check the comand for service is supported
        if cls.command not in const.SERVICE_ACTIONS[cls.service]:
            critical('Given command {} is not supported'.format(cls.command))
            print('Valid command for the service {}'.format(cls.service))
            for k in const.SERVICE_ACTIONS[cls.service]:
                print('\t◦ {}'.format(k))
        # if name is required for the combination of service with command
        if cls.service in const.SERVICE_REQUIRE_NAME_WITH_COMMAND:
            if cls.command in const.SERVICE_REQUIRE_NAME_WITH_COMMAND[cls.service]:
                if cls.name == 'none':
                    critical('Given service {} requires the -name flag'.format(cls.service))
                    sys.exit(1)

    @classmethod
    def _valid_dir(cls, **kwargs):
        """ check is directory
        """
        cls.fqpn = kwargs.get('fqpn', {})
        if not Path(cls.fqpn).is_dir():
            critical('Directory {} errored: check if directory exist'.\
                format(cls.fqpn))
            sys.exit(1)

    @classmethod
    def _valid_file(cls, **kwargs):
        """ check is file
        """
        cls.fqpn = kwargs.get('fqpn', {})
        if not Path(cls.fqpn).is_file():
            critical('File {} errored: check if file exist'.\
                format(cls.fqpn))
            sys.exit(1)

    @classmethod
    def _valid_yaml(cls, **kwargs):
        """ make sure file in correct yaml file
        """
        cls.fqpn = kwargs.get('fqpn', {})
        cls._valid_file(fqpn=cls.fqpn)
        try:
            yaml_file = open(cls.fqpn, 'r')
            with yaml_file as ymlfile:
                return yaml.safe_load(ymlfile)
        except Exception as err:
            critical('Could not open the file or yaml format issue {}. Error: {}'.\
                format(cls.fqpn, err))
            sys.exit(1)
