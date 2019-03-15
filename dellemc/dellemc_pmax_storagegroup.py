#!/usr/bin/python
# Copyright: (C) 2018, DellEMC
# Author(s): Paul Martin <paule.martin@dell.com>
# Author(s): Olivier Carminati <olivier.carminati@bpce-it.fr>
# Author(s): Julien Brusset <julien.brusset.prestataire@bpce-it.fr>
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
  - "Olivier Carminati (@ocarm)"
  - "Julien Brusset (@jbrt)"
short_description: "Storage group Control Module for Dell EMC PowerMax or 
VMAX All Flash Arrays, This module can create or delete storage groups and 
manipulate size and number of volumes given in volume requests list. volume 
removal is handled in dellemc_pmax_volume module, to build a requests list 
for an existing storage group you can run with an empty requests list and 
examine the return"

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
  no_compression:
    description:
      - "Set the compression on the Storage Group at creation time, 
      to disable compression set this to true"
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
      - "List of volume requests to be added or already in storage group. 
      Each request in the list provided should have a unique combination of 
      num_vols, cap_gb, vol_name. Volume Name should be unique to the 
      request. Increasing size or num_volumes on a volume request 
      would add or expand capacity for volumes in requests list.  If empty 
      list is provided current contents of storage group will be returned: See 
      examples for usage"
    type: list
    required: false
    Default: empty list which will try to create storage group with no volumes 
  state:
    description:
      - "Valid values are present, absent, or current. Present will create 
      storage group if it doesn't already exist, absent will attempt to 
      delete"
    type: string
    required: true

requirements:
  - Ansible
  - "Unisphere for PowerMax version 9.0 or higher."
  - "VMAX All Flash, VMAX3, or PowerMax storage Array."
  - "PyU4V version 3.0.0.9 or higher using PIP python -m pip install PyU4V"
'''
EXAMPLES = '''
#!/usr/bin/env ansible-playbook
---
- name: "Provision a new storage group"
  hosts: localhost
  connection: local
  gather_facts: no
  vars_files:
    - vars.yml
  vars:
    input: &uni_connection_vars
      array_id : "{{ array_id }}"
      password : "{{ password }}"
      unispherehost : "{{ unispherehost }}"
      universion : "{{ universion }}"
      user : "{{   user  }}"
      verifycert : "{{ verifycert }}"
# Each item will be treated as a request for volumes of the same size
# volume name must be unique per request, all sizes are GB values.  A
# request can have multiple volumes with the same name, however module
# will not run if it detects two requests with same name.  This is self
# imposed restriction to make idempotence easier for change tracking.
    lun_request :
      - num_vols : 1
        cap_gb: 4
        vol_name: "DATA"
      - num_vols: 1
        cap_gb: 2
        vol_name: "REDO"
      - num_vols: 1
        cap_gb: 3
        vol_name: "FRA"

  tasks:
  - name: "Create New Storage Group volumes"
    dellemc_pmax_storagegroup:
      <<: *uni_connection_vars
      sgname: "Ansible_SG"
      slo: "Diamond"
      luns: "{{ lun_request }}"
      compression: true
      state: present
