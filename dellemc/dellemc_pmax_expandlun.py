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
short_description: "Expand Volume on Dell EMC PowerMax or VMAX All
Flash"
version_added: "2.8"
description:
  - "This module assumes code level 5978 or higher, volums can not be part 
  of an SRDF Metro configuration, this restriction may be lifted in a later 
  release. This module has been tested against UNI 9.0. Every effort has 
  been made to verify the scripts run with valid input. These modules are a 
  tech preview."
module: dellemc_pmax_expandlun
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
  newsizegb:
    description:
      - "Integer value for the size of volumes In GB. Must be greater than
      volumes existing size."
    required: true
  device_id:
    description:
      - "Hexidecimal lun ID for VMAX or PowerMax Volume to be Expanded"
    required: true
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
    - name: "Create New Storage Group and add data volumes"
      dellemc_pmax_createsg:
        array_id: "{{array_id}}"
        cap_unit: GB
        num_vols: 1
        password: "{{password}}"
        sgname: "{{sgname}}"
        slo: Diamond
        srp_id: SRP_1
        unispherehost: "{{unispherehost}}"
        universion: "{{universion}}"
        user: "{{user}}"
        verifycert: "{{verifycert}}"
        vol_size: 1
        workload: None
        volumeIdentifier: 'REDO'
'''
RETURN = '''
dellemc_pmax_createsg:
    description: Information about storage group created
    returned: success
    type: dict
    sample: '{
        "vol_detail": {
        "allocated_percent": 0,
        "cap_cyl": 1639,
        "cap_gb": 3.0,
        "cap_mb": 3073.0,
        "effective_wwn": "60000970000197600156533030313341",
        "emulation": "FBA",
        "encapsulated": false,
        "has_effective_wwn": false,
        "num_of_front_end_paths": 0,
        "num_of_storage_groups": 1,
        "pinned": false,
        "reserved": false,
        "snapvx_source": false,
        "snapvx_target": false,
        "ssid": "FFFFFFFF",
        "status": "Ready",
        "storageGroupId": [
            "Ansible_SG"
        ],
        "type": "TDEV",
        "volumeId": "0013A",
        "volume_identifier": "DATA",
        "wwn": "60000970000197600156533030313341"
                }
        }'
'''
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.dellemc import dellemc_pmax_argument_spec, pmaxapi


def main():
    changed = False
    argument_spec = dellemc_pmax_argument_spec()
    argument_spec.update(dict(
            device_id=dict(type='str', required=True),
            newsizegb = dict(type='int', required=True)
        )
    )
    module = AnsibleModule(argument_spec=argument_spec)
    # Setup connection to API and import  modules.
    conn = pmaxapi(module)
    dellemc = conn.provisioning
    if dellemc.get_volume(device_id=module.params[
            'device_id'])['cap_gb'] < module.params[
            'newsizegb']:
        dellemc.extend_volume(new_size=module.params[
            'newsizegb'],device_id=module.params[
            'device_id'])
        changed = True
    else:
        module.exit_json(msg="new volume size must be greater "
                             "than current size", changed=changed)

    facts = dellemc.get_volume(device_id=module.params[
            'device_id'])
    result = {'state': 'info', 'changed': changed}
    module.exit_json(ansible_facts={'vol_detail': facts}, **result)

if __name__ == '__main__':
    main()


