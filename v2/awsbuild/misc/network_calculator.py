# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8:noet:tabstop=4:softtabstop=4:shiftwidth=8:expandtab

""" python3 class """

# Copyright (c)  2010 - 2020, © Badassops LLC / Luc Suryo
# All rights reserved.
# BSD 3-Clause License : http://www.freebsd.org/copyright/freebsd-license.html

import sys
import ipaddress
from logging import critical, warning
from pprint import PrettyPrinter
import awsbuild.const as const

class NetworkCalc():
    """
        The class is use by the VPC and the Security class, is does a calculation based on the given CIDR.
        Hardcoded: there will be a F(ront) E(end) and a B(ack) E(end) in the VPC
        Further the minimal availabilty zone is 4, which bring that the CIDR minimal size is a modulo of 8
        NOTE the fact the availabilty zone can be anywhere between 3 (good) and 5 (bad), which will
        make it hard to devided, so hardcoded that there is always be 4 zones, as per AWS that over time
        there will be at least 4 zones.
    """

    def __init__(self, **kwargs):
        """ initial the object """
        self.min_cidr_v4 = const.MIN_CIDR_V4
        self.min_cidr_v6 = const.MIN_CIDR_V6
        self.network_v4 = kwargs.get('network_v4', {})
        self.cidr_v4 = kwargs.get('cidr_v4', {})
        self.network_v6 = kwargs.get('network_v6', {})
        self.cidr_v6 = kwargs.get('cidr_v6', {})
        self.ipv6 = kwargs.get('ipv6', False)
        if int(self.cidr_v4) > self.min_cidr_v4:
            critical('The CIDR v4 {} is too small, minimaal size is {}'.\
                format(self.cidr_v4, self.min_cidr_v4))
            sys.exit(1)
        if self.ipv6:
            if int(self.cidr_v6) > self.min_cidr_v6:
                critical('The CIDR v6 {} is too small, minimaal size is {}'.\
                    format(self.cidr_v6, self.min_cidr_v6))
                sys.exit(1)

    def describe(self):
        """ get the network info info """
        output = PrettyPrinter(indent=2, width=41, compact=False)
        print('\n⚬ IPv4 subnets')
        output.pprint(self.__get_subnets(network=self.network_v4, cidr=self.cidr_v4, ipv6=False))
        if self.ipv6:
            print('\n⚬ IPv6 subnets')
            output.pprint(self.__get_subnets(network=self.network_v6, cidr=self.cidr_v6, ipv6=True))

    def get_info(self):
        """ get the network info """
        network_info = {}
        network_info = self.__get_subnets(network=self.network_v4, cidr=self.cidr_v4, ipv6=False)
        if self.ipv6:
            network_info.update(self.__get_subnets(network=self.network_v6, cidr=self.cidr_v6, ipv6=True))
        return network_info

    @classmethod
    def __get_subnets(cls, **kwargs):
        """ get ipv4 or ipv6 subnets info """
        network = kwargs.get('network', {})
        cidr = kwargs.get('cidr', {})
        ipv6 = kwargs.get('ipv6', False)
        if not cidr.lstrip().startswith('/'):
            cidr = '/' + cidr
        network_cidr = network + cidr
        suffix = '_ipv4'
        if ipv6:
            suffix = '_ipv6'
        subnet_info = {}
        try:
            # devide to 2 equal size cidrs
            subnets = list(ipaddress.ip_network(network_cidr).subnets(prefixlen_diff=1))
            subnet_info['fe_subnet' + suffix] = str(subnets[0])
            subnet_info['be_subnet' + suffix] = str(subnets[1])
            # IPv4
            if not ipv6:
                cnt = 1
                for subnet in list(ipaddress.ip_network(str(subnets[0])).subnets(prefixlen_diff=2)):
                    subnet_info['fe_subnet' + suffix + '_' + str(cnt)] = str(subnet)
                    cnt += 1
                cnt = 1
                for subnet in list(ipaddress.ip_network(str(subnets[1])).subnets(prefixlen_diff=2)):
                    subnet_info['be_subnet' + suffix + '_' + str(cnt)] = str(subnet)
                    cnt += 1
            # IPv6
            else:
                # IPv6 must be /64! and we always getting a /56 from AWS
                subnets = list(ipaddress.ip_network(network_cidr).subnets(prefixlen_diff=8))
                # fe takes the first half 4 from the /64s : 0 -> 3
                cnt = 1
                for subnet in subnets[:4]:
                    subnet_info['fe_subnet' + suffix + '_' + str(cnt)] = str(subnet)
                    cnt += 1
                # be takes the second half 4 from the /64s : example 128 -> 131 if /56
                start = int(len(subnets)/2)
                end = start + 4
                cnt = 1
                for subnet in subnets[start:end]:
                    subnet_info['be_subnet' + suffix + '_' + str(cnt)] = str(subnet)
                    cnt += 1
            return subnet_info
        except Exception as err:
            print('Unable to get the subnets, wrong cidr and network values, error {}'.format(err))
            return None

def is_valid(**kwargs):
    """ The function check if the given ip address is valid and is a IPv4 or IPv6 """
    ip_address = kwargs.get('ip', {})
    try:
        ip_type = ipaddress.ip_network(ip_address, strict=True)
        return str(ip_type.version)
    except Exception as err:
        warning('Given IP address {} it invalid, Error {}'.format(ip_address, err))
        return None

def is_private(**kwargs):
    """ The function check if the given ip address is valid and is a IPv4 or IPv6 """
    ip_address = kwargs.get('ip', {})
    if is_valid(ip=ip_address) is not None:
        return ipaddress.ip_network(ip_address, strict=True).is_private
    return None
