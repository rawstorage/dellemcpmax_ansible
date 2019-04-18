#!/usr/bin/python
# Copyright (C) 2018 DellEMC
# Author(s): Paul Martin <paule.martin@dell.com>
# Author(s): Olivier Carminati <olivier.carminati@bpce-it.fr>
# Author(s): Julien Brusset <julien.brusset.prestataire@bpce-it.fr>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.dellemc import dellemc_pmax_argument_spec, pmaxapi

__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
author:
  - "Paul Martin (@rawstorage)"
  - "Olivier Carminati (@ocarm)"
  - "Julien Brusset (@jbrt)"
short_description: "Create and manage hosts, host groups on Dell 
EMC PowerMax or VMAX All Flash"
version_added: "2.8"
description:
  - "This module has been tested against UNI 9.0. Every effort has been made
  to verify the scripts run with valid input. These modules are a tech preview"
module: dellemc_pmax_createhost
options:
  array_id:
    description:
      - "Integer 12 Digit Serial Number of PowerMAX or VMAX array."
    required: true
  unispherehost:
    description:
      - "Fully Qualified Domain Name or IP address of Unisphere for PowerMax
      host."
    required: true
  universion:
    description:
      - "Integer, version of unipshere software  e.g. 90"
    required: true
  verifycert:
    description:
      - "Boolean, security check on ssl certificates"
    type: bool
    required: true
  user:
    description:
      - "Unisphere username"
  password:
    description:
      - "password for Unisphere user"
  host_id:
    description:
      - "32 Character string no special character permitted except for
      underscore"
  initiator_list:
    description:
      - "List of WWNs or iQN."
  host_type:
    description:
      - "string describing the OS type (default or hpux)"
  consistent_lun:
    description:
      - "boolean that indicate if the consistent_lun must be set"
  state:
    description:
      - "expected state of host at the end of task, present will create or 
      modify a host, absent will delete if the host exists and is not part 
      of a masking view"
   wwn_state:
    description:
      - "states whether or not the wwns in the list should be added or 
      removed from the host, present will try to add the wwn in the list, 
      absent will remove any of the specified wwn. Removal of last wwn will 
      not be possible if the host is part of a masking view"

requirements:
  - Ansible
  - "Unisphere for PowerMax version 9.0 or higher."
  - "VMAX All Flash, VMAX3, or PowerMax storage Array."
  - "PyU4V version 3.0.0.9 or higher using PIP python -m pip install PyU4V"
'''
EXAMPLES = '''
---
- name: "Create a New Host"
  connection: local
  hosts: localhost
  vars_files:
    - vars.yml
  tasks:
  - name: Create Host
    dellemc_pmax_host:
        unispherehost: "{{unispherehost}}"
        universion: "{{universion}}"
        verifycert: "{{verifycert}}"
        user: "{{user}}"
        password: "{{password}}"
        array_id: "{{array_id}}"
        initiator_list:
        - 10000000c98ffea2
        - 10000000c98ffeb3
        host_type: default
        consistent_lun: true
        host_id: "AnsibleHost1"
        state: present
        wwn_state: present
  - name: Add initiator Host
    dellemc_pmax_host:
        unispherehost: "{{unispherehost}}"
        universion: "{{universion}}"
        verifycert: "{{verifycert}}"
        user: "{{user}}"
        password: "{{password}}"
        array_id: "{{array_id}}"
        initiator_list:
        - 10000000c98ffec3
        - 10000000c98ffec4
        host_id: "AnsibleHost1"
        host_type: default
        consistent_lun: true
        state: present
        wwn_state: present
  - name: remove initiators from host
    dellemc_pmax_host:
        unispherehost: "{{unispherehost}}"
        universion: "{{universion}}"
        verifycert: "{{verifycert}}"
        user: "{{user}}"
        password: "{{password}}"
        array_id: "{{array_id}}"
        initiator_list:
        - 10000000c98ffea2
        - 10000000c98ffeb3
        host_id: "AnsibleHost1"
        host_type: default
        consistent_lun: true
        state: present
        wwn_state: absent
  - name: rename a host
    dellemc_pmax_host:
        unispherehost: "{{unispherehost}}"
        universion: "{{universion}}"
        verifycert: "{{verifycert}}"
        user: "{{user}}"
        password: "{{password}}"
        array_id: "{{array_id}}"
        host_id: "AnsibleHost1"
        new_host_id: "NewAnsibleHost1"
        host_type: default
        state: present
  - name: Delete Host
    dellemc_pmax_host:
        unispherehost: "{{unispherehost}}"
        universion: "{{universion}}"
        verifycert: "{{verifycert}}"
        user: "{{user}}"
        password: "{{password}}"
        array_id: "{{array_id}}"
        initiator_list:
        - 10000000c98ffea2
        - 10000000c98ffeb3
        host_id: "AnsibleHost1"
        host_type: default
        consistent_lun: true
        state: absent
        wwn_state: absent
