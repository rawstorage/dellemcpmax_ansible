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
module: dellemc_pmax_storagegroup
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
      - "List describing volumes to be added or list of luns expected to be 
      in the storage group. list should have a unique combination of 
      num_vols, vol_size, vol_name. See examples for usage"
    type: list
    required: false
    Default: empty list which will try to create storage group with no volumes 
  state:
    description:
      - "Valid values are present, absent, or current"
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
      - num_vols: 2
        vol_size: 1
        vol_name: "DATA"
      - num_vols: 2
        vol_size: 1
        vol_name: "REDO"

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
        state: present
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
        state: "absent"
    - debug: var=storagegroup_detail
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


def create_sg(apiconnection, module):
    dellemc = apiconnection
    changed = False
    newvols = 0
    # Compile a list of existing storage groups.
    message = "no changes made"
    sglist = dellemc.get_storage_group_list()
    if module.params["luns"]:
        playbook_lunlist = module.params["luns"]
    else:
        playbook_lunlist = []
    if module.params['sgname'] not in sglist:
        dellemc.create_storage_group(srp_id="SRP_1",
                                     sg_id=module.params['sgname'],
                                     slo=module.params['slo'])

        changed = True
        message = "Empty Storage Group Created"
        if len(playbook_lunlist) > 0:
            for lun in playbook_lunlist:
                dellemc.add_new_vol_to_storagegroup(sg_id=module.params[
                    'sgname'], cap_unit="GB",
                                                    num_vols=lun[
                                                        'num_vols'],
                                                    vol_size=lun['vol_size'],
                                                    vol_name=lun['vol_name'])
            message = "New Storage Group Created and Volumes Added"
    # If the storage group exists, we need to check if the volumelist
    # matches what the user has in the playbook
    elif module.params['sgname'] in sglist and len(playbook_lunlist) > 0:
        # Get list of volumes currently in the SG
        sg_lunlist = dellemc.get_volume_list(
            filters={'storageGroupId': module.params['sgname']})
        sg_lun_detail_list = []
        for lun in sg_lunlist:
            lundetails = dellemc.get_volume(lun)
            sg_lun_detail_list.append(lundetails)
        # Check if existing luns in SG match the request made in playbook
        # lunlist if there are enough volumes matching the size and type
        # volumes count and capacity will remain the same, if not the volume
        #  count will be increased to match the request
        for lun_request in playbook_lunlist:
            # Assuming each list item is a unique request combination of
            # volume size and identifier/name
            existing_vols = 0
            for existinglun in sg_lun_detail_list:
                if (existinglun['cap_gb'] == lun_request['vol_size']) and (
                        existinglun['volume_identifier'] == lun_request['vol_name']):
                    existing_vols = existing_vols + 1
            if existing_vols < lun_request['num_vols']:
                newvols = lun_request['num_vols'] - existing_vols
                dellemc.add_new_vol_to_storagegroup(sg_id=module.params['sgname'],
                                                    num_vols=newvols,
                                                    vol_size=lun_request['vol_size'],
                                                    cap_unit="GB",
                                                    vol_name=lun_request['vol_name'])
                message = "New Volumes Added to Storage Group"
                changed = True
            elif existing_vols > lun_request['num_vols']:
                message = "It looks like you are trying to remove volumes, " \
                          "please use dellemc_pmax_volume module for this " \
                          "operation, this module only supports create, " \
                          "add and show operations"

    # TODO add logic for capturing and dealing with resize operations.

    sg_lunlist = dellemc.get_volume_list(
            filters={'storageGroupId': module.params['sgname']})

    lunsummary = []
    for lun in sg_lunlist:
        lundetails = dellemc.get_volume(lun)
        # sg_lun_detail_list.append(lundetails)
        sglun = {}
        sglun['volumeId'] = lundetails['volumeId']
        sglun['vol_name'] = lundetails['volume_identifier']
        sglun['cap_gb'] = lundetails['cap_gb']
        sglun['wwn'] = lundetails['effective_wwn']
        lunsummary.append(sglun)

    facts = ({'storagegroup_name': module.params['sgname'],
              'storagegroup_detail': dellemc.get_storage_group(
                  storage_group_name=module.params['sgname']),
              'sg_volumes': lunsummary,
              'message': message})
    result = {'state': 'info', 'changed': changed}

    module.exit_json(ansible_facts={'storagegroup_detail': facts}, **result)


def delete_sg(apiconnection, module):
    dellemc = apiconnection
    changed = False
    # Compile a list of existing storage groups.
    sglist = dellemc.get_storage_group_list()
    message = "Resource already in the requested state"
    if module.params['sgname'] in sglist:
        sgmaskingviews = dellemc.get_masking_views_from_storage_group(
            storagegroup=module.params['sgname'])
        if len(sgmaskingviews) == 0:
            # Remove volume label name before deleting storage group
            lunlist=dellemc.get_volume_list(filters={'storageGroupId': module.params['sgname']})
            for lun in lunlist:
                dellemc._modify_volume(device_id=lun, payload={
                    "editVolumeActionParam": {
                        "modifyVolumeIdentifierParam": {
                            "volumeIdentifier": {
                                "volumeIdentifierChoice": "none"
                            }
                        }
                    }
                })
            dellemc.delete_storagegroup(storagegroup_id=module.params['sgname'])
            changed = True
            message = "Delete Operation Completed"
        else:
            message = "Storage Group is Part of a Masking View, please check " \
                    "before retrying"
    sglistafter = dellemc.get_storage_group_list()
    facts = ({'storagegroups': sglistafter, 'message': message})
    result = {'state': 'info', 'changed': changed}
    module.exit_json(ansible_facts={'storagegroup_detail': facts}, **result)


def main():
    argument_spec = dellemc_pmax_argument_spec()
    argument_spec.update(dict(
        sgname=dict(type='str', required=True),
        srp_id=dict(type='str', required=False),
        slo=dict(type='str', required=False),
        luns=dict(type='list', required=False),
        state=dict(type='str', choices=['present', 'absent'],
                   required=True)
    ))
    module = AnsibleModule(argument_spec=argument_spec)
    # Setup connection to API and import provisioning modules.
    conn = pmaxapi(module)
    dellemc = conn.provisioning

    if module.params['state'] == "present":
        create_sg(apiconnection=dellemc, module=module)

    elif module.params['state'] == "absent":
        delete_sg(apiconnection=dellemc, module=module)


if __name__ == '__main__':
    main()
