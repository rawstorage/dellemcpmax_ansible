#!/usr/bin/python
# Copyright (C) 2018 DellEMC
# Author(s): Paul Martin <paule.martin@dell.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

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
  - "PyU4V version 3.0.0.8 or higher using PIP python -m pip install PyU4V"
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
        state: present
        wwn_state: absent
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


class DellEmcHost(object):
    def __init__(self):
        self.argument_spec = dellemc_pmax_argument_spec()
        self.argument_spec.update(dict(
            host_id=dict(type='str', required=True),
            initiator_list=dict(type='list', required=True),
            state=dict(type='str', required=True,
                       choices=['present', 'absent']),
            wwn_state=dict(type='str', required=True,
                           choices=['present', 'absent'])
        )
        )
        self.module = AnsibleModule(argument_spec=self.argument_spec)

        self.conn = pmaxapi(self.module)

    def create_or_modify_host(self):
        changed = False
        hostlist = self.conn.provisioning.get_host_list()
        hostdetail = {}
        message = ""

        if self.module.params['host_id'] not in hostlist:
            try:
                self.conn.provisioning.create_host(
                    host_name=self.module.params['host_id'],
                    initiator_list=self.module.params['initiator_list'])
                message = "Host Sucessfully Created"
                changed = True
                hostdetail = self.conn.provisioning.get_host(
                    host_id=self.module.params['host_id'])
            except Exception:
                message = "unable to create host with the specified parameters, " \
                          "check hostname is unique and wwns are not in use"

        elif self.module.params['wwn_state'] == 'absent':
            try:
                self.conn.provisioning.modify_host(
                    host_id=self.module.params['host_id'],
                    remove_init_list=self.module.params['initiator_list'])
                changed = True
                message = "Host initiators removed"
                hostdetail = self.conn.provisioning.get_host(
                    host_id=self.module.params['host_id'])
            except Exception:
                message = "unable to remove initiators, please check the " \
                          "supplied list"

        elif self.module.params['wwn_state'] == 'present':
            try:
                self.conn.provisioning.modify_host(
                    host_id=self.module.params['host_id'],
                    add_init_list=self.module.params['initiator_list'])
                changed = True
                message = "initiators added"
                hostdetail = self.conn.provisioning.get_host(
                    host_id=self.module.params['host_id'])
            except Exception:
                message = "unable to add initiators, check the list and retry"

        facts = ({'message': message})
        result = {'state': 'info', 'changed': changed,
                  'host_detail': hostdetail}
        self.module.exit_json(ansible_facts={'host_detail': facts}, **result)

    def delete_host(self):
        changed = False
        # Compile a list of existing hosts.
        hostlist = self.conn.provisioning.get_host_list()
        # Check if Host Name already exists.
        if self.module.params['host_id'] in hostlist:
            mvlist = self.conn.provisioning.get_masking_views_by_host( \
                initiatorgroup_name=self.module.params['host_id'])
            if len(mvlist) < 1:
                self.conn.provisioning.delete_host(
                    host_id=self.module.params['host_id'])
                changed = True
                message = "Host Deleted"
            else:
                message = self.module.params[
                              'host_id'] + " host is part of a Masking " \
                                           "view"
        else:
            message = "Specified host does not exist"
        facts = ({'message': message})
        result = {'state': 'info', 'changed': changed}
        self.module.exit_json(ansible_facts={'host_detail': facts}, **result)

    def apply_module(self):
        if self.module.params['state'] == "present":
            self.create_or_modify_host()
        elif self.module.params['state'] == "absent":
            self.delete_host()


def main():
    d = DellEmcHost()
    d.apply_module()


if __name__ == '__main__':
    main()