'''
RETURN = r'''
    "ansible_facts": {
        "host_detail": {
            "message": "initiators added"
        }
    },
    "changed": true,
    "host_detail": {
        "consistent_lun": false,
        "disabled_flags": "",
        "enabled_flags": "",
        "hostId": "AnsibleHost1",
        "initiator": [
            "10000000c98ffea2",
            "10000000c98ffeb3",
            "10000000c98ffec3",
            "10000000c98ffec4"
        ],
        "num_of_host_groups": 0,
        "num_of_initiators": 4,
        "num_of_masking_views": 0,
        "num_of_powerpath_hosts": 0,
        "port_flags_override": false,
        "type": "Fibre"
    },
    "invocation": {
        "module_args": {
            "array_id": "000197600156",
            "host_id": "AnsibleHost1",
            "initiator_list": [
                "10000000c98ffea2",
                "10000000c98ffeb3"
            ],
            "password": "VALUE_SPECIFIED_IN_NO_LOG_PARAMETER",
            "state": "present",
            "unispherehost": "10.60.156.63",
            "universion": 90,
            "user": "VALUE_SPECIFIED_IN_NO_LOG_PARAMETER",
            "verifycert": false,
            "wwn_state": "present"
        }
    },
    "state": "info"
}
'''
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.dellemc import dellemc_pmax_argument_spec, pmaxapi

BASE_FLAGS = {'volume_set_addressing': {'enabled': False, 'override': False},
              'disable_q_reset_on_ua': {'enabled': False, 'override': False},
              'environ_set': {'enabled': False, 'override': False},
              'avoid_reset_broadcast': {'enabled': False, 'override': False},
              'openvms': {'enabled': False, 'override': False},
              'scsi_3': {'enabled': False, 'override': False},
              'spc2_protocol_version': {'enabled': False, 'override': False},
              'scsi_support1': {'enabled': False, 'override': False},
              'consistent_lun': False
              }


def flags_default():
    """
    Build Host Flags for the default host_type
    :return: (dict)
    """
    return BASE_FLAGS


def flags_hpux():
    """
    Build Host Flags for HPUX host_type
    :return: (dict)
    """
    flags = BASE_FLAGS.copy()
    flags['volume_set_addressing'] = {'enabled': True, 'override': True}
    flags['spc2_protocol_version'] = {'enabled': True, 'override': True}
    flags['openvms'] = {'enabled': False, 'override': True}
    return flags


HOST_FLAGS = {'default': flags_default(),
              'hpux': flags_hpux()}


class DellEmcHost(object):
    """
    Create, modify or delete an PowerMax host (Initiator Group)
    """

    def __init__(self):
        self._argument_spec = dellemc_pmax_argument_spec()
        self._argument_spec.update(
            dict(
                host_id=dict(type='str', required=True),
                new_host_id=dict(type='str', required=False, default=None),
                initiator_list=dict(type='list', required=False),
                state=dict(type='str', required=True,
                           choices=['present', 'absent']),
                wwn_state=dict(type='str', required=False,
                               choices=['present', 'absent']),
                host_type=dict(type='str', required=False, default
                ='default' ),
                consistent_lun=dict(type='bool', required=False, default=False)
            ))

        self._module = AnsibleModule(argument_spec=self._argument_spec)
        self._conn = pmaxapi(self._module)
        self._changed = False  # Will gives the final status of execution
        self._message = []  # Contains the returned messages to the user

        self._host_id = self._module.params['host_id']
        self._initiators = self._module.params['initiator_list']

        # Host flags initialization
        try:
            self._host_flags = HOST_FLAGS[self._module.params['host_type']]
            self._host_flags['consistent_lun'] = self._module.params[
                'consistent_lun']
        except KeyError:
            self._module.fail_json(msg="{} is not a valid or supported host "
                                       "type".format(
                self._module.params['host_flags']))

    def _add_initiators_in_host(self):
        """
        Adding initiators into an existing host
        :return: None
        """
        try:
            # Determine if we need to add WWN or not
            host = self._conn.provisioning.get_host(host_id=self._host_id)
            to_add = [w for w in self._initiators if
                      w not in host['initiator']]
            if to_add:
                self._conn.provisioning.modify_host(host_id=self._host_id,
                                                    add_init_list=to_add)
                self._changed = True
                self._message.append("Initiators {} added in {}".
                                     format(", ".join(to_add), self._host_id))

            else:
                self._message.append("Host already in the requested state")

        except Exception as error:
            self._module.fail_json(msg="Unable to add initiators, check "
                                       "the list and retry: {}".format(error))

    def _create_host(self):
        """
        Will create or modify an existing host
        :return: (None)
        """
        # First use-case: the host doesn't exists yet, we create it
        if self._host_id not in self._conn.provisioning.get_host_list():
            try:
                self._conn.provisioning.create_host(host_name=self._host_id,
                                                    initiator_list=self._initiators,
                                                    host_flags=self._host_flags)

                self._message.append("Host {} successfully "
                                     "created".format(self._host_id))
                self._changed = True

            except Exception as error:
                self._module.fail_json(msg="Unable to create host with the "
                                           "specified parameters, check "
                                           "hostname is unique and WWNs are "
                                           "not in use: {}".format(error))
        else:
            self._message.append("Host already exists")

    def _remove_initiators_from_host(self):
        """
        Removing initiators from an existing host
        :return: None
        """
        try:
            # Determine if we need to remove WWN or not
            host = self._conn.provisioning.get_host(host_id=self._host_id)
            to_del = [w for w in self._initiators if w in host['initiator']]
            if to_del:
                self._conn.provisioning.modify_host(host_id=self._host_id,
                                                    remove_init_list=to_del)
                self._changed = True
                self._message.append("Host initiators {} removed from {}".
                                     format(", ".join(to_del), self._host_id))
            else:
                self._message.append("Host already in the requested state")

        except Exception as error:
            self._module.fail_json(msg="Unable to remove initiators, please "
                                       "check the supplied list ({})".format(
                error))

    def _rename_host(self):
        """
        Renaming an existing host
        :return: None
        """
        try:
            if self._host_id not in self._conn.provisioning.get_host_list():
                self._module.fail_json(
                    msg="Host {} doesn't exists".format(self._host_id))

            self._conn.provisioning.modify_host(host_id=self._host_id,
                                                new_name=self._module.params[
                                                    'new_host_id'])
            self._changed = True
            # Updating host_id to be consistent with the next facts gathering
            self._host_id = self._module.params['new_host_id']
            self._message.append("Host renamed to {}".format(self._host_id))

        except Exception as error:
            self._module.fail_json(msg="Unable to rename host, please "
                                       "check the supplied list ({})".format(
                error))

    def _delete_host(self):
        """
        Deleting an existing host
        :return: (None)
        """
        # Check if Host Name already exists.
        if self._host_id in self._conn.provisioning.get_host_list():
            mvlist = self._conn.provisioning. \
                get_masking_views_by_host(initiatorgroup_name=self._host_id)

            if len(mvlist) < 1:
                self._conn.provisioning.delete_host(host_id=self._host_id)
                self._changed = True
                self._message.append("Host {} deleted".format(self._host_id))

            else:
                self._message.append("{} host is part of a Masking view".
                                     format(self._host_id))
        else:
            self._module.fail_json(
                msg="Specified Host {} does not exist".format(self._host_id))

    def apply_module(self):
        """
        Main method of this module
        :return: (dict) Status and facts
        """
        result = {}

        # User has requested to create or modify an host
        if self._module.params['state'] == 'present':
            # If we want to rename host, this operation will done in first
            # place and will be exclusive (because it's not make sense to
            # rename AND add or removes initiators)
            if self._module.params['new_host_id']:
                self._rename_host()

            else:
                self._create_host()
                if self._module.params['wwn_state'] == 'absent':
                    self._remove_initiators_from_host()
                elif self._module.params['wwn_state'] == 'present':
                    self._add_initiators_in_host()

            h_details = self._conn.provisioning.get_host(host_id=self._host_id)
            result = {'state': 'info', 'changed': self._changed,
                      'host_detail': h_details}

        # User has requested to delete an host
        elif self._module.params['state'] == 'absent':
            self._delete_host()
            result = {'state': 'info', 'changed': self._changed}

        facts = ({'message': self._message})
        self._module.exit_json(ansible_facts={'host_detail': facts}, **result)


def main():
    DellEmcHost().apply_module()


if __name__ == '__main__':
    main()