#!/usr/bin/python
# Copyright (C) 2018 DellEMC
# Author(s): Paul Martin <paule.martin@dell.com>
# Author(s): Olivier Carminati <olivier.carminati@bpce-it.fr>
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
  - "Julien Brusset (@jbrt)"
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
    required: true
  password:
    description:
      - "password for Unisphere user"
    required: true
  portgroup_id:
    description:
      - "32 Character string no special character permitted except for
      underscore"
    required: true
  new_portgroup_id:
    description:
      - "32 Character string no special character permitted except for
      underscore"
    required: false
  array_ports:
    description:
      - "List of Ports to be part of Port Group either FA or SE"
    required: false
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
  - "PyU4V version 3.0.0.10 or higher using PIP python -m pip install PyU4V"
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
    - name: "Rename PG"
      dellemc_pmax_portgroup:
             unispherehost: "{{unispherehost}}"
             universion: "{{universion}}"
             verifycert: "{{verifycert}}"
             user: "{{user}}"
             password: "{{password}}"
             array_id: "{{array_id}}"
             portgroup_id: "Ansible_PG2"
             new_portgroup_id: "Ansible_PG2"
             state: present
    - name "Delete Port Group"
      dellemc_pmax_portgroup:
             unispherehost: "{{unispherehost}}"
             universion: "{{universion}}"
             verifycert: "{{verifycert}}"
             user: "{{user}}"
             password: "{{password}}"
             array_id: "{{array_id}}"
             portgroup_id: "Ansible_PG2"
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
import re


