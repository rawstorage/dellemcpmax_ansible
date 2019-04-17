#!/usr/bin/python
# Copyright (C) 2018 DellEMC
# Author(s): Paul Martin <paule.martin@dell.com>
# Author(s): Julien Brusset <julien.brusset.prestataire@bpce-it.fr>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.dellemc import dellemc_pmax_argument_spec, pmaxapi

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
  new_maskingview_name:
    description:
      - "32 Character string representing the new name of the masking view, 
      this name must not already be in use"
requirements:
  - Ansible
  - "Unisphere for PowerMax version 9.0 or higher."
  - "VMAX All Flash, VMAX3, or PowerMax storage Array."
  - "PyU4V version 3.0.0.10 or higher using PIP python -m pip install PyU4V"
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
    - name: "Rename Masking View"
      dellemc_pmax_createmaskingview:
        array_id: "{{array_id}}"
        password: "{{password}}"
        unispherehost: "{{unispherehost}}"
        universion: "{{universion}}"
        user: "{{user}}"
        verifycert: "{{verifycert}}"
        maskingview_name: "Ansible_MV"
        new_maskingview_name: "NewAnsible_MV"
        state: present
'''
RETURN = r'''
ok: [localhost] => {
    "maskingview_detail": {
        "message": "Masking view Ansible_MV successfully created",
        "mv_details": {
            "hostId": "AnsibleHost1",
            "maskingViewId": "Ansible_MV",
            "portGroupId": "AnsiblePG1",
            "storageGroupId": "AnsibleSG1"
        }
    }
}
'''


class DellEmcPmaxMaskingview(object):
    """
    Module for creating or deleting a Masking View
    """

    def __init__(self):
        self._argument_spec = dellemc_pmax_argument_spec()
        self._argument_spec.update(dict(
            sgname=dict(type='str', required=False),
            host_or_cluster=dict(type='str', required=False),
            portgroup_id=dict(type='str', required=False),
            maskingview_name=dict(type='str', required=True),
            new_maskingview_name=dict(type='str', required=False),
            state=dict(type='str', choices=['present', 'absent'], required=True)
        ))

        self._module = AnsibleModule(argument_spec=self._argument_spec)
        self._conn = pmaxapi(self._module)
        self._changed = False
        self._message = ''

        self._portgroup_id = self._module.params['portgroup_id']
        self._maskingview_name = self._module.params['maskingview_name']
        self._host_or_cluster = self._module.params['host_or_cluster']
        self._sgname = self._module.params['sgname']

    def create_maskingview(self):
        """
        Creating a Masking View
        :return: (None)
        """
        try:
            self._conn.provisioning. \
                create_masking_view_existing_components(
                                        port_group_name=self._portgroup_id,
                                        masking_view_name=self._maskingview_name,
                                        host_name=self._host_or_cluster,
                                        storage_group_name=self._sgname)
            self._changed = True
            self._message = "Masking view {} successfully created".\
                            format(self._maskingview_name)

        except Exception as error:
            self._module.fail_json(msg="Check input parameters, Error Creating "
                                       "Masking view: {}".format(error))

    def delete_maskingview(self):
        """
        Deleting a Masking View
        :return: (None)
        """
        try:
            self._conn.provisioning.\
                delete_masking_view(maskingview_name=self._maskingview_name)
            self._changed = True
            self._message = "Masking view {} successfully deleted".\
                            format(self._maskingview_name)

        except Exception as error:
            self._module.fail_json(msg="Unable to Delete the specified Masking"
                                       " view: {}".format(error))

    def _rename_maskingview(self):
        """
        Renaming an existing Masking View
        :return: None
        """
        try:
            if self._maskingview_name not in self._conn.provisioning.get_masking_view_list():
                self._module.fail_json(msg="Masking View {} doesn't exists".
                                           format(self._maskingview_name))

            self._conn.provisioning. \
                rename_masking_view(masking_view_id=self._maskingview_name,
                                    new_name=self._module.params['new_maskingview_name'])
            self._changed = True
            # Updating maskingview_name to be consistent with the next facts gathering
            self._maskingview_name = self._module.params['new_maskingview_name']
            self._message = "Masking View renamed to {}".format(self._maskingview_name)

        except Exception as error:
            self._module.fail_json(msg="Unable to rename Masking View ({})".
                                       format(error))

    def apply_module(self):
        """
        Masking View logic
        :return: (None)
        """
        facts = {}

        # Case 1 - Create a masking view
        if self._module.params['state'] == "present":
            # If we want to rename MV, this operation will done in first
            # place and will be exclusive
            if self._module.params['new_maskingview_name']:
                self._rename_maskingview()
                facts = ({'message': self._message,
                          'mv_details': self._conn.provisioning.
                          get_masking_view(masking_view_name=self._maskingview_name)})

            else:
                # Check if MaskingView exists
                if self._maskingview_name in \
                        self._conn.provisioning.get_masking_view_list():
                    facts = ({'message': "MaskingView {} already "
                                         "exists".format(self._maskingview_name)})
                # If not, create it
                else:
                    self.create_maskingview()
                    facts = ({'message': self._message,
                              'mv_details': self._conn.provisioning.
                              get_masking_view(masking_view_name=self._maskingview_name)})

        # Case 2 - Delete an existing masking view
        elif self._module.params['state'] == "absent":
            self.delete_maskingview()
            facts = ({'message': self._message})

        result = {'state': 'info', 'changed': self._changed}
        self._module.exit_json(ansible_facts={'maskingview_detail': facts}, **result)


def main():
    """
    Main function
    :return:
    """
    DellEmcPmaxMaskingview().apply_module()


if __name__ == '__main__':
    main()