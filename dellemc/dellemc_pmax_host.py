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
- name: "Create a New Host"
  connection: local
  hosts: localhost
  vars:
    array_id: 000197600156
    password: smc
    sgname: Ansible_SG
    unispherehost: "192.168.1.123"
    universion: "90"
    user: smc
    verifycert: false

  tasks:
  - name: Create Host2
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
        host_id: "AnsibleHost2"
        action: create_host
'''
RETURN = r'''
'''
def create_host(apiconnection, module):
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
    for initiator in module.params['initiator_list']:
        if dellemc.is_initiator_in_host(initiator=initiator):
           valid_initiator = False
    # Check if Host Name already exists.
    if module.params['host_id'] not in hostlist and valid_initiator:
        dellemc.create_host(host_name=module.params['host_id'],
                            initiator_list=module.params['initiator_list'])
        message = "Host Sucessfully Created"
        changed = True
    else:
        message = "A host with the specified name already exists, " \
                  "or initiator wwwn is in another host"
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

def create_hostgroup(apiconnection, module):
    changed = False
    # Create a New Host
    conn = apiconnection
    dellemc = conn.provisioning
    # Check for each host in the host list that it exists, otherwise fail
    # module.
    configuredhostlist = dellemc.get_host_list()
    hostgrouplist = dellemc.get_hostgroup_list()
    host_exists = True
    message = ""
    if module.params['hostgroup_id'] not in hostgrouplist:
        for host in module.params["host_list"]:
            if host not in configuredhostlist:
                host_exists = False
                message = host + " does not exist, check input paramters"
    if module.params['hostgroup_id'] not in hostgrouplist and host_exists:
        dellemc.create_hostgroup(hostgroup_id=module.params['hostgroup_id'],
                                 host_list=module.params["host_list"])
        changed = True
        message = module.params['hostgroup_id']+" Cluster Created"
    else:
        message = "Cluster Name Already Exists"

    facts = ({'message': message})
    result = {'state': 'info', 'changed': changed}
    module.exit_json(ansible_facts={'host_detail': facts}, **result)

def delete_hostgroup(apiconnection, module):
    changed = False
    # Create a New Host
    conn = apiconnection
    dellemc = conn.provisioning
    # Compile a list of existing hosts.
    hostgrouplist = dellemc.get_hostgroup_list()
    # Check if Host Name already exists.
    if module.params['hostgroup_id'] in hostgrouplist:
        mvlist = dellemc.get_masking_views_by_host(\
                initiatorgroup_name=module.params['host_id'])
        if len(mvlist) < 1:
            dellemc.delete_hostgroup(hostgroup_id=module.params['hostgroup_id'])
            changed = True
            message = "HostGroup Deleted"
        else:
            message = module.params['host_id'] + " host is part of a Masking " \
                                                "view"
    else:
        message = "Specified hostgroup does not exist"
    facts = ({'message': message})
    result = {'state': 'info', 'changed': changed}
    module.exit_json(ansible_facts={'host_detail': facts}, **result)

def modify_hostgroup(apiconnection, module, action):
    changed = False
    # Create a New Host
    conn = apiconnection
    dellemc = conn.provisioning
    # Compile a list of existing hosts.
    hostgrouplist = dellemc.get_hostgroup_list()
    # Check if Host Name already exists.
    if module.params['hostgroup_id'] in hostgrouplist:
        mvlist = dellemc.get_masking_views_by_host(\
                initiatorgroup_name=module.params['host_id'])
        if len(mvlist) < 1:
            dellemc.delete_hostgroup(hostgroup_id=module.params['hostgroup_id'])
            changed = True
            message = "HostGroup Deleted"
        else:
            message = module.params['host_id'] + " host is part of a Masking " \
                                                "view"
    else:
        message = "Specified hostgroup does not exist"
    facts = ({'message': message})
    result = {'state': 'info', 'changed': changed}
    module.exit_json(ansible_facts={'host_detail': facts}, **result)


from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.dellemc import dellemc_pmax_argument_spec, pmaxapi

def main():
    argument_spec = dellemc_pmax_argument_spec()
    argument_spec.update(dict(
        host_id=dict(type='str', required=False),
        initiator_list=dict(type='list', required=False),
        host_list=dict(type='list', required=False),
        hostgroup_id=dict(type='str', required=False),
        action=dict(type='str', required=True, choices=['create_host',
                                                        'delete_host',
                                                        'create_hostgroup',
                                                        'delete_hostgroup',
                                                        'add_host_to_hostgroup',
                                                        'remove_host_from_hostgroup',
                                                        'add_initiator',
                                                        'remove_initiator'])
    )
    )
    module = AnsibleModule(argument_spec=argument_spec)
    # Setup connection to API
    conn = pmaxapi(module)
    if module.params['action'] == "create_host":
        create_host(apiconnection=conn,module=module)
    elif module.params['action'] == "delete_host":
        delete_host(apiconnection=conn,module=module)
    elif module.params['action'] == "create_hostgroup":
        create_hostgroup(apiconnection=conn,module=module)
    elif module.params['action'] == "delete_hostgroup":
        delete_hostgroup(apiconnection=conn,module=module)

    # TODO add and remove host/initiator functions to be added



if __name__ == '__main__':
    main()
