#!/usr/bin/python
# Copyright (C) 2018 DellEMC
# Author(s): Paul Martin <paule.martin@dell.com>
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

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
short_description: "Create or modify port group on Dell EMC PowerMax or VMAX All
Flash"
version_added: "2.8"
description:
  - "This module will ensure that the Specified Port Group is Present or 
  Absent on the array specified resulting in either a create or delete 
  operation.  The port list supplied will be checked against the current 
  configuration of the port group and added/removed as needed. This module has 
  been 
  tested with Unisphere 9.0. 
  Every effort has been made to verify the scripts run with valid input. 
  These modules are a tech preview"
  
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
  array_ports:
    description:
      - "List of Ports to be part of Port Group either FA or SE"
  state:
    description:
      - "Whether Port group should exist or not"
    required: true
  port_state:
    description:
      - "Whether Array Ports in list should be part of the port group or not"
    required: true
    
requirements:
  - Ansible
  - "Unisphere for PowerMax version 9.0 or higher."
  - "VMAX All Flash, VMAX3, or PowerMax storage Array."
  - "PyU4V version 3.0.0.9 or higher using PIP python -m pip install PyU4V"
'''
EXAMPLES = '''
---
- name: "Create a New Port Group"
  connection: local
  hosts: localhost
  vars_files:
    - vars.yml

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
               -  FA-1D:4
               -  FA-2D:4
             state: present 
             port_state: in_pg    
    - name: "Remove ports"
      dellemc_pmax_portgroup:
             unispherehost: "{{unispherehost}}"
             universion: "{{universion}}"
             verifycert: "{{verifycert}}"
             user: "{{user}}"
             password: "{{password}}"
             array_id: "{{array_id}}"
             portgroup_id: "Ansible_PG2"
             array_ports:
               -  FA-2D:8
             state: present
             port_state: out_of_pg
    - name "Delete Port Group"
      dellemc_pmax_portgroup:
             unispherehost: "{{unispherehost}}"
             universion: "{{universion}}"
             verifycert: "{{verifycert}}"
             user: "{{user}}"
             password: "{{password}}"
             array_id: "{{array_id}}"
             portgroup_id: "Ansible_PG2"
             array_ports:
               -  FA-2D:8
             state: absent
             port_state: out_of_pg       
'''
RETURN = r'''
changed: [localhost] => {
    "ansible_facts": {
        "portgroup_detail": {
            "message": "no changes made, check input parameters",
            "portgroup_details": {
                "maskingview": [],
                "num_of_masking_views": 0,
                "num_of_ports": 2,
                "portGroupId": "Ansible_PG",
                "symmetrixPortKey": [
                    {
                        "directorId": "FA-2D",
                        "portId": "FA-2D:4"
                    },
                    {
                        "directorId": "FA-1D",
                        "portId": "FA-1D:4"
                    }
                ],
                "type": "Fibre"
            }
        }
    },
    "changed": true,
    "invocation": {
        "module_args": {
            "array_id": "000197600156",
            "array_ports": [
                "FA-1D:4",
                "FA-2D:4"
            ],
            "password": "VALUE_SPECIFIED_IN_NO_LOG_PARAMETER",
            "portgroup_id": "Ansible_PG",
            "state": "present",
            "unispherehost": "192.168.1.1",
            "universion": 90,
            "user": "VALUE_SPECIFIED_IN_NO_LOG_PARAMETER",
            "verifycert": false
        }
    },
    "state": "info"
}

