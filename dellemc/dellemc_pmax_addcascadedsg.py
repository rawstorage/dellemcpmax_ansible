#!/usr/bin/python
# Copyright: (C) 2018, DellEMC
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
short_description: "Add Child SG to an existing Storage Group, esisting 
Storage Group"
version_added: "2.8"
description:
  - "Adds existing child storage group, both parent and child storage 
  groups must exist and parent storeag group should not contain any volumes.
  This module has been tested against UNI 9.0. Every effort has been made
  to verify the scripts run with valid input. These modules are a tech preview."
module: dellemc_pmax_createsg
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
  child_sg:
    description:
      - "Storage Group Name for Child SG"
  parent_sg:
    description:
      - "Storage Group name for parent storage group"
requirements:
  - Ansible
  - "Unisphere for PowerMax version 9.0 or higher."
  - "VMAX All Flash, VMAX3, or PowerMax storage Array."
  - "PyU4V version 3.0.0.8 or higher using PIP python -m pip install PyU4V"
'''
EXAMPLES = '''
---
- name: "Provision Storage For DB Cluster"
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
    - name: "Base Values for Task Add module Specific paramters"
      dellemc_pmax_addcascadedsg:
        unispherehost: "{{unispherehost}}"
        universion: "{{universion}}"
        array_id: "{{array_id}}"
        user: "{{user}}"
        password: "{{password}}"
        verifycert: "{{verifycert}}"
        parent_sg: "Parent_SG"
        child_sg: "Child_SG"
'''
RETURN = '''
dellemc_pmax_createsg:
    description: Information about storage group created
    returned: success
    type: dict
    sample: '{
        "some_detail": {
            "somevalues":
            }
        }'
'''
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.dellemc import dellemc_pmax_argument_spec, pmaxapi

def main():
    changed = False
    argument_spec = dellemc_pmax_argument_spec()
    argument_spec.update(dict(
            parent_sg=dict(type='str', required=True),
            child_sg=dict(type='str', required=True)
        )
    )
    module = AnsibleModule(argument_spec=argument_spec)
    # Setup connection to API and import provisioning modules.
    conn = pmaxapi(module)
    dellemc = conn.provisioning
    # Compile a list of existing stroage groups.
    sglist = dellemc.get_storage_group_list()
    # Check if Storage Group already exists
    if module.params['parent_sg'] and module.params['child_sg'] in sglist:
        # Check that parent SG is either of type parent or standalone with
        # no volumes
        if dellemc.get_storage_group(module.params['parent_sg'])["type"]== "Standalone"
            and dellemc.get_storage_group(module.params['parent_sg'])[
                "num_of_vols"]=0:
            dellemc.add_child_sg_to_parent_sg(child_sg=module.params[
                'child_sg'], parent_sg=module.params['parent_sg'])
            changed = True
        elif dellemc.get_storage_group(module.params['parent_sg'])["type"]==\
             "Parent":
            dellemc.add_child_sg_to_parent_sg(child_sg=module.params[
                'child_sg'], parent_sg=module.params['parent_sg'])
            changed = True
    else:
        module.fail_json(msg='Both Parent and Child SG must exist for module '
                             'to run sucessfully', changed=False)
    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()


