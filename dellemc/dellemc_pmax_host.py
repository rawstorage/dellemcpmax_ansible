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
requirements:
  - Ansible
  - "Unisphere for PowerMax version 9.0 or higher."
  - "VMAX All Flash, VMAX3, or PowerMax storage Array."
  - "PyU4V version 3.0.0.8 or higher using PIP python -m pip install PyU4V"
'''
EXAMPLES = '''
---
- name: "Create hosts and Clusters"
  connection: local
  hosts: localhost
  vars:
    array_id: 000197600156
    password: smc
    unispherehost: "192.168.1.1"
    universion: "90"
    user: smc
    verifycert: false

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
        action: create_host
  - name: Create Host2
    dellemc_pmax_host:
        unispherehost: "{{unispherehost}}"
        universion: "{{universion}}"
        verifycert: "{{verifycert}}"
        user: "{{user}}"
        password: "{{password}}"
        array_id: "{{array_id}}"
        initiator_list:
        - 10000000c98ffe4a
        - 10000000c98ff5b3
        host_id: "AnsibleHost2"
        action: create_host
        
  - name: "Create Hostgroup"
    dellemc_pmax_host:
        unispherehost: "{{unispherehost}}"
        universion: "{{universion}}"
        verifycert: "{{verifycert}}"
        user: "{{user}}"
        password: "{{password}}"
        array_id: "{{array_id}}"
        action: create_hostgroup
        host_list:
          - "AnsibleHost1"
          - "AnsibleHost2"
        hostgroup_id: "AnsibleCluster"

  - name: Delete Cluster
    dellemc_pmax_host:
        unispherehost: "{{unispherehost}}"
        universion: "{{universion}}"
        verifycert: "{{verifycert}}"
        user: "{{user}}"
        password: "{{password}}"
        array_id: "{{array_id}}"
        hostgroup_id: "AnsibleCluster"
        action: delete_hostgroup

  - name: Delete Host2
    dellemc_pmax_host:
        unispherehost: "{{unispherehost}}"
        universion: "{{universion}}"
        verifycert: "{{verifycert}}"
        user: "{{user}}"
        password: "{{password}}"
        array_id: "{{array_id}}"
        host_id: "AnsibleHost2"
        action: delete_host

  - name: Delete Host1
    dellemc_pmax_host:
        unispherehost: "{{unispherehost}}"
        universion: "{{universion}}"
        verifycert: "{{verifycert}}"
        user: "{{user}}"
        password: "{{password}}"
        array_id: "{{array_id}}"
        host_id: "AnsibleHost1"
        action: delete_host

'''
RETURN = r'''
'''
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.dellemc import dellemc_pmax_argument_spec, pmaxapi


def create_or_modify_host(apiconnection, module):
    changed = False
    # Create a New Host
    conn = apiconnection
    dellemc = conn.provisioning
    # Compile a list of existing hosts.
    hostlist = dellemc.get_host_list()
    # Check if initiators are already in use.
    message = ""
    # Check all initiators are valid for use in new host
    valid_initiator = True
    bad_initiators_list = []
    valid_initiator_list =[]
    host_initiators = dellemc.get_host(host_id=module.params['host_id'])[
        'initiator']

    if module.params['host_id'] not in hostlist:
        dellemc.create_host(host_name=module.params['host_id'],
                            initiator_list=module.params['initiator_list'])
        message = "Host Sucessfully Created"
        changed = True

    elif len(module.params['initiator_list']) < len(host_initiators):
        # if fewer initiators specified than are in the host already attempt
        #  to remove the excess.
        remove_init_list=[]
        for initiator in host_initiators:
            if initiator not in module.params['initiator_list']:
                remove_init_list.append(initiator)
        dellemc.modify_host(host_id=module.params['host_id'],
                            remove_init_list=remove_init_list)
        changed = True
        message = "initiators %s have been removed from host" % \
                  str(remove_init_list)

    elif len(module.params['initiator_list']) > len(host_initiators):
        add_init_list=[]
        for initiator in module.params['initiator_list']:
            if initiator not in host_initiators:
                add_init_list.append(initiator)
        dellemc.modify_host(host_id=module.params['host_id'],
                            add_init_list=add_init_list)
        changed = True
        message = "initiators added"

    else:
        message = str(valid_initiator_list)
    facts = ({'message': message})
    result = {'state': 'info', 'changed': changed}
    module.exit_json(ansible_facts={'host_detail': facts}, **result)


def delete_host(apiconnection, module):
    changed = False
    # Create a New Host
    conn = apiconnection
    dellemc = conn.provisioning
    # Compile a list of existing hosts.
    hostlist = dellemc.get_host_list()
    # Check if Host Name already exists.
    if module.params['host_id'] in hostlist:
        mvlist = dellemc.get_masking_views_by_host(\
                initiatorgroup_name=module.params['host_id'])
        if len(mvlist) < 1:
            dellemc.delete_host(host_id=module.params['host_id'])
            changed = True
            message = "Host Deleted"
        else:
            message = module.params['host_id'] + " host is part of a Masking " \
                                                "view"
    else:
        message = "Specified host does not exist"
    facts = ({'message': message})
    result = {'state': 'info', 'changed': changed}
    module.exit_json(ansible_facts={'host_detail': facts}, **result)


def main():
    argument_spec = dellemc_pmax_argument_spec()
    argument_spec.update(dict(
        host_id=dict(type='str', required=False),
        initiator_list=dict(type='list', required=False),
        state=dict(type='str', required=True, choices=['present', 'absent'])
    )
    )
    module = AnsibleModule(argument_spec=argument_spec)
    # Setup connection to API
    conn = pmaxapi(module)
    if module.params['state'] == "present":
        create_or_modify_host(apiconnection=conn, module=module)
    elif module.params['state'] == "absent":
        delete_host(apiconnection=conn, module=module)


if __name__ == '__main__':
    main()
