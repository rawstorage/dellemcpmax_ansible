#!/usr/bin/python
# Copyright: (C) 2018, DellEMC
# Author(s): Paul Martin <paule.martin@dell.com>
# Author(s): Olivier Carminati <olivier.carminati@bpce-it.fr>
# Author(s): Julien Brusset <julien.brusset.prestataire@bpce-it.fr>
# GNU General Public License v3.0+ (see COPYING
# or https://www.gnu.org/licenses/gpl-3.0.txt)

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
short_description: "Storage group Control Module for Dell EMC PowerMax or 
VMAX All Flash Arrays, can be used to show, create, delete, and add volumes,
volume removal is handled in dellemc_pmax_volume module"
version_added: "2.8"
description:
  - "This module has been tested against UNI 9.0 with VMAX3, VMAX All Flash 
  and PowerMAX. Every effort has been made to verify the scripts run with 
  valid input. These modules are a tech preview."
module: dellemc_pmax_cascadedsg
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
  parent_sg:
    description:
      - "name of Parent SG"
    type: string
    required: true
  child_sg_list:
    description:
      - "List of Child Stroage groups to be added or removed from Parent"
    type: list
    required: True
  parent_state:
    description:
      - "Present or Absent, Absent will delete the parent storage group"
    type: string
    required: true
  child_state:
    description:
      - "Present or Absent, Absent will attempt to remove children in the list 
      from the parent storage group"
    type: string
    required: true
requirements:
  - Ansible
  - "Unisphere for PowerMax version 9.0 or higher."
  - "VMAX All Flash, VMAX3, or PowerMax storage Array."
  - "PyU4V version 3.0.0.9 or higher using PIP python -m pip install PyU4V"
'''
EXAMPLES = '''
- name: "Provision a new storage group"
  hosts: localhost
  connection: local
  gather_facts: no
  vars_files:
    - vars.yml
  tasks:
    - name: "Create Cascaded Storage Group Relationship"
      dellemc_pmax_cascadedsg:
        array_id: "{{array_id}}"
        password: "{{password}}"
        unispherehost: "{{unispherehost}}"
        universion: "{{universion}}"
        user: "{{user}}"
        verifycert: "{{verifycert}}"
        parent_sg: ansible_parent
        child_sg_list:
        - ansible_child1
        - ansible_child2
        parent_state: present
        child_state: present
    - debug: var=storagegroup_detail
'''
RETURN = r'''
ok: [localhost] => {
    "storagegroup_detail": {
        "message": "Changes Successful",
        "storage_group_details": {
            "VPSaved": "N/A",
            "cap_gb": 0.0,
            "child_storage_group": [
                "ansible_child1",
                "ansible_child2"
            ],
            "compression": false,
            "device_emulation": "N/A",
            "num_of_child_sgs": 2,
            "num_of_masking_views": 0,
            "num_of_parent_sgs": 0,
            "num_of_snapshots": 0,
            "num_of_vols": 0,
            "slo": "NONE",
            "slo_compliance": "NONE",
            "storageGroupId": "ansible_parent",
            "type": "Parent",
            "unprotected": true
        }
    }
}
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.dellemc import dellemc_pmax_argument_spec, pmaxapi


