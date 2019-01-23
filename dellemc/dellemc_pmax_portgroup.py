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
short_description: "Create port group on Dell EMC PowerMax or VMAX All
Flash"
version_added: "2.8"
description:
  - "This module has been tested against UNI 9.0. Every effort has been made
  to verify the scripts run with valid input. These modules are a tech preview"
module: dellemc_pmax_createportgroup
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
  portgroup_id:
    description:
      - "32 Character string no special character permitted except for
      underscore"
  port_list:
    description:
      - "List of WWNs of Frontend Ports to be part of Port Group either FA
      or SE"
requirements:
  - Ansible
  - "Unisphere for PowerMax version 9.0 or higher."
  - "VMAX All Flash, VMAX3, or PowerMax storage Array."
  - "PyU4V version 3.0.0.8 or higher using PIP python -m pip install PyU4V"
'''
EXAMPLES = '''
---
- name: "Create a New Port Group"
  connection: local
  hosts: localhost
  vars:
    array_id: 000197600156
    password: smc
    unispherehost: "192.168.1.123"
    universion: "90"
    user: smc
    verifycert: false
  tasks:
    - name: "Create New Port Group and add ports"    
      dellemc_pmax_portgroup:
             unispherehost: "{{unispherehost}}"
             universion: "{{universion}}"
             verifycert: "{{verifycert}}"
             user: "{{user}}"
             password: "{{password}}"
             array_id: "{{array_id}}"
             portgroup_id: "Ansible_PG"
             array_ports:
               -  FA-1D:5
               -  FA-2D:5
             
'''
RETURN = r'''
'''
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.dellemc import dellemc_pmax_argument_spec, pmaxapi


def create_portgroup(apiconnection, module):
    dellemc = apiconnection
    changed = False
    pg_list = dellemc.get_portgroup_list()
    pg_details= "Nothing to Display"
    message = "no changes made, check input parameters"
    # Check if Port group exists

    if module.params['portgroup_id'] not in pg_list:
        ports_list = []
        # format ports to dict in list, e.g.
        # ["FA-1D:5"] to [{'directorId': 'FA-1D', 'portId': '5'}]
        for item in module.params.get('array_ports'):
            director_port = {}
            director_port["directorId"] = item.split(":")[0]
            director_port["portId"] = item.split(":")[1]
            ports_list.append(director_port)
        dellemc.create_multiport_portgroup(
            module.params.get('portgroup_id'), ports_list)
        pg_details = dellemc.get_portgroup(module.params['portgroup_id'])
        changed = True
    else:
        message = "Port Group already exists"
        pg_details = dellemc.get_portgroup(module.params['portgroup_id'])
    facts = ({'message': message, 'portgroup_details': pg_details})
    result = {'state': 'info', 'changed': changed}
    module.exit_json(ansible_facts={'portgroup_detail': facts}, **result)

def add_port(apiconnection, module):
    # No Checks to see if ports are already in the group due to API
    # behavior, API will retrun success if the change doesn't need to be
    # done for add
    dellemc = apiconnection
    changed = False
    pg_list = dellemc.get_portgroup_list()
    pg_details= "Nothing to Display"
    message = "no changes made, check input parameters"
    # Check if Port group exists
    if module.params['portgroup_id'] in pg_list:
        for item in module.params.get('array_ports'):
            dellemc.modify_portgroup(module.params['portgroup_id'],
            add_port=tuple(item.split(":")))
        changed = True
        pg_details = dellemc.get_portgroup(module.params['portgroup_id'])

    else:
        message = "No storage group matches the name specified, check input"
    facts = ({'message': message, 'portgroup_details': pg_details})
    result = {'state': 'info', 'changed': changed}
    module.exit_json(ansible_facts={'portgroup_detail': facts}, **result)

def remove_ports(apiconnection, module):
    dellemc = apiconnection
    changed = False
    pg_list = dellemc.get_portgroup_list()
    pg_details= "Nothing to Display"
    message = "no changes made, check input parameters"
    # Check if Port group exists
    if module.params['portgroup_id'] in pg_list:
        pg_portlist = dellemc.get_portgroup(module.params['portgroup_id'])["symmetrixPortKey"]
        for i in pg_portlist:
            try:
                split = i['portId'].split(':')
                i['portId'] = split[1]
            except IndexError:
                pass
            for item in module.params['array_ports']:
                array_dir, array_port = item.split(":")
                if i["directorId"] == array_dir and i['portId'] == array_port:
                    dellemc.modify_portgroup(module.params['portgroup_id'],
                                             remove_port=tuple(item.split(":")))
                    changed = True
        pg_details = dellemc.get_portgroup(module.params['portgroup_id'])

    else:
        message = "No storage group matches the name specified, check input"
    facts = ({'message': message, 'portgroup_details': pg_details})
    result = {'state': 'info', 'changed': changed}
    module.exit_json(ansible_facts={'portgroup_detail': facts}, **result)

def delete_portgroup(apiconnection, module):
    dellemc = apiconnection
    changed = False
    #Build a list of Port Groups that are not in masking view
    pg_list = dellemc.get_portgroup_list(filters=({
    "num_of_masking_views": "0"}))
    message = "no changes made, check that port group exists and is not part" \
              "of a masking view"
    if module.params['portgroup_id'] in pg_list:

        dellemc.delete_portgroup(module.params['portgroup_id'])
        changed = True
    pg_list = dellemc.get_portgroup_list()

    facts = ({'message': message, 'portgroups': pg_list})
    result = {'state': 'info', 'changed': changed}
    module.exit_json(ansible_facts={'portgroup_detail': facts}, **result)



def main():
    changed = False
    argument_spec = dellemc_pmax_argument_spec()
    argument_spec.update(dict(
            portgroup_id=dict(type='str', required=True),
            action=dict(type='str',required=True,choices=['create', 'show',
                                                          'add_ports',
                                                          'remove_ports',
                                                          'delete']),
            array_ports=dict(type='list', default=[])
        )
    )
    module = AnsibleModule(argument_spec=argument_spec)
    # Setup connection to API and import provisioning modules.
    conn = pmaxapi(module)
    dellemc = conn.provisioning
    if module.params.get('action') == 'show':
        result.update(dellemc.get_portgroup(
            module.params.get('port_group')))
    elif module.params.get('action') == 'create':
        create_portgroup(apiconnection=dellemc, module=module)
    elif module.params.get('action') == 'add_ports':
        add_port(apiconnection=dellemc, module=module)
    elif module.params.get('action') == 'remove_ports':
        remove_ports(apiconnection=dellemc, module=module)
    elif module.params.get('action') == 'delete':
        delete_portgroup(apiconnection=dellemc, module=module)
    else:
        module.fail_json(msg='unsupported action')

    module.exit_json(changed=changed)
if __name__ == '__main__':
    main()