ok: [localhost] => {
    "ansible_facts": {
        "portgroup_detail": {
            "message": "no changes made, check that port group exists and is not part of a masking view",
            "portgroups": [
                "Demo_GK_PG",
                "HCA_PG",
                "HSBC_PG",
                "Lab_GK_PG",
                "MF_TEST_PG",
                "MyMetroSG_PG",
                "Pat_VdBench_1_PG",
                "Pat_VdBench_2_PG",
                "Pat_VdBench_3_PG",
                "Pat_VdBench_4_PG",
                "PM_DEL40_GK_PG",
                "SRDF_TEST_PG",
                "tesjn_PG",
                "Uniprod_MGMT_PG"
            ]
        }
    },
    "changed": false,
    "invocation": {
        "module_args": {
            "array_id": "000197600156",
            "array_ports": [
                "FA-1D:4",
                "FA-2D:4",
            ],
            "password": "VALUE_SPECIFIED_IN_NO_LOG_PARAMETER",
            "portgroup_id": "Ansible_PG",
            "state": "absent",
            "unispherehost": "192.168.1.1",
            "universion": 90,
            "user": "VALUE_SPECIFIED_IN_NO_LOG_PARAMETER",
            "verifycert": false
        }
    },
    "state": "info"
}
'''
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.dellemc import dellemc_pmax_argument_spec, pmaxapi


class DellEmcPortGroup(object):
    def __init__(self):
        self.argument_spec = dellemc_pmax_argument_spec()
        self.argument_spec.update(dict(
            portgroup_id=dict(type='str', required=True),
            state=dict(type='str', required=True, choices=['absent',
                                                           'present']),
            array_ports=dict(type='list', default=[]),
            port_state=dict(type='str', required=True, choices=['in_pg',
                                                                'out_of_pg']),
        )
        )
        self.module = AnsibleModule(argument_spec=self.argument_spec)

        self.conn = pmaxapi(self.module)

    def create_or_modify_portgroup(self):
        changed = False
        pg_list = self.conn.provisioning.get_portgroup_list()
        pg_details = "Nothing to Display"
        message = "No changes made, check input parameters"
        valid_array_ports = self.conn.provisioning.get_port_list()
        # Check if Port group exists

        if self.module.params['portgroup_id'] not in pg_list:
            ports_list = []
            # format ports to dict in list, e.g.
            # ["FA-1D:5"] to [{'directorId': 'FA-1D', 'portId': '5'}]
            for item in self.module.params.get('array_ports'):
                director_port = {}
                director_port["directorId"] = item.split(":")[0]
                director_port["portId"] = item.split(":")[1]
                ports_list.append(director_port)
            try:
                self.conn.provisioning.create_multiport_portgroup(
                    self.module.params.get('portgroup_id'), ports_list)
                pg_details = self.conn.provisioning.get_portgroup(
                    self.module.params['portgroup_id'])
                changed = True
            except Exception:
                message = "problem creating port group"
                self.module.exit_json(msg=message)

        elif self.module.params['portgroup_id'] in pg_list:
            # check if port list supplied matches with what is in the group.
            # Building 2 dictionaries with same keys to compare
            ansible_ports_list = []
            for i in self.module.params['array_ports']:
                directorid, portid = i.split(":")
                ansible_ports_list.append({'directorId': directorid,
                                           'portId': portid})
            array_pg_ports_list = []
            array_pg_ports = self.conn.provisioning.get_portgroup(
                portgroup_id=self.module.params[
                    'portgroup_id'])["symmetrixPortKey"]
            # normalise array_pg dictionary list to match expected, Bugfix until
            #  9.1
            for i in array_pg_ports:
                try:
                    split = i['portId'].split(':')
                    i['portId'] = split[1]
                except IndexError:
                    pass
                array_pg_ports_list.append(i)

            # Attempt to add new ports.
            if self.module.params['portgroup_id'] in pg_list and \
                    self.module.params[
                        'port_state'] == 'in_pg':
                for ansible_port in ansible_ports_list:
                    if ansible_port not in array_pg_ports_list:
                        ansible_port_tuple = (
                            ansible_port['directorId'], ansible_port[
                                'portId'])
                        try:
                            self.conn.provisioning.modify_portgroup(
                                self.module.params['portgroup_id'],
                                add_port=ansible_port_tuple)
                            changed = True
                            pg_details = self.conn.provisioning.get_portgroup(
                                self.module.params['portgroup_id'])
                            message = "Ports Added"
                        except Exception:
                            message = "Unable to Add Port " \
                                      "Check port %s is valid and of the correct" \
                                      "emulation " % str(ansible_port_tuple)
                            pg_details = self.conn.provisioning.get_portgroup(
                                self.module.params['portgroup_id'])
            # Attempt to remove ports.
            elif self.module.params['portgroup_id'] in pg_list and \
                    self.module.params[
                        'port_state'] == 'out_of_pg':
                for port in self.module.params['array_ports']:
                    ansible_port_tuple = tuple(port.split(":"))
                    try:
                        self.conn.provisioning.modify_portgroup(
                            portgroup_id=self.module.params[
                                'portgroup_id'],
                            remove_port=ansible_port_tuple)
                        changed = True
                        pg_details = self.conn.provisioning.get_portgroup(
                            self.module.params[
                                'portgroup_id'])
                    except Exception:
                        message = "Unable to remove one or more ports " \
                                  "specified"
            else:
                message = "No Changes made"

        facts = ({'message': message, 'portgroup_details': pg_details})
        result = {'state': 'info', 'changed': changed}
        self.module.exit_json(ansible_facts={'portgroup_detail': facts},
                              **result)

    def delete_portgroup(self):
        changed = False
        # Build a list of Port Groups that are not in masking view
        pg_list = self.conn.provisioning.get_portgroup_list(
            filters=({"num_of_masking_views"
                      : "0"}))
        if self.module.params['portgroup_id'] in pg_list:
            self.conn.provisioning.delete_portgroup(
                self.module.params['portgroup_id'])
            changed = True
            message = "Port Group Deleted"
        pg_list = self.conn.provisioning.get_portgroup_list()

        facts = ({'message': message, 'portgroups': pg_list})
        result = {'state': 'info', 'changed': changed}
        self.module.exit_json(ansible_facts={'portgroup_detail': facts},
                              **result)

    def apply_module(self):
        changed = False
        if self.module.params['state'] == 'present':
            self.create_or_modify_portgroup()

        elif self.module.params['state'] == 'absent':
            self.delete_portgroup()

        else:
            self.module.fail_json(msg='unsupported action')
        self.module.exit_json(changed=changed)


def main():
    d = DellEmcPortGroup()
    d.apply_module()


if __name__ == '__main__':
    main()
