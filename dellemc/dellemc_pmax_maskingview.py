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
short_description: "Create a new masking view on Dell EMC PowerMax or VMAX All
Flash"
version_added: "2.8"
description:
  - "This module has been tested against UNI 9.0. Every effort has been made
  to verify the scripts run with valid input. These modules are a tech preview"
module: dellemc_pmax_createmaskingview
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
  sgname:
    description:
      - "32 Character string representing storage group name"
  host_or_cluster:
    description:
      - "Host or Cluster Name, Unique 32 Character string representing
      masking"
  maskingview_name:
    description:
      - "32 Character string representing masking view name, name must not
      already be in use"

requirements:
  - Ansible
  - "Unisphere for PowerMax version 9.0 or higher."
  - "VMAX All Flash, VMAX3, or PowerMax storage Array."
  - "PyU4V version 3.0.0.8 or higher using PIP python -m pip install PyU4V"
'''
EXAMPLES = '''
---
- name: "Create a Masking View from existing components"
  connection: local
  hosts: localhost
  vars_files:
    - vars.yml
  tasks:
    - name: "Create Masking View for Host Access to storage group volumes"
      dellemc_pmax_createmaskingview:
        array_id: "{{array_id}}"
        password: "{{password}}"
        unispherehost: "{{unispherehost}}"
        universion: "{{universion}}"
        user: "{{user}}"
        verifycert: "{{verifycert}}"
        sgname: "{{sgname}}"
        portgroup_id: "Ansible_PG"
        host_or_cluster : "AnsibleCluster"
        maskingview_name: "Ansible_MV"
        state: present
'''
RETURN = r'''
'''
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.dellemc import dellemc_pmax_argument_spec, pmaxapi


class DellEmcPmaxMaskingview(object):

    def __init__(self):
        self.argument_spec = dellemc_pmax_argument_spec()
        self.argument_spec.update(dict(
            sgname=dict(type='str', required=True),
            host_or_cluster=dict(type='str', required=True),
            portgroup_id=dict(type='str', required=True),
            maskingview_name=dict(type='str', required=True),
            state=dict(type='str', choices=['present', 'absent'],
                       required=True)
        )
        )

        self.module = AnsibleModule(argument_spec=self.argument_spec)

        self.conn = pmaxapi(self.module)

    def create_maskingview(self):
        changed = False
        mv_details = "Nothing to display"
        # Check Masking
        try:
            self.conn.provisioning.create_masking_view_existing_components(
                        port_group_name=self.module.params['portgroup_id'],
                        masking_view_name=self.module.params['maskingview_name'],
                        host_name=self.module.params['host_or_cluster'],
                        storage_group_name=self.module.params['sgname'])
            changed = True
            message = "Masking view successfully created"
            mv_details = self.conn.provisioning.get_masking_view(
                masking_view_name=self.module.params[
                                                      'maskingview_name'])

        except Exception:
            message = "Error Creating Masking view rerun playbook with -vvv to " \
                      "check error message"
        facts = ({'message': message,
                  'mv_details': mv_details})
        result = {'state': 'info', 'changed': changed}
        self.module.exit_json(ansible_facts={'maskingview_detail': facts},
                          **result)

    def delete_maskingview(self):
        changed = False
        mv_details = ""
        message = ""
        try:
            self.conn.provisioning.delete_masking_view(
                maskingview_name=self.module.params['maskingview_name'])
            changed = True
        except Exception:
            message = "Unable to Delete the specified Masking view"
        facts = ({'message': message,
                  'mv_details': mv_details})
        result = {'state': 'info', 'changed': changed}
        self.module.exit_json(ansible_facts={'maskingview_detail': facts},
                          **result)

    def apply_module(self):
        if self.module.params['state'] == "present":
            self.create_maskingview()
        elif self.module.params['state'] == 'absent':
            self.delete_maskingview()


def main():

    d = DellEmcPmaxMaskingview()
    d.apply_module()


if __name__ == '__main__':
    main()
