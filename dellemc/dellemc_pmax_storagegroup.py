#!/usr/bin/python
# Copyright: (C) 2018, DellEMC
# Author(s): Paul Martin <paule.martin@dell.com>
# GNU General Public License v3.0+ (see COPYING
# or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from itertools import groupby

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
---
- name: "Provision a new storage group"
  hosts: localhost
  connection: local
  gather_facts: no
  vars_files:
    - vars.yml
  vars:
    lun_request:
      # Each item will be treated as a request for volumes of the same size
      # volume name must be unique per request, all sizes are GB values.  A
      # request can have multiple volumes with the same name, however module
      # will not run if it detects two requests with same name.  This is self
      # imposed restriction to make idempotence easier for change tracking.
      - num_vols: 2
        cap_gb: 2
        vol_name: "DATA"
      - num_vols: 3
        cap_gb: 2
        vol_name: "REDO"
  tasks:
    - name: "Create New Storage Group volumes"
      dellemc_pmax_storagegroup:
        array_id: "{{array_id}}"
        password: "{{password}}"
        unispherehost: "{{unispherehost}}"
        universion: "{{universion}}"
        user: "{{user}}"
        verifycert: "{{verifycert}}"
        sgname: "Ansible_SG"
        slo: "Diamond"
        luns: "{{lun_request}}"
        state: 'present'
        resize: True
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


