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
manipulate number of volumes given in volume requests list. volume 
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
  new_sgname:
    description:
      - "New Storage Group name 32 Characters no special characters other than
      underscore."
    required: false
  slo:
    description:
      - "Service Level for the storage group, Supported on VMAX3 and All Flash
      and PowerMAX NVMe Arrays running PowerMAX OS 5978 and above.  Default is
      set to Diamond, but user can override this by setting a different value."
    required: false
  compression:
    description:
      - "Set the compression on the Storage Group to create"
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
      Increasing size or num_volumes on a volume request 
      would add or expand capacity for volumes in requests list.  If empty 
      list is provided current contents of storage group will be returned: See 
      examples for usage"
    type: list
    required: false
    Default: empty list which will try to create storage group with no volumes 
  state:
    description:
      - "Valid values are present or  absent. Present will create 
      storage group if it doesn't already exist, absent will attempt to 
      delete"
    type: string
    required: true
requirements:
  - Ansible
  - "Unisphere for PowerMax version 9.0 or higher."
  - "VMAX All Flash, VMAX3, or PowerMax storage Array."
  - "PyU4V version 3.0.0.10 or higher using PIP python -m pip install PyU4V"
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
# , all sizes are GB values.
# A request can have multiple volumes with the same name, however module
# will only kept the last vol_name. This is self imposed restriction 
# to make idempotence easier for change tracking.
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
  - name: "Renaming SG"
    dellemc_pmax_storagegroup:
      <<: *uni_connection_vars
      sgname: "Ansible_SG"
      new_sgname: "NewAnsible_SG"
      slo: "Diamond"
      state: present
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
        "lun_request": [
            {
                "cap_gb": 1,
                "num_vols": 4
            },
            {
                "cap_gb": 2,
                "num_vols": 1
            }
        ],
        "message": [
            "SG Ansible_SG already exists",
            "SLO of SG Ansible_SG already Diamond",
            "1 volume(s) of 1 GB added"
        ],
        "sg_volumes": [
            {
                "cap_gb": 1.0,
                "vol_name": "REDO",
                "volumeId": "000DC",
                "wwn": "60000970000297800941533030304443"
            },
            {
                "cap_gb": 1.0,
                "vol_name": "REDO",
                "volumeId": "000DD",
                "wwn": "60000970000297800941533030304444"
            },
            {
                "cap_gb": 2.0,
                "vol_name": "DATA",
                "volumeId": "000DE",
                "wwn": "60000970000297800941533030304445"
            },
            {
                "cap_gb": 1.0,
                "vol_name": "REDO",
                "volumeId": "000DF",
                "wwn": "60000970000297800941533030304446"
            },
            {
                "cap_gb": 1.0,
                "vol_name": "REDO",
                "volumeId": "000E0",
                "wwn": "60000970000297800941533030304530"
            }
        ],
        "storagegroup_name": "Ansible_SG"
    }
}
'''
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.dellemc import dellemc_pmax_argument_spec, pmaxapi


def unique_and_count(lst):
    """
    :param lst:
    :return: list of unique dicts with a 'count' key added"
    """

    def canonicalize_dict(x):
        """
        Return a (key, value) list sorted by the hash of the key
        """
        return sorted(x.items(), key=lambda x: hash(x[0]))

    grouper = groupby(sorted(map(canonicalize_dict, lst)))
    return [dict(k + [("count", len(list(g)))]) for k, g in grouper]


class DellEmcStorageGroup(object):
    """
    Manipulating a Storage Group (creating, deleting, or modifying)
    """

    def __init__(self):
        self._argument_spec = dellemc_pmax_argument_spec()
        self._argument_spec.update(dict(
            sgname=dict(type='str', required=True),
            new_sgname=dict(type='str', required=False),
            slo=dict(type='str',
                     choices=['Diamond', 'Platinum', 'Gold',
                              'Silver', 'Bronze'],
                     required=False,
                     default=None),
            luns=dict(type='list', required=False),
            state=dict(type='str',
                       choices=['present', 'absent'],
                       required=True),
            no_compression=dict(type='bool', required=False)
        ))

        self._module = AnsibleModule(argument_spec=self._argument_spec)
        self._conn = pmaxapi(self._module)
        self._changed = False
        self._lun_request = []
        self._message = []
        self._sg_name = self._module.params['sgname']

        # Parsing the lun_request if exists
        if self._module.params['luns']:
            self._parsing_lun_request()

    def _parsing_lun_request(self):
        """
        Parsing the lun_request structure, aggregate duplicates if found
        :return: None
        """
        mapping = {}  # Will contains cap size as key (details as values)
        for g in self._module.params['luns']:
            # If this size of LUN has never seen before, we save it
            if g['cap_gb'] not in mapping:
                mapping[g['cap_gb']] = {'number': int(g['num_vols']),
                                        'name': g.get('vol_name', None)}

            # If this LUN size already seen
            # We have to add the number of LUNs to get the total number of
            # LUNs of that given size
            else:
                mapping[g['cap_gb']]['number'] += int(g['num_vols'])
                if 'vol_name' in g:
                    mapping[g['cap_gb']]['name'] = g['vol_name']

        # Dumping the final data structure into the target variable
        for lun_size in mapping:
            self._lun_request.append({'num_vols': mapping[lun_size]['number'],
                                      'cap_gb': lun_size,
                                      'vol_name': mapping[lun_size]['name']})

    def _get_sg_lun_list(self):
        """
        Get a list of volumes/luns in the storage group and return a list
        :return: formatted list of luns currently in the storage group
        """
        sg_lunlist = self._conn.provisioning.\
            get_volume_list(filters={'storageGroupId': self._sg_name})

        result = []
        if sg_lunlist:
            for lun in sg_lunlist:
                lun_details = self._conn.provisioning.get_volume(lun)
                sg_lun = {'volumeId': lun_details['volumeId'],
                          'cap_gb': lun_details['cap_gb'],
                          'wwn': lun_details['effective_wwn']}
                if 'volume_identifier' in lun_details:
                    sg_lun['vol_name'] = lun_details['volume_identifier']

                else:
                    sg_lun['vol_name'] = "NO_LABEL"
                result.append(sg_lun)

        return result

    def _current_sg_config(self):
        """
        Helper function returns list of dictionary that can be used to
        construct the list of volumes for changes or requests.
        :return: list of volume requests in SG in similar format to playbook
        input
        """
        lun_summary = []
        for lun in self._get_sg_lun_list():
            lun_details = self._conn.provisioning.get_volume(lun['volumeId'])
            lun_summary.append({'cap_gb': int(lun_details['cap_gb'])})

        current_config = unique_and_count(lun_summary)
        for i in current_config:
            i['num_vols'] = i.pop('count')

        return current_config

    def _change_service_level(self):
        """
        Change Service Level on existing Storage Group
        :return: None
        """
        payload = {
            "editStorageGroupActionParam": {
                "editStorageGroupSLOParam": {
                    "sloId": self._module.params['slo']
                }
            }
        }
        try:
            if self._module.params['slo']:
                sg_detail = self._conn.provisioning.get_storage_group(storage_group_name=self._sg_name)
                if sg_detail['slo'] != self._module.params['slo']:

                    self._conn.provisioning.\
                        modify_storage_group(storagegroup=self._sg_name,
                                             payload=payload)
                    self._changed = True
                    self._message.append("Applied {} SLO to {}".format(self._module.params['slo'],
                                                                       self._sg_name))
                else:
                    self._message.append("SLO of SG {} already {}".
                                         format(self._sg_name,
                                                self._module.params['slo']))

        except Exception as error:
            self._module.fail_json(msg="Unable to modify SLO for {} ({})".
                                       format(self._sg_name, error))

    def _create_sg(self):
        """
        Create SG if needed and exit module gracefully with changes
        :return: None
        """
        if self._sg_name not in self._conn.provisioning.get_storage_group_list():
            # In case of compressed SG requested, we put the compression flag
            # at ON. Warning: slo must be present for that option can works (cf. PyU4V)

            srp = "None" if self._module.params['slo'] == "None" else "SRP_1"
            if 'compression' in self._module.params:
                _compression = False if self._module.params['compression'] else True
                self._conn.provisioning.\
                    create_storage_group(srp_id=srp,
                                         sg_id=self._sg_name,
                                         slo=self._module.params['slo'],
                                         do_disable_compression=_compression)
            else:
                self._conn.provisioning.\
                    create_storage_group(srp_id=srp,
                                         sg_id=self._sg_name,
                                         slo=self._module.params['slo'])

            self._changed = True
            self._message.append("Empty Storage Group {} Created".format(self._sg_name))
        else:
            self._message.append("SG {} already exists".format(self._sg_name))

    def _delete_sg(self):
        """
        Delete Storage Group
        :return: None
        """
        # SG must exists before go ahead (obviously...)
        if self._sg_name not in self._conn.provisioning.get_storage_group_list():
            self._module.fail_json(msg="SG {} doesn't exists".format(self._sg_name))

        masking_view = self._conn.provisioning.\
            get_masking_views_from_storage_group(storagegroup=self._sg_name)

        if masking_view:
            self._message.append("Storage Group {} is Part of a Masking View".
                                 format(self._sg_name))
            self._module.fail_json(msg=self._message)

        self._conn.provisioning.delete_storagegroup(storagegroup_id=self._sg_name)
        self._changed = True
        self._message.append("SG {} has been deleted".format(self._sg_name))

    def _modify_sg(self):
        """
        Modify a Storage Group (meaning adding volumes if needed)
        :return: None
        """
        # First, we extract the current config of the related SG (same format as lun_request)
        current_config = self._current_sg_config()

        if len(current_config) > len(self._lun_request):
            message = "Volume requests must contain current config plus " \
                      "additional requests, operations on a subset of " \
                      "volumes not supported with this module."
            self._module.fail_json(msg=message)

        # Adding Volumes into a Parent SG is not supported
        sg_details = self._conn.provisioning.get_storage_group(storage_group_name=self._sg_name)
        if sg_details['type'] == 'Parent':
            self._module.fail_json(msg="{} is a parent SG and it's not possible "
                                       "to add volume in a parent SG".
                                       format(self._sg_name))

        # If the SG is empty, we add the whole lun_request inside it
        elif sg_details['num_of_vols'] == 0:
            for group in self._lun_request:
                self._conn.provisioning. \
                    add_new_vol_to_storagegroup(sg_id=self._sg_name,
                                                cap_unit="GB",
                                                num_vols=group['num_vols'],
                                                vol_size=group['cap_gb'],
                                                vol_name=group['vol_name'])
                self._message.append("{} volume(s) of {} GB added".
                                     format(group['num_vols'], group['cap_gb']))
                self._changed = True

        # Here, we assume that's the SG is not empty and we have to
        # determine how many LUNs to add inside it
        else:
            for group in self._lun_request:
                lun_to_create = group['num_vols']

                # Let's determine if we need to add more volumes into the
                # SG or not
                for in_sg in current_config:
                    # Loop until finding group of TDEVs with the same size as
                    # requested
                    if in_sg['cap_gb'] != group['cap_gb']:
                        continue

                    if in_sg['num_vols'] > group['num_vols']:
                        msg = "There is {} vols of {} GB in {} actually. You " \
                              "asked {} vols in your requests. This module " \
                              "doesn't support volumes deletion (Backlog: {})".\
                              format(in_sg['num_vols'],
                                     in_sg['cap_gb'],
                                     self._sg_name,
                                     group['num_vols'],
                                     ", ".join(self._message))
                        self._module.exit_json(msg=msg)

                    # Computing the exact number of LUNs to create (difference
                    # between the request and existing)
                    lun_to_create = group['num_vols'] - in_sg['num_vols']

                if lun_to_create > 0:
                    self._conn.provisioning. \
                        add_new_vol_to_storagegroup(sg_id=self._sg_name,
                                                    cap_unit="GB",
                                                    num_vols=lun_to_create,
                                                    vol_size=group['cap_gb'],
                                                    vol_name=group['vol_name'])

                    self._message.append("{} volume(s) of {} GB added".
                                         format(lun_to_create, group['cap_gb']))
                    self._changed = True
                else:
                    self._message.append("No new volume of {} GB to add in {}".
                                         format(group['cap_gb'], self._sg_name))

    def _rename_sg(self):
        """
        Renaming an existing StorageGroup
        :return: None
        """
        try:
            sg_list = self._conn.provisioning.get_storage_group_list()
            if self._sg_name not in sg_list:
                self._module.fail_json(msg="SG {} doesn't exists".format(self._sg_name))

            if self._module.params['new_sgname'] in sg_list:
                self._module.fail_json(msg="Target SG name {} already exists".
                                       format(self._module.params['new_sgname']))

            rename = {
                "editStorageGroupActionParam": {
                    "renameStorageGroupParam": {
                        "new_storage_Group_name": self._module.params['new_sgname']
                    }
                }
            }
            self._conn.provisioning.modify_storage_group(storagegroup=self._sg_name,
                                                         payload=rename)
            self._changed = True
            # Updating sg_name to be consistent with the next facts gathering
            self._sg_name = self._module.params['new_sgname']
            self._message.append("SG renamed to {}".format(self._sg_name))

        except Exception as error:
            self._module.fail_json(msg="Unable to rename SG({})".format(error))

    def apply_module(self):
        """
        Main function for that object
        :return: None
        """
        facts = {}

        # Storage Group deletion
        if self._module.params['state'] == 'absent':
            self._delete_sg()

        # Storage Group creation and/or alteration
        elif self._module.params['state'] == 'present':
            # If we want to rename SG, this operation will done in first
            # place and will be exclusive
            if self._module.params['new_sgname']:
                self._rename_sg()

            else:
                self._create_sg()
                self._change_service_level()
                if self._lun_request:
                    self._modify_sg()
            facts['sg_volumes'] = self._get_sg_lun_list()
            facts['lun_request'] = self._current_sg_config()

        facts['message'] = self._message
        facts['storagegroup_name'] = self._sg_name
        result = {'state': 'info', 'changed': self._changed}
        self._module.exit_json(ansible_facts={'storagegroup_detail': facts}, **result)


def main():
    DellEmcStorageGroup().apply_module()


if __name__ == '__main__':
    main()