class DellEmcPortGroup(object):
    """
    Creating, Updating or Deleting a PortGroup
    """
    def __init__(self):
        self._argument_spec = dellemc_pmax_argument_spec()
        self._argument_spec.update(dict(
            portgroup_id=dict(type='str', required=True),
            new_portgroup_id=dict(type='str', required=False),
            state=dict(type='str', required=True, choices=['absent',
                                                           'present']),
            array_ports=dict(type='list', required=False, default=[]),
            port_state=dict(type='str', required=False, choices=['in_pg',
                                                                 'out_of_pg']),
        ))
        self._module = AnsibleModule(argument_spec=self._argument_spec)
        self._conn = pmaxapi(self._module)
        self._portgroup_id = self._module.params.get('portgroup_id')
        self._array_ports = self._module.params.get('array_ports')
        self._changed = False
        self._message = []

    def _create_portgroup(self):
        """
        Create a new PortGroup
        :return: None
        """
        ports_list = []

        # format ports to dict in list, e.g.
        # ["FA-1D:5"] to [{'directorId': 'FA-1D', 'portId': '5'}]
        for item in self._array_ports:
            ports_list.append({"directorId": item.split(":")[0],
                               "portId": item.split(":")[1]})
        try:
            self._conn.provisioning.create_multiport_portgroup(self._portgroup_id,
                                                               ports_list)
            self._message.append("Port group {} created".format(self._portgroup_id))
            self._changed = True

        except Exception as error:
            self._module.fail_json(msg="problem creating port group. Error {}".
                                   format(error),
                                   changed=self._changed)

    def _add_new_ports(self, actual_ports_in_pg):
        """
        Add port in a PortGroup
        :param actual_ports_in_pg: list of port that are actually in PortGroup
        :return: None
        """

        # Make a list with port to add that are not actually in PortGroup
        ports_not_in_pg = set(self._array_ports) - set(actual_ports_in_pg)

        for ansible_port in ports_not_in_pg:
            directorid, portid = ansible_port.split(":")
            ansible_port_tuple = (directorid, portid)
            try:
                self._conn.provisioning.\
                    modify_portgroup(portgroup_id=self._portgroup_id,
                                     add_port=ansible_port_tuple)

                self._changed = True
                self._message.append("Port {} added".
                                     format(':'.join(map(str, ansible_port_tuple))))

            except Exception:
                msg = "Unable to Add Port Check port {} is valid and of the " \
                      "correct emulation ".format(':'.join(map(str, ansible_port_tuple)))
                self._module.fail_json(msg=msg)

    def _pre_checks(self):
        """
        Launch some pre-checks before attempting creating or modifying a PG
        :return: None
        """
        if self._array_ports:
            # Collect port list from array and transform it to format
            # ["FA-2D:4", "FA-2D:6", ...]
            ports_list = self._conn.provisioning.get_port_list()
            valid_array_ports = list(map(lambda x: "{}:{}"
                                         .format(x['directorId'], x['portId']),
                                         ports_list))

            # Check if all ports exist on the array
            if not set(self._array_ports).issubset(valid_array_ports):
                self._module.fail_json(msg="some port are not found on the array."
                                           "check input {}."
                                       .format(self._array_ports),
                                       changed=self._changed)

    def _remove_ports(self, actual_ports_in_pg):
        """
        Remove a list of port from a PortGroup
        :param actual_ports_in_pg: list of port that are actually in PortGroup
        :return: None
        """
        # Make a list with port to remove that are  actually in PortGroup
        ports_in_pg = set(self._array_ports) & set(actual_ports_in_pg)
        for port in ports_in_pg:
            ansible_port_tuple = tuple(port.split(":"))
            try:
                self._conn.provisioning.\
                    modify_portgroup(portgroup_id=self._portgroup_id,
                                     remove_port=ansible_port_tuple)
                self._changed = True
                self._message.append("Port {} removed."
                                     .format(':'.join(map(str, ansible_port_tuple))))

            except Exception as error:
                msg = "Unable to remove one or more ports specified"
                self._module.fail_json(msg="{}. Error {}".format(msg, error),
                                       changed=self._changed)

    def _rename_portgroup(self):
        """
        Renaming an existing PortGroup
        :return: None
        """
        try:
            self._conn.provisioning.\
                modify_portgroup(portgroup_id=self._portgroup_id,
                                 rename_portgroup=self._module.params['new_portgroup_id'])

            self._changed = True
            # Updating portgroup_id to be consistent with the next facts gathering
            self._portgroup_id = self._module.params['new_portgroup_id']
            self._message.append("PortGroup renamed to {}".format(self._portgroup_id))

        except Exception as error:
            self._module.fail_json(msg="Unable to rename PortGroup ({})".
                                   format(error))

    def _updating_portgroup(self):
        """
        Updating an existing PortGroup (adding/removing ports)
        :return: None
        """
        # Collect actual port in PG
        dict_ports_in_pg = self._conn. \
            provisioning. \
            get_portgroup(portgroup_id=self._portgroup_id)["symmetrixPortKey"]

        # normalise array_pg dictionary list to match expected,
        # bug fix until 9.1 in there to account for incorrect
        # key data being returned on some systems.
        # PortId was being returned in the
        # format FA11D:6 instead of just the 6
        actual_ports_in_pg = []
        pattern_normal = re.compile("^FA-\d{1,2}D:\d{1,2}")  # Ex: FA-2D:4
        pattern_reverse = re.compile("^\d{1,2}:FA-\d{1,2}D")  # Ex: 4:FA-2D

        for port in dict_ports_in_pg:
            # If the portId is like FA-2D:4
            if re.match(pattern_normal, port['portId']):
                actual_ports_in_pg.append(port['portId'])

            # If the portId is like 4:FA-2D
            if re.match(pattern_reverse, port['portId']):
                dirport, director = port['portId'].split(':')
                actual_ports_in_pg.append(":".join([director, dirport]))

            # If not pattern is matching it's a problem !
            if not re.match(pattern_normal, port['portId']) \
                    and not re.match(pattern_reverse, port['portId']):
                self._module.fail_json(msg="Cannot parsing FA port {} while updating PG".
                                           format(port['portId']))

        if self._module.params['port_state'] == 'in_pg':
            self._add_new_ports(actual_ports_in_pg)

        elif self._module.params['port_state'] == 'out_of_pg':
            self._remove_ports(actual_ports_in_pg)

    def _delete_portgroup(self):
        """
        Deleting a PortGroup
        :return: None
        """
        # Build a list of Port Groups that are not in masking view
        if self._portgroup_id in self._conn.provisioning. \
                get_portgroup_list(filters=({"num_of_masking_views": "0"})):
            self._conn.provisioning.delete_portgroup(self._portgroup_id)
            self._changed = True
            self._message.append("Port Group {} Deleted ".format(self._portgroup_id))

    def apply_module(self):
        """
        Main function for that object
        :return: None
        """
        # if 'present' try to create/update/rename a PortGroup
        if self._module.params['state'] == 'present':
            self._pre_checks()
            if self._portgroup_id not in self._conn.provisioning.get_portgroup_list():
                self._create_portgroup()

            else:
                # if renaming is required, this task will be exclusive
                if self._module.params['new_portgroup_id']:
                    self._rename_portgroup()
                else:
                    self._updating_portgroup()

        elif self._module.params['state'] == 'absent':
            self._delete_portgroup()

        else:
            self._module.fail_json(msg='unsupported action', changed=self._changed)

        # Importing Py4UV exception
        from PyU4V.utils.exception import ResourceNotFoundException
        try:
            pg_details = self._conn.provisioning.get_portgroup(self._portgroup_id)

        except ResourceNotFoundException:
            pg_details = "Port group {} does not exist".format(self._portgroup_id)

        if not self.changed:
            self._message.append("No Changes made. Already in that state.")

        facts = ({'message': self._message, 'portgroup_details': pg_details})
        result = {'state': 'info', 'changed': self._changed}
        self._module.exit_json(ansible_facts={'portgroup_detail': facts}, **result)


def main():
    """
    Main function
    :return: None
    """
    DellEmcPortGroup().apply_module()


if __name__ == '__main__':
    main()
