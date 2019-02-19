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
short_description: "Simple Module to Modify Volumes that are part of a 
Strorage group on Dell EMC PowerMax or VMAX All Flash Arrays"
version_added: "2.8"
description:
  - "Module can be used to remove of modify a list of volumes from storage 
  group.  This module assumes code level 5978 or higher, volumes can not be 
  part of an SRDF Metro configuration, this restriction may be lifted in a later 
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
  newcap_gb:
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
- name: Provision Storage For DB Cluster
  hosts: localhost
  connection: local
  vars_files:
    - vars.yml
    
  tasks:
  - name: Modify Volume Sizes and Labels
    dellemc_pmax_volume:
        unispherehost: "{{unispherehost}}"
        universion: "{{universion}}"
        verifycert: "{{verifycert}}"
        user: "{{user}}"
        password: "{{password}}"
        array_id: "{{array_id}}"
        sgname: 'Ansible_SG'
        in_sg: "Present"
        volumes:
          - device_id: "000BB"
            cap_gb: 5
            vol_name: "LABEL"
          - device_id: "000BA"
            cap_gb: 5
            vol_name: "LABEL"
  - debug: var=storagegroup_detail

'''
RETURN = '''
ok: [localhost] => {
    "storagegroup_detail": {
        "message": "Volume resized .No changes made to Volume names",
        "sg_volumes": [
            {
                "cap_gb": 5.0,
                "vol_name": "LABEL",
                "volumeId": "000BA",
                "wwn": "60000970000197600156533030304241"
            },
            {
                "cap_gb": 5.0,
                "vol_name": "LABEL",
                "volumeId": "000BB",
                "wwn": "60000970000197600156533030304242"
            },
            {
                "cap_gb": 1.0,
                "vol_name": "DATA",
                "volumeId": "000BC",
                "wwn": "60000970000197600156533030304243"
            },
            {
                "cap_gb": 1.0,
                "vol_name": "DATA",
                "volumeId": "000BD",
                "wwn": "60000970000197600156533030304244"
            },
            {
                "cap_gb": 1.0,
                "vol_name": "REDO",
                "volumeId": "000BE",
                "wwn": "60000970000197600156533030304245"
            },
            {
                "cap_gb": 1.0,
                "vol_name": "REDO",
                "volumeId": "000BF",
                "wwn": "60000970000197600156533030304246"
            }
        ],
        "storagegroup_detail": {
            "VPSaved": "100.0%",
            "base_slo_name": "Diamond",
            "cap_gb": 6.01,
            "compression": true,
            "device_emulation": "FBA",
            "num_of_child_sgs": 0,
            "num_of_masking_views": 0,
            "num_of_parent_sgs": 0,
            "num_of_snapshots": 0,
            "num_of_vols": 6,
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


class DellEmcVolume(object):

    def __init__(self):
        self.argument_spec = dellemc_pmax_argument_spec()
        self. argument_spec.update(dict(
            volumes=dict(type='list', required=True),
            sgname=dict(type='str', required=True),
            in_sg=dict(type='str', choices=['present', 'absent'],
                       required=True)))
        self.module = AnsibleModule(argument_spec=self.argument_spec)
        self.conn = pmaxapi(self.module)

    def remove_volumes(self):
        changed = False
        playbook_luns = self.module.params["volumes"]
        playbook_volume_ids=[]
        for volume in playbook_luns:
            playbook_volume_ids.append(volume['device_id'])
        sglist = self.conn.provisioning.get_storage_group_list()
        message = "no changes made, check input parameters"
        # Check storage group exists
        if self.module.params['sgname'] in sglist:
            sg_vols = self.conn.provisioning.get_volume_list(filters={
                'storageGroupId': self.module.params['sgname']})
            result = set(sg_vols) >= set(playbook_volume_ids)
            # make sure all volumes are present in the storage group and that
            # deleting will not result in an empty storage group.
            if len(sg_vols) > len(playbook_volume_ids):
                if result:
                    for lun in playbook_volume_ids:
                        self.conn.provisioning.remove_vol_from_storagegroup(sg_id=self.module.params[
                            'sgname'], vol_id=lun)
                        message = "Volumes Successfully Removed"
                        changed = True
                else:
                    message = "Not All Volumes in the list provided are in " \
                              "storage group"
            elif not result:
                changed = False
                message = "Check your volume list, not all volumes provided are " \
                          "part of the specified storage group"
            elif len(sg_vols) == len(playbook_volume_ids):
                changed = False
                message = "Result will remove all volumes from SG"

        lunsummary = []
        for lun in sg_vols:
            lundetails = self.conn.provisioning.get_volume(lun)
            # sg_lun_detail_list.append(lundetails)
            sglun = {}
            sglun['volumeId'] = lundetails['volumeId']
            sglun['vol_name'] = lundetails['volume_identifier']
            sglun['cap_gb'] = lundetails['cap_gb']
            sglun['wwn'] = lundetails['effective_wwn']
            lunsummary.append(sglun)

        facts = ({'storagegroup_name': self.module.params['sgname'],
                  'storagegroup_detail': self.conn.provisioning.get_storage_group(
                      storage_group_name=self.module.params['sgname']),
                  'sg_volumes': lunsummary,
                  'message': message})
        result = {'state': 'info', 'changed': changed}

        self.module.exit_json(ansible_facts={'storagegroup_detail': facts}, **result)

    def modify_volume(self):
        changed = False
        message = ""
        # Get a list of all volumes in SG
        sg_vols = self.conn.provisioning.get_volume_list(filters={
            'storageGroupId': self.module.params['sgname']})
        for volume in self.module.params['volumes']:
            current_volume = self.conn.provisioning.get_volume(device_id=volume[
                    'device_id'])
            if current_volume['cap_gb'] < volume['cap_gb']:
                self.conn.provisioning.extend_volume(new_size=volume[
                    'cap_gb'],device_id=volume[
                    'device_id'])
                message = "Volume resized"
                changed = True
            # TODO add logic to add specific volumes.
            else:
                message = "Unable to resize all volumes specified, check input"
            # Checks to verify identifier matches the label
            if volume['vol_name'] == current_volume['volume_identifier']:
                message = message + " .No changes made to Volume names"
            else:
                self.conn.provisioning.rename_volume(device_id=volume[
                    'device_id'], new_name=volume[
                    'vol_name'])
                message = message + " labels have changed"
                changed = True

        lunsummary = []
        for lun in sg_vols:
            lundetails = self.conn.provisioning.get_volume(lun)
            # sg_lun_detail_list.append(lundetails)
            sglun = {}
            sglun['volumeId'] = lundetails['volumeId']
            sglun['vol_name'] = lundetails['volume_identifier']
            sglun['cap_gb'] = lundetails['cap_gb']
            sglun['wwn'] = lundetails['effective_wwn']
            lunsummary.append(sglun)

        facts = ({'storagegroup_name': self.module.params['sgname'],
                  'storagegroup_detail': self.conn.provisioning.get_storage_group(
                      storage_group_name=self.module.params['sgname']),
                  'sg_volumes': lunsummary,
                  'message': message})
        result = {'state': 'info', 'changed': changed}

        self.module.exit_json(ansible_facts={'storagegroup_detail': facts}, **result)

    def apply_module(self):
        if self.module.params['in_sg'] == 'absent':
            self.remove_volumes()

        elif self.module.params['in_sg'] == 'present':
            self.modify_volume()


def main():
    d = DellEmcVolume()
    d.apply_module()


if __name__ == '__main__':
    main()
