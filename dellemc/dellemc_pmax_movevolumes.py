#!/usr/bin/python
# Copyright: (C) 2018, DellEMC
# Author(s): Julien Brusset <julien.brusset.prestataire@bpce-it.fr>
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
  - "Julien Brusset (@jbrt)"
short_description: "Move TDEVs from a Storage Group to another Storage Group (and 
delete source SG if needed as an option)"
version_added: "2.8"
description:
  - "This module has been tested against UNI 9.0. Every effort has been made
  to verify the scripts run with valid input. These modules are a tech preview."
module: dellemc_pmax_movevolumes
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
    sg_source: "SG_TEST"
    sg_target: "SG_TARGET"
    delete_source: false
    force: true

  tasks:
    - name: "Base Values for Task Add module Specific parameters"
      dellemc_pmax_movevolumes:
        unispherehost: "{{unispherehost}}"
        universion: "{{universion}}"
        array_id: "{{array_id}}"
        user: "{{user}}"
        password: "{{password}}"
        verifycert: "{{verifycert}}"
        sg_source: "{{ sg_source }}"
        sg_target: "{{ sg_target }}"
        delete_source: "{{ delete_source }}"
        force: "{{ force }}"
'''
RETURN = ''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.dellemc import dellemc_pmax_argument_spec, pmaxapi


def main():
    changed = False
    argument_spec = dellemc_pmax_argument_spec()
    argument_spec.update(dict(
        sg_source=dict(type='str', required=True),
        sg_target=dict(type='str', required=True),
        force=dict(type='bool', required=True),
        delete_source=dict(type='bool', required=False, default=False)
    ))
    module = AnsibleModule(argument_spec=argument_spec)
    # Setup connection to API and import  modules.
    conn = pmaxapi(module)
    pmax_prov = conn.provisioning

    sg_source = module.params['sg_source']
    sg_target = module.params['sg_target']
    delete_source = module.params['delete_source']

    # Compile a list of existing storage groups
    # Test if source and target storage groups exists
    sg_list = pmax_prov.get_storage_group_list()
    if sg_source not in sg_list:
        module.fail_json(msg=f'SG {sg_source} not exists')
    if sg_target not in sg_list:
        module.fail_json(msg=f'SG {sg_target} not exists')

    volumes_source = pmax_prov.get_vols_from_storagegroup(sg_source)
    volumes_target = pmax_prov.get_vols_from_storagegroup(sg_target)
    output_message = f'TDEV {",".join(volumes_source)} moved from {sg_source} ' \
                     f'to {sg_target}'

    # Check if some TDEVs are already in the target SG. If yes, updating the
    # move list with the remaining TDEVs
    intersection = set(volumes_source).intersection(set(volumes_target))
    if intersection:
        volumes_source = set(volumes_source).difference(set(volumes_source))
        output_message = f'Moved only TDEV {volumes_source} to {sg_target}, ' \
                         f'TDEVs {intersection} alrealdy in {sg_target}'

    # If there is still have TDEVs to move, move them
    if volumes_source:
        pmax_prov.move_volumes_between_storage_groups(device_ids=volumes_source,
                                                      source_storagegroup_name=sg_source,
                                                      target_storagegroup_name=sg_target,
                                                      force=module.params['force'])
        changed = True
        if delete_source:
            pmax_prov.delete_storagegroup(storagegroup_id=sg_source)
            output_message += f' (source SG {sg_source} deleted)'

        module.exit_json(changed=changed, output=output_message)

    # Even if there is no TDEVs to move exit without error
    module.exit_json(output=f'Nothing to move from {sg_source} to {sg_target} or '
                            f'TDEVs already in the target SG')


if __name__ == '__main__':
    main()