#!/usr/bin/env ansible-playbook
---
- name: "Add Volumes storage group"
  hosts: localhost
  connection: local
  gather_facts: no
  vars_files:
    - vars.yml
  vars:
    input: &uni_connection_vars
      array_id : "{{ array_id }}"
      password : "{{ password }}"
      unispherehost : "{{ unispherehost }}"
      universion : "{{ universion }}"
      user : "{{   user  }}"
      verifycert : "{{ verifycert }}"
    lun_request :
    # num_vols for DATA has been increased to 2, new volume will be added of 
    # 4 GB with name DATA. 
      - num_vols : 2
        cap_gb: 4
        vol_name: "DATA"
      - num_vols: 1
        cap_gb: 2
        vol_name: "REDO"
      - num_vols: 1
        cap_gb: 3
        vol_name: "FRA"
    # A new 1 GB volume is to be added with Label TEMP
      - num_vols: 1
        cap_gb: 1
        vol_name: "TEMP"
  tasks:
  - name: "Modify Group volumes"
    dellemc_pmax_storagegroup:
      <<: *uni_connection_vars
      sgname: "Ansible_SG"
      slo: "Diamond"
      luns: "{{ lun_request }}"
      state: present
    tasks:
  - name: "Delete Storage Group"
    dellemc_pmax_storagegroup:
      <<: *uni_connection_vars
      sgname: "Ansible_SG"
      slo: "Diamond"
      luns: "{{ lun_request }}"
      state: absent

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
            slo=dict(type='str', choices=['Diamond', 'Platinum', 'Gold',
                                          'Silver', 'Bronze', 'None'],
                     required=True),
            luns=dict(type='list', required=False),
            state=dict(type='str', choices=['present', 'absent'],
                       required=True),
            no_compression=dict(type='bool', required=False)
        ))

        self.module = AnsibleModule(argument_spec=self.argument_spec)
        self.conn = pmaxapi(self.module)

    def change_service_level(self):
        """
        Change Service Level on existing Storage Group
        :return: Changed True or False
        """
        payload = {
            "editStorageGroupActionParam": {
                "editStorageGroupSLOParam": {
                    "sloId": self.module.params['slo']
                }
            }
        }
        try:
            self.conn.provisioning.\
                modify_storage_group(storagegroup=self.module.params['sgname'],
                                     payload=payload)
            changed = True

        except Exception:
            changed = False

        finally:
            return changed

    def sg_lunlist(self):
        """
        Get a list of volumes/luns in the storage group and return a list
        :return: formatted list of luns currently in the storage grou
        """
        sg_lunlist = self.conn.provisioning.get_volume_list(
            filters={'storageGroupId': self.module.params['sgname']})
        lunsummary = []
        if sg_lunlist:
            for lun in sg_lunlist:
                lundetails = self.conn.provisioning.get_volume(lun)
                sglun = {}
                sglun['volumeId'] = lundetails['volumeId']
                sglun['cap_gb'] = lundetails['cap_gb']
                sglun['wwn'] = lundetails['effective_wwn']
                if 'volume_identifier' in lundetails:
                    sglun['vol_name'] = lundetails['volume_identifier']
                else:
                    sglun['vol_name'] = "NO_LABEL"
                lunsummary.append(sglun)
        return lunsummary

    def canonicalize_dict(self, x):
        """
        :param x:
        :return: "Return a (key, value) list sorted by the hash of the key"
        """

        return sorted(x.items(), key=lambda x: hash(x[0]))

    def unique_and_count(self, lst):
        """
        :param lst:
        :return: list of unique dicts with a 'count' key added"
        """
        grouper = groupby(sorted(map(self.canonicalize_dict, lst)))
        return [dict(k + [("count", len(list(g)))]) for k, g in grouper]

    def current_sg_config(self):
        """
        Helper function returns list of dictionary that can be used to
        construct the list of volumes for changes or requests.
        :return: list of volume requests in SG in similar format to playbook
        input
        """
        lunsummary = []
        sglunlist = self.sg_lunlist()
        for lun in sglunlist:
            lundetails = self.conn.provisioning.get_volume(lun['volumeId'])
            sglun = {}
            sglun['vol_name'] = lundetails['volume_identifier']
            sglun['cap_gb'] = int(lundetails['cap_gb'])
            lunsummary.append(sglun)
        current_config = self.unique_and_count(lunsummary)
        for i in current_config:
            i['num_vols'] = i.pop('count')

        return current_config

    def create_sg(self):
        """
        Create SG if needed and exit module gracefully with changes
        :return:
        """
        changed = False
        message = "no changes made"
        sglist = self.conn.provisioning.get_storage_group_list()
        if self.module.params["luns"]:
            playbook_request = self.module.params["luns"]
        else:
            playbook_request = []
        # Make sure there Volume Names are Unique in LUN List, if label is
        # repeated on multiple requests, module will exit.
        names = []
        for lun_request_name in playbook_request:
            if lun_request_name['vol_name'] in names:
                self.module.exit_json(msg="Check format of volume request "
                                          "list, vol_name should be unique "
                                          "per "
                                          "request")
            else:
                names.append(lun_request_name['vol_name'])

        if self.module.params['sgname'] not in sglist:
            # In case of compressed SG requested, we put the compression flag
            # at ON. Warning: slo must be present for that option can works
            # (cf. PyU4V)
            if self.module.params['no_compression']:
                    self.conn.provisioning.create_storage_group(srp_id='SRP_1',
                                                                sg_id=
                                                                self.module.params[
                                                                    'sgname'],
                                                                slo=
                                                                self.module.params[
                                                                    'slo'],
                                                                do_disable_compression=self.module.params['no_compression'])
            else:
                self.conn.provisioning.create_storage_group(srp_id='SRP_1',
                                                            sg_id=
                                                            self.module.params[
                                                                'sgname'],
                                                            slo=
                                                            self.module.params[
                                                                'slo'])
            changed = True
            message = "Empty Storage Group Created"

            if playbook_request:
                for lun in playbook_request:
                    self.conn.provisioning.\
                        add_new_vol_to_storagegroup(sg_id=self.module.params['sgname'],
                                                    cap_unit="GB",
                                                    num_vols=lun['num_vols'],
                                                    vol_size=lun['cap_gb'],
                                                    vol_name=lun['vol_name'],
                                                    create_new_volumes=False)
                message = "New Storage Group Created and Volumes Added"
        # If the storage group exists, need to check if the volume
        # configuration and size matches the playbook
        elif self.module.params['sgname'] in sglist and playbook_request:
            message = self.check_volume_changes()

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

    def check_volume_changes(self):
        changed = False
        """
        Usually called on existing storage group and determines and makes
        changes per the lun request list supplied in the playbook
        :return: String Detailing Changes made.
        """
        message = "No Changes Made"
        changed = self.change_service_level()
        current = self.current_sg_config()

        sg_summary = self.conn.provisioning.get_storage_group(
                          storage_group_name=self.module.params['sgname'])

        if sg_summary['num_of_vols'] == 0 \
                and sg_summary['type'] == 'Standalone':

            for request in self.module.params['luns']:
                self.conn.provisioning.add_new_vol_to_storagegroup(
                    sg_id=self.module.params['sgname'],
                    cap_unit="GB",
                    num_vols=request['num_vols'],
                    vol_size=request['cap_gb'],
                    vol_name=request['vol_name'])

        sglunnames = []
        for lunname in current:
            sglunnames.append(lunname['vol_name'].upper())

        if len(current) > len(self.module.params['luns']):
            facts = ({'storagegroup_name': self.module.params['sgname'],
                      'storage_group_current_config': current,
                      'message': "Volume Requests must contain current "
                                 "config plus additional requests, "
                                 "operations on a subset of volumes not "
                                 "supported with this module."})
            result = {'state': 'info', 'changed': changed}

            self.module.exit_json(ansible_facts={'storagegroup_detail': facts},
                                  **result)

        for request in self.module.params['luns']:
            if request['vol_name'].upper() not in sglunnames:
                self.conn.provisioning.add_new_vol_to_storagegroup(
                    sg_id=self.module.params['sgname'],
                    cap_unit="GB",
                    num_vols=request['num_vols'],
                    vol_size=request['cap_gb'],
                    vol_name=request['vol_name'].upper())
                message = "Volumes Added"
                changed = True

            else:
                # Check to see if any current volume set needs to be changed.
                for currentlunset in current:
                    if request['vol_name'] == currentlunset['vol_name']:
                        if request['num_vols'] > currentlunset['num_vols'] \
                                and request['cap_gb'] == currentlunset[
                                'cap_gb']:
                            new_vols = request['num_vols'] - currentlunset[
                                'num_vols']
                            self.conn.provisioning.add_new_vol_to_storagegroup(
                                sg_id=self.module.params['sgname'],
                                cap_unit="GB",
                                num_vols=new_vols,
                                vol_size=request['cap_gb'],
                                vol_name=request['vol_name'])
                            message = message + "Volumes Added"
                            changed = True
                        elif request['num_vols'] == currentlunset[
                            'num_vols'] and \
                                request['cap_gb'] > currentlunset['cap_gb']:
                            self.resize_sg_vols(volname=request[
                                'vol_name'], newsize=request['cap_gb'])
                            message = "Capacity increased for volumes with " \
                                      "label " + request['vol_name']
                            changed = True
                        elif request['num_vols'] > currentlunset[
                            'num_vols'] and \
                                request['cap_gb'] > currentlunset['cap_gb']:
                            new_vols = request['num_vols'] - currentlunset[
                                'num_vols']
                            self.resize_sg_vols(volname=request[
                                'vol_name'], newsize=request['cap_gb'])
                            self.conn.provisioning.add_new_vol_to_storagegroup(
                                sg_id=self.module.params['sgname'],
                                cap_unit="GB",
                                num_vols=new_vols,
                                vol_size=request['cap_gb'],
                                vol_name=request['vol_name'])
                            changed = True
                            message = "volumes added and resized"
                        elif request['num_vols'] < currentlunset['num_vols']:
                            self.module.exit_json(msg="Module doesn't support "
                                                  "removing devices please "
                                                      "use volumes module "
                                                      "for this operation " +
                                                      str(currentlunset) +
                                                      "playbook is trying " +
                                                      str(request),
                                                  changed=changed)

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

    def resize_sg_vols(self, volname, newsize):
        """
        :param volname: identifier name for volume to be resized
        :param newsize: Requested size in GB.
        :return:
        """
        # Assumes volumes already exist in storage group.  Attempts to match
        # volume based on volume label.
        sglunlist = self.sg_lunlist()
        for existinglun in sglunlist:
                # checking list of luns each volume identifer will be
                # checked to see if it will be resized
            if volname == existinglun['vol_name']:
                self.conn.provisioning.\
                    extend_volume(new_size=newsize,
                                  device_id=existinglun['volumeId'])

    def delete_sg(self):
        """
        Delete Storage Group
        :return:
        """
        changed = False
        # Compile a list of existing storage groups.
        sglist = self.conn.provisioning.get_storage_group_list()
        message = "Resource already in the requested state"
        if self.module.params['sgname'] in sglist:
            sgmaskingviews = self.conn.provisioning.\
                get_masking_views_from_storage_group(
                    storagegroup=self.module.params['sgname'])

            if not sgmaskingviews:
                # Remove volume label name before deleting storage group
                lunlist = self.sg_lunlist()
                for lun in lunlist:
                    # Remove labels from devices before deleting to ensure
                    # they are valid for re-use.
                    self.conn.provisioning._modify_volume(
                        device_id=lun['volumeId'], payload={
                            "editVolumeActionParam": {
                                "modifyVolumeIdentifierParam": {
                                    "volumeIdentifier": {
                                        "volumeIdentifierChoice":
                                            "none"
                                    }
                                }},
                            "executionOption": "ASYNCHRONOUS"
                        })
                try:
                    self.conn.provisioning.delete_storagegroup(
                    storagegroup_id=self.module.params['sgname'])
                    changed = True
                    message = "Delete Operation Completed"
                except Exception:
                    message = "Unable to Delete Storage Group, check that it " \
                              "is not a child SG, use cascadedsg module to " \
                              "remove child from parent before delete"

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
        elif self.module.params['state'] == "present":
            self.create_sg()


def main():
    d = DellEmcStorageGroup()
    d.apply_module()


if __name__ == '__main__':
    main()
