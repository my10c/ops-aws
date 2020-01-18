# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8:noet:tabstop=4:softtabstop=4:shiftwidth=8:expandtab

""" python3 method """

# Copyright (c)  2010 - 2020, © Badassops LLC / Luc Suryo
# All rights reserved.
# BSD 3-Clause License : http://www.freebsd.org/copyright/freebsd-license.html

from logging import warning

def create_resource_tag(**kwargs):
    """ create tag via resource """
    resource = kwargs.get('resource', {})
    tag_name = kwargs.get('tag_name', {})
    tag_value = kwargs.get('tag_value', {})
    try:
        resource.create_tags(
            Tags=[{'Key': tag_name, 'Value': tag_value},]
        )
        return True
    except Exception as err:
        warning('Unable to set the {} tag, error: {}'.format(tag_name, err))
        return False

def create_resource_id_tag(**kwargs):
    """ create tag via resource id """
    session = kwargs.get('session', {})
    resource_id = kwargs.get('resource_id', {})
    tag_name = kwargs.get('tag_name', {})
    tag_value = kwargs.get('tag_value', {})
    try:
        tag_session = session.get_client_session(service='ec2')
        tag_session.create_tags(
            Resources=[resource_id],
            Tags=[{'Key': tag_name, 'Value': tag_value},]
        )
        return True
    except Exception as err:
        warning('Unable to set the {} tag, error: {}'.format(tag_name, err))
        return False
