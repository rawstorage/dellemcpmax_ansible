#!/usr/bin/python
# coding: utf-8
# Author(s): Julien Brusset <julien.brusset.prestataire@bpce-it.fr>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
This module declare some custom filters for Ansible helping users to
validating/manipulating WWN addresses in various formats.
"""

import re
from ansible.errors import AnsibleError


class WWNError(Exception):
    """
    Generic Exception raised if the given string is not a good WWN
    """
    pass


class WWN(object):
    """
    Transform strings into WWN objects
    """

    def __init__(self, address):
        """
        Initialization
        :param address: (str) a string containing a WWN (ex: 1122334455667788)
        """
        if isinstance(address, WWN):
            self._address = address.wwn
        else:
            self._address = self._normalize(address)

    def __format__(self, format_spec):
        return self.__str__()

    @classmethod
    def _normalize(cls, address):
        """
        Normalize the given WWN into a lowercase with colons
        :param address:
        :return: (str) WWN normalized
        """
        _regexDot = re.compile("([0-9a-fA-F]{2}|:){15}")
        _regexNoDot = re.compile("([0-9a-fA-F]{16})")

        if len(address) == 16 or len(address) == 23:
            if _regexDot.match(address):
                cls._address = address
            elif _regexNoDot.match(address):
                cls._address = ':'.join(re.findall('..', address))
            else:
                raise WWNError(address)
        else:
            raise WWNError(address)
        return cls._address.lower()

    def __eq__(self, other):
        """
        Compare two WWNs
        :param other: (str) WWN to compare
        :return: (bool) True if WWN are identical else False
        """
        if isinstance(other, str):
            try:
                other = WWN(other)
            except WWNError:
                return False
        elif not isinstance(other, WWN):
            return False
        return self._address == other._address

    def __repr__(self):
        return self._address

    @property
    def wwn(self):
        """
        Returns the embedded WWN
        :return: (str) WWN string
        """
        return self._address


class FilterModule(object):
    """
    Ansible filters declaration
    """
    def filters(self):
        return {
            'wwn': self.wwn_filter,
            'wwn_nodots': self.wwn_nodots_filter,
            'WWN': self.WWN_filter,
            'WWN_nodots': self.WWN_nodots_filter
        }

    def wwn_filter(self, a_variable):
        """
        Returns WWN lowercase with colons like 11:22:33:44:55:66:aa:bb
        :param a_variable: (str) variable to transform
        :return: (str) transformed string
        """
        try:
            return WWN(a_variable).wwn
        except WWNError as error:
            raise AnsibleError(f'Malformed WWN {error}')

    def wwn_nodots_filter(self, a_variable):
        """
        Returns WWN lowercase without colons like 112233445566aabb
        :param a_variable: (str) variable to transform
        :return: (str) transformed string
        """
        try:
            return WWN(a_variable).wwn.replace(':', '')
        except WWNError as error:
            raise AnsibleError(f'Malformed WWN {error}')

    def WWN_filter(self, a_variable):
        """
        Returns WWN uppercase with colons like 11:22:33:44:55:66:AA:BB
        :param a_variable: (str) variable to transform
        :return: (str) transformed string
        """
        try:
            return WWN(a_variable).wwn.upper()
        except WWNError as error:
            raise AnsibleError(f'Malformed WWN {error}')

    def WWN_nodots_filter(self, a_variable):
        """
        Returns WWN uppercase without colons like 112233445566AABB
        :param a_variable: (str) variable to transform
        :return: (str) transformed string
        """
        try:
            return WWN(a_variable).wwn.upper().replace(':', '')
        except WWNError as error:
            raise AnsibleError(f'Malformed WWN {error}')