class DellEmcCascadeStorageGroup(object):
    def __init__(self):
        self._argument_spec = dellemc_pmax_argument_spec()
        self._argument_spec.update(dict(
            parent_sg=dict(type='str', required=True),
            child_sg_list=dict(type='list', required=False),
            parent_state=dict(type='str', choices=['present', 'absent'],
                              required=True),
            child_state=dict(type='str', choices=['present', 'absent'],
                             required=True)))

        self._module = AnsibleModule(argument_spec=self._argument_spec)
        self._conn = pmaxapi(self._module)

        self._parent_sg = self._module.params['parent_sg']
        self._child_sg_list = self._module.params['child_sg_list']

        self._sglist = self._conn.provisioning.get_storage_group_list()
        if self._parent_sg in self._sglist:
            self._parent_sg_detail = self._conn.provisioning.get_storage_group(
                storage_group_name=self._parent_sg)
        else:
            self._parent_sg_detail = None

        self._changed = False
        self._message = ""
        self._error_message = ""

    def _add_child_sg(self):

        for child in self._child_sg_list:
            if not self._parent_sg_detail.get("child_storage_group") or \
                    child not in self._parent_sg_detail.get(
                "child_storage_group"):
                try:
                    self._conn.provisioning.add_child_sg_to_parent_sg(
                        child_sg=child, parent_sg=self._parent_sg)
                    self._changed = True
                    self._message += "{} added. ".format(child)

                except Exception as error:
                    self._error_message += "Child {}. Error {}. ".format(child,
                                                                         error)

        if self._error_message != "":
            self._module.fail_json(
                msg="Problem adding the following child storage group(s) {}"
                    .format(self._error_message), changed=self._changed)

        if not self._message:
            self._message = "No change made. Already in that state"

    def _remove_child_sg(self):

        if self._parent_sg_detail["num_of_child_sgs"] > \
                len(self._child_sg_list) \
                or self._parent_sg_detail["num_of_masking_views"] == 0:
            for child in self._child_sg_list:
                try:
                    if child in self._parent_sg_detail. \
                            get("child_storage_group"):
                        self._conn.provisioning.remove_child_sg_from_parent_sg(
                            child_sg=child, parent_sg=self._parent_sg)
                        self._changed = True
                        self._message += "{} removed. ".format(child)

                except Exception as error:
                    self._error_message += "Child {}. Error {}. ".format(child,
                                                                         error)
        else:
            message = "Unable to remove Child Storage groups, at least one " \
                      "child storage group must exist if parent is part of a " \
                      "Masking view"
            self._module.fail_json(msg=message, changed=self._changed)

        if self._error_message:
            message = "Problem removing the following child storage group(s)" \
                      " {}".format(self._error_message)
            self._module.fail_json(msg=message, changed=self._changed)

        if not self._message:
            self._message = "No change made. Already in that state."

    def _create_cascaded(self):

        if not self._child_sg_list:
            self._module.fail_json(msg="child_sg_list cannot be empty.",
                                   changed=self._changed)

        child_exists = True
        child_message = "Specified Child Storage Group(s) do not exist "
        for child in self._child_sg_list:
            if child not in self._sglist:
                child_message += "{} ".format(child)
                child_exists = False

        if not child_exists:
            self._module.fail_json(msg=child_message, changed=self._changed)
        # prechecks passed.  Module can now create cascaded relationship

        if self._parent_sg in self._sglist:
            if self._parent_sg_detail["type"] == "Standalone" and \
                    self._parent_sg_detail["num_of_vols"] == 0:
                self._add_child_sg()
            elif self._parent_sg_detail["type"] == "Parent":
                self._add_child_sg()
        else:
            try:
                self._conn.provisioning. \
                    create_storage_group(srp_id="None", slo="None",
                                         sg_id=self._parent_sg)
                self._changed = True
                self._parent_sg_detail = self._conn.provisioning.get_storage_group(
                    storage_group_name=self._parent_sg)
                self._add_child_sg()
            except Exception as error:
                self._module.fail_json(msg="Problem creating Parent storage "
                                           "group. {}".format(error),
                                       changed=self._changed)

    def _delete_sg(self):

        if self._parent_sg in self._sglist:
            try:
                self._conn.provisioning.delete_storagegroup(
                    storagegroup_id=self._parent_sg)
                self._changed = True
                self._message = " {} deleted.".format(self._parent_sg)
            except Exception as error:
                message = "Unable to delete Parent Storage Group check if " \
                          "it is Part of a Masking View before attempting " \
                          "to delete. {}".format(error)
                self._module.fail_json(msg=message, changed=self._changed)

        if not self._message:
            self._message = "Resource already in the requested state"

    def apply_module(self):

        if self._module.params["parent_state"] == 'present' and \
                self._module.params["child_state"] == 'present':
            self._create_cascaded()

        elif self._module.params["parent_state"] == 'present' and \
                self._module.params["child_state"] == 'absent':
            self._remove_child_sg()

        elif self._module.params["parent_state"] == 'absent':
            self._delete_sg()

        # Importing Py4UV exception
        from PyU4V.utils.exception import ResourceNotFoundException
        try:
            sgdetails = self._conn.provisioning.get_storage_group(
                storage_group_name=self._parent_sg)
        except ResourceNotFoundException:
            sgdetails = "Storage group {} does not exist".format(
                self._parent_sg)

        facts = (
        {'storage_group_details': sgdetails, 'message': self._message})
        result = {'state': 'info', 'changed': self._changed}
        self._module.exit_json(ansible_facts={'storagegroup_detail': facts},
                               **result)


def main():
    DellEmcCascadeStorageGroup().apply_module()


if __name__ == '__main__':
    main()