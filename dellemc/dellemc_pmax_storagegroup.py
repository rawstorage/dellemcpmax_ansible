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
short_description: "Storage group Control Module for Dell EMC PowerMax or 
VMAX All Flash Arrays, can be used to show, create, delete, and add or
remove volumes"
version_added: "2.8"
description:
  - "This module has been tested against UNI 9.0. Every effort has been made
  to verify the scripts run with valid input. These modules are a tech preview."
module: dellemc_pmax_create_emptysg
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
  srp_id:
    description:
      - "Storage Resource Pool Name, Default is set to SRP_1, if your system
      has mainframe or multiple pools you can set this to a different value to
      match your environment."
    required: false
    type: str
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
      - "List describing volumes to be added or list of luns and volumes 
      to be removed from a storage group. Not Required for Show or Delete 
      actions. See examples for usage"
    type: list
    required: false
  action:
    description:
      - "create, add_volumes, remove_volumes, show, delete"
    type: string
    required: true
       
    
requirements:
  - Ansible
  - "Unisphere for PowerMax version 9.0 or higher."
  - "VMAX All Flash, VMAX3, or PowerMax storage Array."
  - "PyU4V version 3.0.0.8 or higher using PIP python -m pip install PyU4V"
'''
EXAMPLES = '''
---
- name: "Test Storage Group Operations"
  connection: local
  hosts: localhost
  vars:
    array_id: "000197600156"
    password: "smc"
    sgname: "Ansible_SG1"
    unispherehost: "192.168.1.1"
    universion: "90"
    user: "smc"
    verifycert: false
    lun_list:
      - cap_unit: "GB"
        num_vols: 2
        vol_size: 1
        vol_name: "DATA"
      - cap_unit: "GB"
        num_vols: 2
        vol_size: 1
        vol_name: "REDO"
    new_lun_list:
      - cap_unit: "GB"
        num_vols: 2
        vol_size: 1
        vol_name: "FRA"
      - cap_unit: "GB"
        num_vols: 2
        vol_size: 1
        vol_name: "TEMP"
    lun_removal_list:
      - "001A2"
  tasks:
    - name: "Create New Storage Group volumes"
      dellemc_pmax_storagegroup:
        array_id: "{{array_id}}"
        password: "{{password}}"
        sgname: "{{sgname}}"
        slo: "Diamond"
        srp_id: "SRP_1"
        unispherehost: "{{unispherehost}}"
        universion: "{{universion}}"
        user: "{{user}}"
        verifycert: "{{verifycert}}"
        luns: "{{lun_list}}"
        action: create
    - debug: var=storagegroup_detail    

    - name: "Add Storage Group volumes"
      dellemc_pmax_storagegroup:
        array_id: "{{array_id}}"
        password: "{{password}}"
        sgname: "{{sgname}}"
        slo: "Diamond"
        srp_id: "SRP_1"
        unispherehost: "{{unispherehost}}"
        universion: "{{universion}}"
        user: "{{user}}"
        verifycert: "{{verifycert}}"
        luns: "{{new_lun_list}}"
        action: "add_volumes"
    - debug: var=storagegroup_detail

    - name: "Show Storage Group"
      dellemc_pmax_storagegroup:
        array_id: "{{array_id}}"
        password: "{{password}}"
        sgname: "{{sgname}}"
        slo: "Diamond"
        srp_id: "SRP_1"
        unispherehost: "{{unispherehost}}"
        universion: "{{universion}}"
        user: "{{user}}"
        verifycert: "{{verifycert}}"
        action: "show"
    - debug: var=storagegroup_detail

    - name: "Remove volumes"
      dellemc_pmax_storagegroup:
        array_id: "{{array_id}}"
        password: "{{password}}"
        sgname: "{{sgname}}"
        slo: "Diamond"
        srp_id: "SRP_1"
        unispherehost: "{{unispherehost}}"
        universion: "{{universion}}"
        user: "{{user}}"
        verifycert: "{{verifycert}}"
        luns: "{{lun_remove_list}}"
        action: remove_volumes
    - debug: var=storagegroup_detail

    - name: "Delete Existing Storage Group"
      dellemc_pmax_storagegroup:
        array_id: "{{array_id}}"
        password: "{{password}}"
        sgname: "{{sgname}}"
        slo: "Diamond"
        srp_id: "SRP_1"
        unispherehost: "{{unispherehost}}"
        universion: "{{universion}}"
        user: "{{user}}"
        verifycert: "{{verifycert}}"
        action: "delete"
    - debug: var=storagegroup_detail
'''
RETURN = r'''
Create Storage Group
ok: [localhost] => {
    "storagegroup_detail": {
        "sg_volumes": [
            "001A2",
            "001A3",
            "001A4",
            "001A5"
        ],
        "storagegroup_name": "Ansible_SG1"
    }
}

Add Volumes to Strogae Group