class DellEmcStorageGroup(object):
    def __init__(self):
        self.argument_spec = dellemc_pmax_argument_spec()
        self.argument_spec.update(dict(
            sgname=dict(type='str', required=True),
            slo=dict(type='str', required=False),
            luns=dict(type='list', required=False),
            state=dict(type='str', choices=['present', 'absent','current'],
                       required=True),
            resize=dict(type='bool', required=False)
        )
        )

        self.module = AnsibleModule(argument_spec=self.argument_spec)

        self.conn = pmaxapi(self.module)

    def sg_lunlist(self):
        # Returns formatted list of luns currently in the storage group
        # specified in the module paramter sgname

        sg_lunlist = self.conn.provisioning.get_volume_list(
            filters={'storageGroupId': self.module.params['sgname']})

        lunsummary = []
        for lun in sg_lunlist:
            lundetails = self.conn.provisioning.get_volume(lun)
            sglun = {}
            sglun['volumeId'] = lundetails['volumeId']
            sglun['vol_name'] = lundetails['volume_identifier']
            sglun['cap_gb'] = lundetails['cap_gb']
            sglun['wwn'] = lundetails['effective_wwn']
            lunsummary.append(sglun)

        return lunsummary

    def canonicalize_dict(self, x):
        "Return a (key, value) list sorted by the hash of the key"
        return sorted(x.items(), key=lambda x: hash(x[0]))

    def unique_and_count(self, lst):
        "Return a list of unique dicts with a 'count' key added"
        grouper = groupby(sorted(map(self.canonicalize_dict, lst)))
        return [dict(k + [("count", len(list(g)))]) for k, g in grouper]

    def current_sg_config(self):
        # Helper function returns list of dictionary that can be used to
        # construct the list of volumes for changes or requests.
        sg_lunlist = self.conn.provisioning.get_volume_list(
            filters={'storageGroupId': self.module.params['sgname']})

        lunsummary = []
        for lun in sg_lunlist:
            lundetails = self.conn.provisioning.get_volume(lun)
            sglun = {}
            sglun['vol_name'] = lundetails['volume_identifier']
            sglun['cap_gb'] = int(lundetails['cap_gb'])
            lunsummary.append(sglun)

        current_config = self.unique_and_count(lunsummary)
        for i in current_config:
            i['num_vols']=i.pop('count')


        return current_config

    def create_sg(self):
        changed = False
        # Compile a list of existing storage groups.
        message = "no changes made"
        sglist = self.conn.provisioning.get_storage_group_list()
        if self.module.params["luns"]:
            playbook_lunlist = self.module.params["luns"]
        else:
            playbook_lunlist = []
        # Make sure there Volume Names are Unique in LUN List, if label is
        # repeated on multiple requests, module will exit.
        names = []
        for lun_request_name in playbook_lunlist:
            if lun_request_name['vol_name'] in names:
                self.module.exit_json(msg="Check format of volume request "
                                          "list, vol_name should be unique "
                                          "per "
                                          "request")
            else:
                names.append(lun_request_name['vol_name'])

        if self.module.params['sgname'] not in sglist:
            self.conn.provisioning.create_storage_group(
                srp_id="SRP_1",
                sg_id=self.module.params[
                    'sgname'],
                slo=self.module.params[
                    'slo'])
            changed = True
            message = "Empty Storage Group Created"
            if len(playbook_lunlist) > 0:
                for lun in playbook_lunlist:
                    self.conn.provisioning.add_new_vol_to_storagegroup(
                        sg_id=self.module.params['sgname'], cap_unit="GB",
                        num_vols=lun[
                            'num_vols'],
                        vol_size=lun['cap_gb'],
                        vol_name=lun['vol_name'])
                message = "New Storage Group Created and Volumes Added"
        # If the storage group exists, we need to check if the volumelist
        # matches what the user has in the playbook
        elif self.module.params['sgname'] in sglist and len(playbook_lunlist) \
                > 0:
            # Get list of volumes currently in the SG
            sg_lunlist = self.conn.provisioning.get_volume_list(
                filters={'storageGroupId': self.module.params['sgname']})
            sg_lun_detail_list = []
            for lun in sg_lunlist:
                lundetails = self.conn.provisioning.get_volume(lun)
                sg_lun_detail_list.append(lundetails)
            # Check if existing luns in SG match the request made in playbook
            # lunlist if there are enough volumes matching the size and type
            # volumes count and capacity will remain the same, if not the
            # volume count will be increased to match the request
            for lun_request in playbook_lunlist:
                # Assuming each list item is a unique request combination of
                # volume size and identifier/name
                existing_vols = 0
                for existinglun in sg_lun_detail_list:
                    if (existinglun['cap_gb'] == lun_request['cap_gb']) and (
                            existinglun['volume_identifier'] == lun_request[
                            'vol_name']):
                        existing_vols = existing_vols + 1
                if existing_vols < lun_request['num_vols']:
                    newvols = lun_request['num_vols'] - existing_vols
                    self.conn.provisioning.add_new_vol_to_storagegroup(
                        sg_id=self.module.params['sgname'], num_vols=newvols,
                        vol_size=lun_request['cap_gb'],
                        cap_unit="GB",
                        vol_name=lun_request['vol_name'])
                    message = "New Volumes Added to Storage Group"
                    changed = True
                elif existing_vols > lun_request['num_vols']:
                    message = "It looks like you are trying to remove " \
                              "volumes, please use dellemc_pmax_volume  " \
                              "supports create, add and show operations"

        # Volume Requests of Different sizes should have unique ID's

        lunsummary = self.sg_lunlist()

        facts = ({'storagegroup_name': self.module.params['sgname'],
                  'storagegroup_detail':
                      self.conn.provisioning.get_storage_group(
                          storage_group_name=self.module.params['sgname']),
                  'sg_volumes': lunsummary,
                  'message': message})
        result = {'state': 'info', 'changed': changed}

        self.module.exit_json(ansible_facts={'storagegroup_detail': facts},
                              **result)

    def resize_sg_vols(self):
        # Assumes volumes already exist in storage group.  Attempts to match
        # volume based on volume label.
        changed = False
        sglunlist = self.sg_lunlist()
        playbook_lunlist = self.module.params['luns']
        sglist = self.conn.provisioning.get_storage_group_list()
        # Catch in case user has set resize = true but still want to create
        # the group.
        if self.module.params['sgname'] not in sglist:
            self.create_sg()
        for playbook_request in playbook_lunlist:
            for existinglun in sglunlist:
                # checking list of luns each volume identifer will be
                # checked to see if it will be resized
                if playbook_request['vol_name'] == existinglun['vol_name'] \
                        and existinglun['cap_gb'] < playbook_request['cap_gb']:
                        self.conn.provisioning.extend_volume(
                            new_size=playbook_request['cap_gb'],
                            device_id=existinglun['volumeId'])
                        changed = True

        lunsummary = self.sg_lunlist()
        facts = ({'storagegroup_name': self.module.params['sgname'],
                  'storagegroup_detail':
                      self.conn.provisioning.get_storage_group(
                          storage_group_name=self.module.params['sgname']),
                  'sg_volumes': lunsummary,
                  'message': "Resize operation attempted, volumes state shown"
                             " below"})
        # Change Message
        result = {'state': 'info', 'changed': changed}
        self.module.exit_json(ansible_facts={'storagegroup_detail': facts},
                              **result)

    def delete_sg(self):
        changed = False
        # Compile a list of existing storage groups.
        sglist = self.conn.provisioning.get_storage_group_list()
        message = "Resource already in the requested state"
        if self.module.params['sgname'] in sglist:
            sgmaskingviews = \
                self.conn.provisioning.get_masking_views_from_storage_group(
                    storagegroup=self.module.params['sgname'])
            if len(sgmaskingviews) == 0:
                # Remove volume label name before deleting storage group
                lunlist = self.conn.provisioning.get_volume_list(filters={
                    'storageGroupId': self.module.params['sgname']})
                for lun in lunlist:
                    self.conn.provisioning._modify_volume(
                        device_id=lun, payload={
                                    "editVolumeActionParam": {
                                        "modifyVolumeIdentifierParam": {
                                            "volumeIdentifier": {
                                                "volumeIdentifierChoice":
                                                    "none"
                                            }
                                        }}})
                self.conn.provisioning.delete_storagegroup(
                    storagegroup_id=self.module.params['sgname'])
                changed = True
                message = "Delete Operation Completed"
            else:
                message = "Storage Group is Part of a Masking View"
        sglistafter = self.conn.provisioning.get_storage_group_list()
        facts = ({'storagegroups': sglistafter, 'message': message})
        result = {'state': 'info', 'changed': changed}
        self.module.exit_json(ansible_facts={'storagegroup_detail': facts},
                              **result)

    def apply_module(self):

        if self.module.params['state'] == 'absent':
            self.delete_sg()
        elif self.module.params['state'] == "current":
            self.current_sg_config()
        elif self.module.params['state'] == "present" and self.module.params[
                'resize']:
            self.resize_sg_vols()
        elif self.module.params['state'] == "present":
            self.create_sg()


def main():
    d = DellEmcStorageGroup()
    d.apply_module()


if __name__ == '__main__':
    main()
