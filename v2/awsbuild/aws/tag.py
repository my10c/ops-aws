# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8:noet:tabstop=4:softtabstop=4:shiftwidth=8:expandtab

""" python3 method """

# Copyright (c)  2010 - 2020, © Badassops LLC / Luc Suryo
# All rights reserved.
# BSD 3-Clause License : http://www.freebsd.org/copyright/freebsd-license.html

# NOTE: requires an EC2 resource object

from logging import warning

def set_tag(**kwargs):
    """ set the tag to the given object """
    obj = kwargs.get('obj', {})
    tag = kwargs.get('tag', {})
    tag_name = kwargs.get('tag_name', 'Name')
    try:
        obj.create_tags(
            Tags=[{'Key': tag_name, 'Value': tag},]
        )
    except Exception as err:
        warning('Unable to set the {} tag Error: {}'.format(tag_name, err))

def set_tag_client(**kwargs):
    """ set the tag using the ec2.client """
    ec2_client = kwargs.get('ec2_client', {})
    resource_id = kwargs.get('resource_id', {})
    tag = kwargs.get('tag', {})
    tag_name = kwargs.get('tag_name', 'Name')
    try:
        ec2_client.create_tags(
            Resources=[resource_id],
            Tags=[{'Key': tag_name, 'Value': tag},]
        )
    except Exception as err:
        warning('Unable to set the {} tag Error: {}'.format(tag_name, err))
