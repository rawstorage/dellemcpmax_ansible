#!/usr/bin/python
# Copyright: (C) 2018, DellEMC
# Author(s): Paul Martin <paule.martin@dell.com>
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
  sgname:
    description:
      - "Storage Group name 32 Characters no special characters other than
      underscore."
    required: true
  slo:
    description:
      - "Service Level for the storage group, Supported on VMAX3 and All Flash
      and PowerMAX NVMe Arrays running PowerMAX OS 5978 and above.  Default is
      set to Diamond, but user can override this by setting a different value."
    required: false
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
  luns:
    description:
      - "List describing volumes to be added or list of luns expected to be 
      in the storage group. list should have a unique combination of 
      num_vols, cap_gb, vol_name. See examples for usage"
    type: list
    required: false
    Default: empty list which will try to create storage group with no volumes 
  state:
    description:
      - "Valid values are present, absent, or current"
    type: string
    required: true
  resize:
    description:
      - "setting this parameter will attempt to resize volumes in the 
      supplied lunlist, volume requests in the lun list with matching label 
      will be resized providing device size in larger than current"
    type: bool
    required: false  

requirements:
  - Ansible
  - "Unisphere for PowerMax version 9.0 or higher."
  - "VMAX All Flash, VMAX3, or PowerMax storage Array."
  - "PyU4V version 3.0.0.8 or higher using PIP python -m pip install PyU4V"
'''
EXAMPLES = '''

'''
RETURN = r'''
ok: [localhost] => {
    "storagegroup_detail": {
        "message": "no changes made",
        "sg_volumes": [
            {
                "vol_name": "DATA",
                "cap_gb": 1.0,
                "volumeId": "00178",
                "wwn": "60000970000197600156533030313738"
            },
            {
                "vol_name": "DATA",
                "cap_gb": 1.0,
                "volumeId": "00179",
                "wwn": "60000970000197600156533030313739"
            },
            {
                "vol_name": "REDO",
                "cap_gb": 1.0,
                "volumeId": "0017A",
                "wwn": "60000970000197600156533030313741"
            },
            {
                "vol_name": "REDO",
                "cap_gb": 1.0,
                "volumeId": "0017B",
                "wwn": "60000970000197600156533030313742"
            }
        ],
        "storagegroup_detail": {
            "VPSaved": "100.0%",
            "base_slo_name": "Diamond",
            "cap_gb": 4.01,
            "compression": true,
            "device_emulation": "FBA",
            "num_of_child_sgs": 0,
            "num_of_masking_views": 0,
            "num_of_parent_sgs": 0,
            "num_of_snapshots": 0,
            "num_of_vols": 4,
            "service_level": "Diamond",
            "slo": "Diamond",
            "slo_compliance": "STABLE",
            "srp": "SRP_1",
            "storageGroupId": "Ansible_SG",
            "type": "Standalone",
            "unprotected": true,
            "vp_saved_percent": 100.0
        },
        "storagegroup_name": "Ansible_SG"
    }
}
ok: [localhost] => {
    "storagegroup_detail": {
        "message": "no changes made",
        "sg_volumes": [
            {
                "vol_name": "DATA",
                "cap_gb": 1.0,
                "volumeId": "00178",
                "wwn": "60000970000197600156533030313738"
            },
            {
                "vol_name": "DATA",
                "cap_gb": 1.0,
                "volumeId": "00179",
                "wwn": "60000970000197600156533030313739"
            },
            {
                "vol_name": "REDO",
                "cap_gb": 1.0,
                "volumeId": "0017A",
                "wwn": "60000970000197600156533030313741"
            },
            {
                "vol_name": "REDO",
                "cap_gb": 1.0,
                "volumeId": "0017B",
                "wwn": "60000970000197600156533030313742"
            }
        ],
        "storagegroup_detail": {
            "VPSaved": "100.0%",
            "base_slo_name": "Diamond",
            "cap_gb": 4.01,
            "compression": true,
            "device_emulation": "FBA",
            "num_of_child_sgs": 0,
            "num_of_masking_views": 0,
            "num_of_parent_sgs": 0,
            "num_of_snapshots": 0,
            "num_of_vols": 4,
            "service_level": "Diamond",
            "slo": "Diamond",
            "slo_compliance": "STABLE",
            "srp": "SRP_1",
            "storageGroupId": "Ansible_SG",
            "type": "Standalone",
            "unprotected": true,
            "vp_saved_percent": 100.0
        },
        "storagegroup_name": "Ansible_SG"
    }
}


'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.dellemc import dellemc_pmax_argument_spec, pmaxapi


