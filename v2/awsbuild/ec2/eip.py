# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8:noet:tabstop=4:softtabstop=4:shiftwidth=8:expandtab

""" python3 class """

# Copyright (c)  2010 - 2020, © Badassops LLC / Luc Suryo
# All rights reserved.
# BSD 3-Clause License : http://www.freebsd.org/copyright/freebsd-license.html

from pprint import PrettyPrinter
from logging import critical, warning
import awsbuild.const as const
from awsbuild.misc.spinner import spin_message
from awsbuild.aws.tag import create_resource_id_tag as set_tag

class EIP():
    """ Class for the AWS EIP
    """

    def __init__(self, **kwargs):
        """ initial the object """
        self.cmd_cfg = kwargs.get('cmd_cfg', {})
        self.session = kwargs.get('session', {})
        self.tag = self.cmd_cfg['tag']

        # DANGER WILL ROBINSON : we using wildcard as filter!
        self.tag_filter = str('*' + self.tag + '*')
        self.filter = [{'Name' : 'tag:Name', 'Values' : [self.tag_filter]}]

    def do_cmd(self):
        """ main command handler """
        if self.cmd_cfg['command'] == 'describe':
            return self.describe()
        if self.cmd_cfg['command'] == 'create':
            return self.create()
        if self.cmd_cfg['command'] == 'modify':
            return self.modify()
        if self.cmd_cfg['command'] == 'destroy':
            return self.destroy()
        return False

    def create(self, **kwargs):
        """ create an eip  """
        tag = kwargs.get('tag', '')
        if not tag:
            tag = self.tag
        try:
            eip_session = self.session.get_client_session(service='ec2')
            eip_info = eip_session.allocate_address(
                Domain='vpc'
            )
            spin_message(
                message='Waiting {} seconds for the eip to become available.'.format(const.TIMER),
                seconds=const.TIMER
            )
            set_tag(session=eip_session, resource_id=eip_info['AllocationId'],\
                tag_name='Name', tag_value=tag)
            return eip_info['AllocationId']
        except Exception as err:
            warning('Unable to create an eip, error: {}'.format(err))
            return None

    def describe(self):
        """ get the eip(s) info """
        eip_info = self.__get_info(session=self.session,\
            Filters=self.filter)
        if len(eip_info['Addresses']) == 0:
            print('\n⚬ No eip found, filter {}'.format(self.filter))
            return
        output = PrettyPrinter(indent=2, width=41, compact=False)
        for info in eip_info['Addresses']:
            print('\n⚬ eip ID {}'.format(info['AllocationId']))
            output.pprint(info)

    def get_info(self):
        """ get the eip(s) info """
        eip_info = self.__get_info(session=self.session,\
            Filters=self.filter)
        if len(eip_info['Addresses']) == 0:
            return None
        return eip_info

    def modify(self, **kwargs):
        """ modify an eip """
        modify = kwargs.get('modify', {})
        eip = kwargs.get('eip', {})
        instance = kwargs.get('instance', {})
        try:
            eip_session = self.session.get_client_session(service='ec2')
            if modify == 'associate':
                eip_session.associate_address(
                    InstanceId=instance,
                    AllocationId=eip
                )
            if modify == 'disassociate':
                eip_session.disassociate_address(
                    AllocationId=eip
                )
            return True
        except Exception as err:
            critical('Unable to {} the eip, error {}'.format(modify, err))
            return False

    def destroy(self, **kwargs):
        """ destroy an eip """
        eip = kwargs.get('eip', {})
        try:
            eip_session = self.session.get_client_session(service='ec2')
            eip_session.release_address(
                AllocationId=eip
            )
            return True
        except Exception as err:
            warning('Unable to release the eip, error {}'.format(err))
            return False

    @classmethod
    def __get_info(cls, **kwargs):
        """ get info """
        cls.session = kwargs.get('session', {})
        cls.filters = kwargs.get('filters', {})
        try:
            cls.eip_session = cls.session.get_client_session(service='ec2')
            eip_info = cls.eip_session.describe_addresses(
                Filters=cls.filters
            )
            return eip_info
        except Exception as err:
            warning('Unable to get info eip, error: {}'.format(err))
            return None
