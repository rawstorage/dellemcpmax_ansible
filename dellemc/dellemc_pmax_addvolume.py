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
short_description: "Create storage group on Dell EMC PowerMax or VMAX All
Flash"
version_added: "2.8"
description:
  - "This module has been tested against UNI 9.0. Every effort has been made
  to verify the scripts run with valid input. These modules are a tech preview"
module: dellemc_pmax_addvolume
options:
  array_id:
    description:
      - "Integer 12 Digit Serial Number of PowerMAX or VMAX array."
    required: true
  cap_unit:
    choices:
      - GB
      - TB
      - MB
      - CYL
    description:
      - "String value, default is set to GB"
    default: GB
  num_vols:
    description:
      - "integer value for the number of volumes. Minimum is 1, module will
      fail if less than one volume is specified or value is 0. If volumes are
      required of different sizes, additional tasks should be added to
      playbooks to use M(dellemc_pmax_addvolume) module."
    required: true
  sgname:
    description:
      - "Storage Group name 32 Characters no special characters other than
      underscore."
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
  vol_size:
    description:
      - "Integer value for the size of volumes.  All volumes will be created
      with same size.  Use dellemc_pmax_addvol to add additional volumes if you
      require different sized volumes once storage group is created."
    required: true
  volumeIdentifier:
    description:
      - "String up to 64 Characters no special character other than
      underscore sets a label to make volumes easily identified on hosts can
      run Dell EMC inq utility command to see this label is  inq -identifier
      device_name"
    required: false
  user:
    description:
      - "Unisphere username"
  password:
    description:
      - "password for Unisphere user"
requirements:
  - Ansible
  - "Unisphere for PowerMax version 9.0 or higher."
  - "VMAX All Flash, VMAX3, or PowerMax storage Array."
  - "PyU4V version 3.0.0.8 or higher using PIP python -m pip install PyU4V"
'''
EXAMPLES = '''
---
- name: "Add volumes to existing storage group"
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
  - name: Add REDO Volumes to Storage Group
    dellemc_pmax_addvolume:
        unispherehost: "{{unispherehost}}"
        universion: "{{universion}}"
        verifycert: "{{verifycert}}"
        user: "{{user}}"
        password: "{{password}}"
        sgname: "{{sgname}}"
        array_id: "{{array_id}}"
        num_vols: 1
        vol_size:  2
        cap_unit: 'GB'
        volumeIdentifier: 'REDO'
  - debug: var=sg_volume_detail
'''
RETURN = '''
dellemc_pmax_createsg:
    description: Information about storage group created
    returned: success
    type: dict
    sample: '{
            "sg_volume_detail": {
        "new_volumes": [
            "00134"
        ],
        "storagegroup_name": "Ansible_SG"
    }
}

'''
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.dellemc import dellemc_pmax_argument_spec, pmaxapi


def main():
    changed = False
    argument_spec = dellemc_pmax_argument_spec()
    argument_spec.update(dict(
        sgname=dict(type='str', required=True),
        num_vols=dict(type='int', required=True),
        vol_size=dict(type='int', required=True),
        cap_unit=dict(type='str', default='GB', choices=['GB',
                                                         'TB',
                                                         'MB', 'CYL']),
        volumeIdentifier=dict(type='str', required=True)
    )
    )
    # Create Connection to Unisphere Server to Make REST calls
    # Setting connection shortcut to Provisioning modules to simplify code
    module = AnsibleModule(argument_spec=argument_spec)
    conn = pmaxapi(module)
    dellemc = conn.provisioning
    # Compile a list of existing storage groups.
    sglist = dellemc.get_storage_group_list()
    # Check if Storage Group already exists, if storage group does not exist
    # module will fail.
    if module.params['sgname'] not in sglist:
        module.fail_json(msg='Storage group does not Exist, Failing Task',
                         changed=changed)
    else:
        # If storage group exists module can proceed
        # Build a list of the existing volumes in the storage group
        sgvols_before = dellemc.get_volume_list(filters={
            'storageGroupId': module.params['sgname']})
        dellemc.add_new_vol_to_storagegroup(sg_id=module.params['sgname'],
                                            num_vols=module.params['num_vols'],
                                            cap_unit=module.params['cap_unit'],
                                            vol_size=module.params['vol_size'],
                                            vol_name=module.params[
                                                'volumeIdentifier'])
        changed = True
        # Build a list of volumes in storage group after being modified
        sgvols_after = dellemc.get_volume_list(filters={
            'storageGroupId': module.params['sgname']})
        newvols = (list(set(sgvols_after) - set(sgvols_before)))
        facts = ({'storagegroup_name': module.params[
            'sgname'],
                  'new_volumes': newvols
                  })
        result = {'state': 'info', 'changed': changed}
        module.exit_json(ansible_facts={'sg_volume_detail': facts},
                         **result)

if __name__ == '__main__':
    main()