ok: [localhost] => {
    "storagegroup_detail": {
        "message": "Operation Successful",
        "new_volumes": [
            "001AC",
            "001AB",
            "001AA",
            "001AD"
        ],
        "sgdetails": {
            "VPSaved": "100.0%",
            "base_slo_name": "Diamond",
            "cap_gb": 11.02,
            "compression": true,
            "device_emulation": "FBA",
            "num_of_child_sgs": 0,
            "num_of_masking_views": 0,
            "num_of_parent_sgs": 0,
            "num_of_snapshots": 0,
            "num_of_vols": 11,
            "service_level": "Diamond",
            "slo": "Diamond",
            "slo_compliance": "STABLE",
            "srp": "SRP_1",
            "storageGroupId": "Ansible_SG1",
            "type": "Standalone",
            "unprotected": true,
            "vp_saved_percent": 100.0
        },
        "storagegroup_name": "Ansible_SG1"
    }
}

Remove Volume

ok: [localhost] => {
    "storagegroup_detail": {
        "message": "Volumes Sucessfully Removed"
    }
}

Show Storage Group

*
ok: [localhost] => {
    "storagegroup_detail": {
        "message": "No changes made",
        "sgdetails": {
            "VPSaved": "100.0%",
            "base_slo_name": "Diamond",
            "cap_gb": 11.02,
            "compression": true,
            "device_emulation": "FBA",
            "num_of_child_sgs": 0,
            "num_of_masking_views": 0,
            "num_of_parent_sgs": 0,
            "num_of_snapshots": 0,
            "num_of_vols": 11,
            "service_level": "Diamond",
            "slo": "Diamond",
            "slo_compliance": "STABLE",
            "srp": "SRP_1",
            "storageGroupId": "Ansible_SG1",
            "type": "Standalone",
            "unprotected": true,
            "vp_saved_percent": 100.0
        },
        "volumes": [
            "001A3",
            "001A4",
            "001A5",
            "001A6",
            "001A7",
            "001A8",
            "001A9",
            "001AA",
            "001AB",
            "001AC",
            "001AD"
        ]
    }
}

Delete Stroage Group 

ok: [localhost] => {
    "storagegroup_detail": {
        "message": "Delete Operation Completed",
        "storagegroups": [
            "Child3_RM_1",
            "CriticalDatabase_1",
            "Demo_GK",
            "esx142_gks",
            "esx142_gks_1",
            "ESX_32_GKs",
            "ESXi_DEMO_SG",
            "FinanceOracle",
            "HSBC",
            "KMR-CSG",
            "Lab_GK",
            "MF_TEST",
            "MTS_ESX_28",
            "MTS_ESX_30",
            "MTS_ESX_32",
            "MTS_ESX_40",
            "MyMetroSG",
            "Pat_VdBench_1",
            "Pat_VdBench_2",
            "Pat_VdBench_3",
            "Pat_VdBench_4",
            "paul_csg2",
            "PM_DELL40_GK",
            "POC_Kit",
            "SRDF_TEST",
            "test1234",
            "Uniprod_MGMT"
        ]
    }
}


