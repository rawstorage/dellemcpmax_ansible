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
short_description: "Template for creating Modules"
version_added: "2.8"
description:
  - "This module has been tested against UNI 9.0. Every effort has been made
  to verify the scripts run with valid input. These modules are a tech preview."
module: dellemc_pmax_create_snapshot
options:
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
  array_id:
    description:
      - "Integer 12 Digit Serial Number of PowerMAX or VMAX array."
    required: true
  sgname:
    description:
      - "Storage Group name 32 Characters no special characters other than
      underscore."
    required: true
  snapshotname:
    description:
      - "Storage Group name 32 Characters no special characters other than
      underscore."
    required: true
    type: str
  ttl:
    description:
      - "Automation expiration of snapshot, note snapshots that are linked
      will not expire until unlink has been performed."
    required: true
    type: int
  timeinhours:
    description:
      - "False will set expiration to days, true will mean expiration is in
      hours."
    type: bool
    required: true   
requirements:
  - Ansible
  - "Unisphere for PowerMax version 9.0 or higher."
  - "VMAX All Flash, VMAX3, or PowerMax storage Array."
  - "PyU4V version 3.0.0.8 or higher using PIP python -m pip install PyU4V"
'''
EXAMPLES = '''
---
- name: Create SnapVX SnapShot of existing Storage Group
  hosts: localhost
  connection: local
  vars:
        unispherehost: '192.168.1.123'
        universion: "90"
        verifycert: False
        user: 'smc'
        password: 'smc'

  tasks:
  - name: Create SnapShot
    dellemc_pmax_create_snapshot:
        unispherehost: "{{unispherehost}}"
        universion: "{{universion}}"
        verifycert: "{{verifycert}}"
        user: "{{user}}"
        password: "{{password}}"
        sgname: 'Ansible_SG'
        array_id: '000197600156'
        ttl: 1
        snapshotname: 'Ansible_SnapShot_1'
        timeinhours: True
  - debug: var=snap_detail
'''
RETURN = '''
dellemc_pmax_createsg:
    description: Information about storage group created
    returned: success
    type: dict
    sample: '{
        "snap_detail": {
        "active_generations": [
            0,
            1,
            2,
            3,
            4,
            5,
            6,
            7
        ],
        "snapshotname": "Ansible_SnapShot_1",
        "storage_group": "Ansible_SG"
    }
}
'
'''
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.dellemc import dellemc_pmax_argument_spec, pmaxapi


def main():
    changed = False
    argument_spec = dellemc_pmax_argument_spec()
    argument_spec.update(dict(
            sgname=dict(type='str', required=True),
            ttl=dict(type='int', required=True),
            snapshotname=dict(type='str', required=True),
            timeinhours=dict(type='bool', required=True),
        )
    )
    # Make REST call to Unisphere Server and execute create snapshot.
    module = AnsibleModule(argument_spec=argument_spec)
    # Setup connection to API and import provisioning and replication modules.
    conn = pmaxapi(module)
    prov=conn.provisioning
    rep=conn.replication
    # Create a list of storage groups on the array.
    sglist=prov.get_storage_group_list()
    # Check Storage Group exist for snapshot to succeed.
    if module.params['sgname'] not in sglist:
        module.fail_json(msg='Storage Group Does Not Exist', changed=changed)
    else:
        rep.create_storagegroup_snap(sg_name=module.params['sgname'],
                                     snap_name=module.params[
                                         'snapshotname'],ttl=module.params[
            'ttl'],hours=module.params['timeinhours'])
        changed = True
    facts = ({'active_generations':rep
        .get_storagegroup_snapshot_generation_list(
        storagegroup_id=module.params['sgname'], snap_name=module.params[
            'snapshotname']),
        "storage_group": module.params['sgname'],
             'snapshotname':module.params['snapshotname']})
    result = {'state': 'info', 'changed': changed}
    module.exit_json(ansible_facts={'snap_detail': facts}, **result)



from ansible.module_utils.basic import *
from ansible.module_utils.urls import *

if __name__ == '__main__':
    main()