class DellEmcCascadeStorageGroup(object):
    def __init__(self):
        self.argument_spec = dellemc_pmax_argument_spec()
        self.argument_spec.update(dict(
            parent_sg=dict(type='str', required=True),
            child_sg_list=dict(type='list', required=True),
            parent_state=dict(type='str', choices=['present', 'absent'],
                       required=True),
            child_state=dict(type='str', choices=['in_parent',
                                                  'not_in_parent'],
                       required=True)
        )
        )
        self.module = AnsibleModule(argument_spec=self.argument_spec)
        self.changed = False
        self.conn = pmaxapi(self.module)
        self.parent_sg = self.module.params['parent_sg']
        self.sglist = self.conn.provisioning.get_storage_group_list()

    def add_child_sg(self):
        message = "Changes Successful"
        error_message =""
        for child in self.module.params['child_sg_list']:
            try:
                self.conn.provisioning.add_child_sg_to_parent_sg(
                    child_sg=child, parent_sg=self.parent_sg)
                self.changed = True
            except Exception:
                error_message = error_message + child + " "
        if error_message != "":
            message = "Problem adding the following child storage group(s) " \
                      + error_message
        sgdetails = self.conn.provisioning.get_storage_group(
            storage_group_name =self.parent_sg)
        facts = ({'storage_group_details': sgdetails, 'message': message})
        result = {'state': 'info', 'changed': self.changed}
        self.module.exit_json(ansible_facts={'storagegroup_detail': facts},
                              **result)

    def remove_child_sg(self):
        message = "Changes Successful"
        error_message =""
        parent_sg_detail = self.conn.provisioning.get_storage_group(
            self.parent_sg)
        if parent_sg_detail["num_of_child_sgs"] > len(self.module.params[
                                                           'child_sg_list'])\
                or parent_sg_detail["num_of_masking_views"] == 0 :
            for child in self.module.params['child_sg_list']:
                try:
                    self.conn.provisioning.remove_child_sg_from_parent_sg(
                        child_sg=child, parent_sg=self.parent_sg)
                    self.changed = True
                except Exception:
                    error_message = error_message + child
        else:
            message = "Unable to remove Child Storage groups, at least one " \
                      "child storage group must exist if parent is part of a " \
                      "Masking view"
        if error_message != "":
            message = "Problem adding the following child storage group(s) " \
                      + error_message

        sgdetails = self.conn.provisioning.get_storage_group(
            storage_group_name =self.parent_sg)
        facts = ({'storage_group_details': sgdetails, 'message': message})
        result = {'state': 'info', 'changed': self.changed}
        self.module.exit_json(ansible_facts={'storagegroup_detail': facts},
                              **result)

    def create_cascaded(self):
        child_exists = True
        child_message = "Specified Child Storage Group(s) do not exist "
        for child in self.module.params['child_sg_list']:
            if child not in self.sglist:
                child_message = child_message + \
                          child\
                          + " "
                child_exists = False
        if not child_exists:
            self.module.exit_json(msg=child_message, changed=self.changed)
        # prechecks passed.  Module can now create cascaded relationship
        parent_sg_detail=self.conn.provisioning.get_storage_group(self.parent_sg)
        if self.parent_sg in self.sglist:
            if parent_sg_detail["type"] == "Standalone" and parent_sg_detail[
                  "num_of_vols"] == 0:
                self.add_child_sg()
            elif parent_sg_detail["type"] == "Parent":
                self.add_child_sg()
        else:
            try:
                self.conn.provisioning.create_storage_group(srp_id="None",
                                                        slo="None",
                                                        sg_id=self.parent_sg)
                self.changed=True
            except Exception:
                self.module.exit_json(msg="Problem creating Parent storage "
                                          "group", changed = self.changed)

    def delete_sg(self):
        message = "Resource already in the requested state"
        if self.parent_sg in self.sglist:
            try:
                self.conn.provisioning.delete_storagegroup(
                    storagegroup_id=self.parent_sg)
                self.changed = True
                message = "Delete Operation Completed"
            except Exception:
                message = "Unable to delete Parent Storage Group check if " \
                          "it is Part of a Masking View before attempting " \
                          "to delete"
        else:
            self.module.exit_json(msg=message,changed=self.changed)
        sglistafter = self.conn.provisioning.get_storage_group_list()
        facts = ({'storagegroups': sglistafter, 'message': message})
        result = {'state': 'info', 'changed': self.changed}
        self.module.exit_json(ansible_facts={'storagegroup_detail': facts},
                              **result)

    def apply_module(self):
        if self.module.params["parent_state"] == 'present' and \
                self.module.params["child_state"] == 'in_parent':
            self.create_cascaded()
        elif self.module.params["parent_state"] == 'present' and \
                self.module.params["child_state"] == 'not_in_parent':
            self.remove_child_sg()
        elif self.module.params["parent_state"] == 'absent':
            self.delete_sg()

def main():
    d = DellEmcCascadeStorageGroup()
    d.apply_module()


if __name__ == '__main__':
    main()