'''
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.dellemc import dellemc_pmax_argument_spec, pmaxapi


def create_sg(apiconnection, module):
    dellemc = apiconnection
    changed = False
    # Compile a list of existing storage groups.
    sglist = dellemc.get_storage_group_list()
    if module.params["luns"]:
        lunlist = module.params["luns"]
    else:
        lunlist = []
    if module.params['sgname'] not in sglist:
        dellemc.create_storage_group(srp_id='SRP_1',
                                     sg_id=module.params['sgname'],
                                     slo=module.params['slo'])
        changed = True
        if len(lunlist) > 0:
            for lun in lunlist:
                dellemc.add_new_vol_to_storagegroup(sg_id=module.params[
                    'sgname'], cap_unit=lun['cap_unit'],
                                                    num_vols=lun[
                                                        'num_vols'],
                                                    vol_size=lun['vol_size'],
                                                    vol_name=lun['vol_name'])
    facts = ({'storagegroup_name': module.params['sgname'],
              'sg_volumes':dellemc.get_volume_list(filters={
        'storageGroupId': module.params['sgname']})})
    result = {'state': 'info', 'changed': changed}

    module.exit_json(ansible_facts={'storagegroup_detail': facts}, **result)

def delete_sg(apiconnection, module):
    dellemc = apiconnection
    changed = False
    # Compile a list of existing storage groups.
    sglist = dellemc.get_storage_group_list()
    message="Resource already in the requested state"
    if module.params['sgname'] in sglist:
        sgmaskingviews = dellemc.get_masking_views_from_storage_group(
            storagegroup=module.params['sgname'])
        if len(sgmaskingviews)==0:
            dellemc.delete_storagegroup(storagegroup_id=module.params['sgname'])
            changed=True
            message = "Delete Operation Completed"
        else:
            message="Storage Group is Part of a Masking View, please check " \
                    "before retrying"
    sglistafter = dellemc.get_storage_group_list()
    facts = ({'storagegroups': sglistafter, 'message': message})
    result = {'state': 'info', 'changed': changed}
    module.exit_json(ansible_facts={'storagegroup_detail': facts}, **result)


def add_volumes(apiconnection, module):
    dellemc = apiconnection
    changed = False
    message = "Check input Parameters, Storage Group not found"
    sglist = dellemc.get_storage_group_list()
    newvols = []
    # Check if storage group exists before making changes
    if module.params['sgname'] in sglist:
        sgvols_before = dellemc.get_volume_list(filters={
            'storageGroupId': module.params['sgname']})
        if module.params["luns"]:
            lunlist = module.params["luns"]
            if len(lunlist) > 0:
                for lun in lunlist:
                    dellemc.add_new_vol_to_storagegroup(
                        sg_id=module.params['sgname'],
                        cap_unit=lun['cap_unit'],
                        num_vols=lun['num_vols'],
                        vol_size=lun['vol_size'],
                        vol_name=lun['vol_name'])
            changed = True
        sgvols_after = dellemc.get_volume_list(filters={
            'storageGroupId': module.params['sgname']})
        newvols = (list(set(sgvols_after) - set(sgvols_before)))
        message = "Operation Successful"
    facts = ({'message': message,'storagegroup_name': module.params['sgname'],
              'new_volumes': newvols, 'sgdetails': dellemc.get_storage_group(
        storage_group_name=module.params['sgname'])})
    result = {'state': 'info', 'changed': changed}
    module.exit_json(ansible_facts={'storagegroup_detail': facts}, **result)

def remove_volumes(apiconnection, module):
    dellemc = apiconnection
    changed = False
    lunlist = module.params["luns"]
    sglist = dellemc.get_storage_group_list()
    message = "no changes made, check input parameters"
    # Check storeage group exists
    if module.params['sgname'] in sglist:
        sg_vols = dellemc.get_volume_list(filters={
            'storageGroupId': module.params['sgname']})
        result = set(sg_vols) >= set(lunlist)
        # make sure all volumes are present in the storage group and that
        # deleting will not result in an empty storage group.
        if len(sg_vols) > len(lunlist):
            if result:
                for lun in lunlist:
                    dellemc.remove_vol_from_storagegroup(sg_id=module.params[
                        'sgname'], vol_id=lun)
                    message = "Volumes Sucessfully Removed"
                    changed = True
            else:
                message = "Not All Volumes in the list provided are in " \
                          "storage group"
    else:
        changed = False
        message = "Result will remove all volumes from SG"

    facts = ({'message': message})
    result = {'state': 'info', 'changed': changed}
    module.exit_json(ansible_facts={'storagegroup_detail': facts}, **result)

def show_storage_group (apiconnection, module):
    dellemc = apiconnection
    changed = False
    sglist = dellemc.get_storage_group_list()
    message = "No changes made"
    # Check storeage group exists
    sg_details = "nothing to display"
    sg_vols = []
    if module.params['sgname'] in sglist:
        sg_vols = dellemc.get_volume_list(filters={
            'storageGroupId': module.params['sgname']})
        sg_details =  dellemc.get_storage_group(
        storage_group_name=module.params['sgname'])
    else:
        changed = False
        message = "Stroage Group Name is not Valid, verify input " \
                      "parameters"
    facts = ({'message': message,
              'sgdetails': sg_details,
             'volumes': sg_vols})
    result = {'state': 'info', 'changed': changed}
    module.exit_json(ansible_facts={'storagegroup_detail': facts}, **result)

def main():
    argument_spec = dellemc_pmax_argument_spec()
    argument_spec.update(dict(
        sgname=dict(type='str', required=True),
        srp_id=dict(type='str', required=False),
        slo=dict(type='str', required=False),
        luns=dict(type='list', required=False),
        action=dict(type='str', choices=['create', 'add_volumes',
                                         'remove_volumes', 'delete', 'show'],
                                        required=True)
    ))
    module = AnsibleModule(argument_spec=argument_spec)
    # Setup connection to API and import provisioning modules.
    conn = pmaxapi(module)
    dellemc = conn.provisioning

    if module.params['action'] == "create":
        create_sg(apiconnection=dellemc, module=module)

    elif module.params['action'] == "show":
        show_storage_group(apiconnection=dellemc, module=module)

    elif module.params['action'] == "add_volumes":
        add_volumes(apiconnection=dellemc, module=module)

    elif module.params['action'] == "delete":
        delete_sg(apiconnection=dellemc, module=module)

    elif module.params['action'] == "remove_volumes":
        remove_volumes(apiconnection=dellemc, module=module)

if __name__ == '__main__':
    main()
