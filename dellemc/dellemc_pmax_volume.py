#!/usr/bin/python
# Copyright: (C) 2018, DellEMC
# Author(s): Paul Martin <paule.martin@dell.com>
# Author(s): Olivier Carminati <olivier.carminati@bpce-it.fr>
# Author(s): Julien Brusset <julien.brusset.prestataire@bpce-it.fr>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
import time

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
short_description: "Simple Module to Modify Volumes that are part of a 
Strorage group on Dell EMC PowerMax or VMAX All Flash Arrays. Volumes 
can also be resized, relabeled, erased or deleted"
version_added: "2.8"
description:
  - "Module can be used to remove of modify a list of volumes from storage 
  group.  This module assumes code level 5978 or higher, volumes can be 
  part of an SRDF Metro configuration (but not for resizing, but freeing a 
  volume used in RDF replication is possible. In that case, RDF replication 
  will be destroyed). This module has been tested against UNI 9.0. Every 
  effort has been made to verify the scripts run with valid input. These 
  modules are a tech preview."
module: dellemc_pmax_volume
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
  volumes:
    description:
      - "A list of volumes described with ID, desired size (if needed) and label"
    required: true
  sgname:
    description:
      - "List of SGs name (used for adding or removing TDEVs)"
    required: false
  in_sg:
    description:
      - "[present|absent] Used with in_sg to define what to do"
    required: false
  freeing:
    description:
      - "Boolean for erasing or not a list of TDEVs (default: false)"
    required: false
  delete:
    description:
      - "Boolean for deleting or not a list of TDEVs (default: false). 
        Freeing needed first."
    required: false
requirements:
  - Ansible
  - "Unisphere for PowerMax version 9.0 or higher."
  - "VMAX All Flash, VMAX3, or PowerMax storage Array."
  - "PyU4V version 3.0.0.9 or higher using PIP python -m pip install PyU4V"
'''
EXAMPLES = '''
---
- name: Provision Storage For DB Cluster
  hosts: localhost
  connection: local
  vars_files:
    - vars.yml
    
  tasks:
  - name: Adding TDEVs into SG
    dellemc_pmax_volume:
      unispherehost: "{{unispherehost}}"
      universion: "{{universion}}"
      verifycert: "{{verifycert}}"
      user: "{{user}}"
      password: "{{password}}"
      array_id: "{{array_id}}"
      sgname: 
        - 'Ansible_SG'
      in_sg: "present"
      volumes:
        - device_id: "000BB"
        - device_id: "000BA"
  - debug: var=storagegroup_detail

  - name: Removing TDEVs from SG
    dellemc_pmax_volume:
      unispherehost: "{{unispherehost}}"
      universion: "{{universion}}"
      verifycert: "{{verifycert}}"
      user: "{{user}}"
      password: "{{password}}"
      array_id: "{{array_id}}"
      sgname: 
        - 'Ansible_SG'
      in_sg: "absent"
      volumes:
        - device_id: "000BB"
        - device_id: "000BA"
  - debug: var=storagegroup_detail

  - name: Resize volume
    dellemc_pmax_volume:
      unispherehost: "{{unispherehost}}"
      universion: "{{universion}}"
      verifycert: "{{verifycert}}"
      user: "{{user}}"
      password: "{{password}}"
      array_id: "{{array_id}}"
      volumes:
        - device_id: "000BB"
          cap_gb: 6
  - debug: var=volume_detail

  - name: Relabeling volumes 
    dellemc_pmax_volume:
      unispherehost: "{{unispherehost}}"
      universion: "{{universion}}"
      verifycert: "{{verifycert}}"
      user: "{{user}}"
      password: "{{password}}"
      array_id: "{{array_id}}"
      volumes:
        - device_id: "000BB"
          vol_name: "MYLABEL"
        - device_id: "000BA"
          vol_name: "MYLABEL"
  - debug: var=volume_detail

  - name: Relabeling AND resizing volumes at the same time 
    dellemc_pmax_volume:
      unispherehost: "{{unispherehost}}"
      universion: "{{universion}}"
      verifycert: "{{verifycert}}"
      user: "{{user}}"
      password: "{{password}}"
      array_id: "{{array_id}}"
      volumes:
        - device_id: "000BB"
          vol_name: "MYLABEL"
          cap_gb: 6
        - device_id: "000BA"
          vol_name: "MYLABEL"
          cap_gb: 6
  - debug: var=volume_detail

  - name: Erasing/Freeing volumes
    dellemc_pmax_volume:
      unispherehost: "{{unispherehost}}"
      universion: "{{universion}}"
      verifycert: "{{verifycert}}"
      user: "{{user}}"
      password: "{{password}}"
      array_id: "{{array_id}}"
      freeing: true
      volumes:
        - device_id: "000BB"
        - device_id: "000BA"
  - debug: var=volume_detail

  - name: Deleting volumes
    dellemc_pmax_volume:
      unispherehost: "{{unispherehost}}"
      universion: "{{universion}}"
      verifycert: "{{verifycert}}"
      user: "{{user}}"
      password: "{{password}}"
      array_id: "{{array_id}}"
      delete: true
      volumes:
        - device_id: "000BB"
        - device_id: "000BA"
  - debug: var=volume_detail
'''
RETURN = '''
ok: [localhost] => {
    "volume_detail": {
        "message": [
            "000E2 was paired with 0008B(000297800953)",
            "000E0 freeing launched",
            "000E2 freeing launched"
        ]
    }
}
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.dellemc import dellemc_pmax_argument_spec, pmaxapi


class DellEmcVolume(object):
    """
    Ansible Module for manipulating TDEVs
    (Resizing, adding/removing to and from SGs, relabeling, deleting)
    """

    def __init__(self):
        self._argument_spec = dellemc_pmax_argument_spec()

        self._argument_spec.update(dict(
            volumes=dict(type='list',
                         options=dict(
                             device_id=dict(default=True, type="str", required=True),
                             vol_name=dict(default=False, type="str", required=False),
                             cap_gb=dict(default=True, type="float", required=False)
                         ), required=True),
            sgname=dict(type='list', required=False, default=[]),
            in_sg=dict(type='str', choices=['present', 'absent'], required=False, ),
            freeing=dict(type='bool', required=False, default=False),
            delete=dict(type='bool', required=False, default=False),
        ))

        self._module = AnsibleModule(argument_spec=self._argument_spec)

        # Convert cap_gb to float ( in case cap_gb is filled using var_prompts).
        # sub-level options are always converted to str. Type doesn't matter
        try:
            for v in self._module.params['volumes']:
                if 'cap_gb' in v.keys():
                    v['cap_gb'] = float(v['cap_gb'])
        except ValueError:
            self._module.fail_json(msg="Cannot convert cap_gb to float (field volumes).")

        self._conn = pmaxapi(self._module)
        self._changed = False
        self._facts = None
        self._message = []

        # Runs pre-checks
        self._mode_resizing = False
        self._modes_pre_checks()

    def _modes_pre_checks(self):
        """
        Checking if only one mode are used at a time
        :return: (None)
        """
        # Pre-check in_sg/freeing/delete options cannot be used together
        params = [bool(self._module.params['in_sg']),
                  self._module.params['freeing'],
                  self._module.params['delete']]

        # If no other action than volume to resize of relabel
        if params.count(True) == 0:
            self._mode_resizing = True

        # Only one mode could be set at a time
        if params.count(True) > 1:
            self._module.fail_json(msg="Only one operation allowed at a time "
                                       "(in_sg OR freeing OR delete)")

    def _add_volumes(self):
        """
        Adding existing TDEVs into existing SG(s)
        :return: (None)
        """
        # First of all, check if SGs exists
        # If not, it's a problem and we can't go ahead
        sg_list = self._conn.provisioning.get_storage_group_list()
        sg_not_exists = False
        sg_missing = ""
        for sg in self._module.params['sgname']:
            if sg not in sg_list:
                sg_missing += "{} SG doesn't exists".format(sg)
        if sg_not_exists:
            self._module.fail_json(msg=sg_missing)

        # Let's launch the main function and add TDEVs into SGs
        volume_ids = [v['device_id'] for v in self._module.params["volumes"]]
        for sg in self._module.params['sgname']:
            sg_vols = self._conn.provisioning. \
                get_volume_list(filters={'storageGroupId': sg})

            try:
                for volume in volume_ids:
                    if volume not in sg_vols:
                        self._conn.provisioning.add_existing_vol_to_sg(sg_id=sg,
                                                                       vol_ids=volume)
                        self._message.append("{} successfully added to {}"
                                             .format(volume, sg))
                        self._changed = True
                    else:
                        self._message.append("{} already in {}".format(volume, sg))
            except Exception as error:
                self._module.fail_json(msg="Unable to add {} to {} ({})"
                                       .format(volume_ids, sg, error))

        self._facts = ({'message': self._message})

    def _delete_volumes(self):
        """
        Delete volumes/TDEVs (must be empty before)
        :return: (None)
        """
        for volume in self._module.params["volumes"]:
            try:
                self._conn.provisioning.delete_volume(device_id=volume["device_id"])
                self._changed = True
                self._message.append("{} has been deleted"
                                     .format(volume["device_id"]))
            except Exception as error:
                self._module.fail_json(msg="Unable to delete volume {} ({})"
                                       .format(volume["device_id"], error))
        self._facts = ({'message': self._message})

    def _freeing_volumes(self):
        """
        Erasing data from TDEVs (TDEVs must be out of SGs)
        :return: (None)
        """
        # Check if any TDEVs still are in SGs which is not normal.
        # (CAREFUL: deallocate by API works EVEN IF A VOLUME IS STILL IN A SG)
        still_in_sg = False
        for volume in self._module.params["volumes"]:
            v_details = self._conn.provisioning.get_volume(device_id=volume['device_id'])
            if 'storageGroupId' in v_details:
                still_in_sg = True
                self._message.append("{} is still in SG {} (remove it before freeing)".
                                     format(volume['device_id'], v_details['storageGroupId']))
        if still_in_sg:
            self._module.fail_json(msg=self._message)

        # First, we need to know if RDF pairs exists and if yes, which volumes
        # are concerned. These information will be used later to destroy RDF
        # pairs
        rdf_mapping = {}
        sg_prefix = "SG_DeletePair_{}".format(round(time.time()))

        for volume in self._module.params["volumes"]:
            v_details = self._conn.provisioning.get_volume(device_id=volume['device_id'])
            if 'rdfGroupId' in v_details:
                for group in v_details['rdfGroupId']:
                    if group['rdf_group_number'] not in rdf_mapping:
                        rdf_mapping[group['rdf_group_number']] = []
                    rdf_mapping[group['rdf_group_number']].append(volume['device_id'])

        # If RDF pairs exists, delete them
        if rdf_mapping:
            _message = []
            for rdf_id in rdf_mapping:
                for volume in rdf_mapping[rdf_id]:
                    v_details = self._conn.replication.get_rdf_group_volume(rdf_number=rdf_id,
                                                                            device_id=volume)
                    _message.append("{} was paired with {}({})".
                                    format(volume,
                                           v_details['remoteVolumeName'],
                                           v_details['remoteSymmetrixId']))

            for rdf_id in rdf_mapping:
                sg_name = "{}_{}".format(sg_prefix, rdf_id)
                try:
                    self._conn.provisioning. \
                        create_storage_group(srp_id='SRP_1',
                                             sg_id=sg_name,
                                             slo='Diamond')
                    self._conn.provisioning. \
                        add_existing_vol_to_sg(sg_id=sg_name,
                                               vol_ids=rdf_mapping[rdf_id])
                    self._conn.replication. \
                        delete_storagegroup_srdf(storagegroup_id=sg_name,
                                                 rdfg_num=rdf_id)
                except Exception as error:
                    self._module.fail_json(msg="Unable to destroy RDF pairs for "
                                               "devices {} ({})"
                                           .format(", ".join(rdf_mapping[rdf_id]), error))
                finally:
                    self._conn.provisioning.delete_storagegroup(storagegroup_id=sg_name)

                self._changed = True
                self._message += _message

        # Finally, let's freeing the list of volumes
        for volume in self._module.params["volumes"]:
            try:
                self._conn.provisioning.deallocate_volume(device_id=volume['device_id'])

            except Exception as error:
                if 'device is already in the requested state' not in str(error):
                    _msg = "Unable to deallocate volume {}. Deleted pairs: {} ({})". \
                        format(volume['device_id'], ", ".join(self._message), error)
                    self._module.fail_json(msg=_msg)

            self._changed = True
            self._message.append("{} freeing launched".format(volume['device_id']))

        self._facts = ({'message': self._message})

    def _relabeling_volumes(self):
        """
        Changing label on Volumes/TDEVs
        :return: (None)
        """
        for volume in self._module.params['volumes']:
            # We try to rename volume only if a 'vol_name' parameter is set into
            # the given options
            if 'vol_name' in volume:
                a_volume = self._conn.provisioning. \
                    get_volume(device_id=volume['device_id'])
                # Checks to verify identifier matches the label
                if 'volume_identifier' in a_volume and \
                        volume['vol_name'] == a_volume['volume_identifier']:
                    self._message.append("{} No changes made to label".
                                         format(volume['device_id']))

                else:
                    try:
                        self._conn.provisioning. \
                            rename_volume(device_id=volume['device_id'],
                                          new_name=volume['vol_name'])
                    except Exception as error:
                        self._module.fail_json(msg="Unable to rename {} ({})".
                                               format(volume['device_id'], error))
                    self._message.append("{} label changed for {}"
                                         .format(volume['device_id'], volume['vol_name']))
                    self._changed = True
        self._facts = ({'message': self._message})

    def _remove_volumes(self):
        """
        Remove Volumes/TDEVs from SG(s)
        :return: (None)
        """
        # First of all, check if SGs exists
        # If not, it's a problem and we can't go ahead
        sg_list = self._conn.provisioning.get_storage_group_list()
        sg_not_exists = False
        sg_missing = ""
        for sg in self._module.params['sgname']:
            if sg not in sg_list:
                sg_missing += "{} SG doesn't exists".format(sg)
        if sg_not_exists:
            self._module.fail_json(msg=sg_missing)

        # Then, we check if the volumes to remove are the last ones into the
        # SG and if this SG are embedded into a MV. If yes, can't go ahead
        # because MV with empty SG is not supported
        volume_ids = [v['device_id'] for v in self._module.params["volumes"]]
        cant_remove = False
        cant_remove_msg = ""
        for sg in self._module.params['sgname']:
            sg_vols = self._conn.provisioning. \
                get_volume_list(filters={'storageGroupId': sg})

            if len(sg_vols) == len(volume_ids) and set(volume_ids) == set(sg_vols):
                if self._conn.provisioning. \
                        get_masking_views_from_storage_group(storagegroup=sg):
                    cant_remove = True
                    cant_remove_msg += "SG {} is used in a MV and TDEVs {} are " \
                                       "the last ones inside it". \
                        format(sg, ", ".join(volume_ids))
        if cant_remove:
            self._module.fail_json(msg=cant_remove_msg)

        # Let's launch the main function and remove TDEVs from SGs
        for sg in self._module.params['sgname']:
            sg_vols = self._conn.provisioning. \
                get_volume_list(filters={'storageGroupId': sg})

            for volume in volume_ids:
                if volume in sg_vols:
                    try:
                        self._conn.provisioning. \
                            remove_vol_from_storagegroup(sg_id=sg,
                                                         vol_id=volume)
                    except Exception as error:
                        self._module.fail_json(msg="Unable to remove {} from {} ({})".
                                               format(volume, sg, error))
                    self._message.append("{} successfully removed from {}"
                                         .format(volume, sg))
                    self._changed = True
                else:
                    self._message.append("{} not in {}".format(volume, sg))

        self._facts = ({'message': self._message})

    def _resizing_volumes(self):
        """
        Resizing volumes (only for non-RDF volumes)
        :return: (None)
        """
        for volume in self._module.params['volumes']:
            # We launch actions only of 'cap_gb' option is set in parameters
            if 'cap_gb' in volume:
                a_volume = self._conn.provisioning. \
                    get_volume(device_id=volume['device_id'])

                if a_volume['cap_gb'] < volume['cap_gb']:
                    try:
                        self._conn.provisioning.extend_volume(new_size=volume['cap_gb'],
                                                              device_id=volume['device_id'])
                    except Exception as error:
                        self._module.fail_json(msg="Unable to extend {} ({})".
                                               format(volume['device_id'], error))
                    self._message.append("Volume {} re-sized to {} GB".
                                         format(volume['device_id'], volume['cap_gb']))
                    self._changed = True
                else:
                    self._message.append("{} size unchanged".format(volume['device_id']))
        self._facts = ({'message': self._message})

    def apply_module(self):
        """
        Main action of this module
        :return: (None)
        """
        # First detect if changes needs to be applied to volumes
        # (ex: size or label)
        if self._mode_resizing:
            self._resizing_volumes()
            self._relabeling_volumes()

        else:
            # Adding or removing TDEVs to/from SGs
            if bool(self._module.params['in_sg']):
                # Parameter check before go ahead
                if not self._module.params['sgname']:
                    self._module.fail_json(msg="sgname parameter must present "
                                               "while using with in_sg "
                                               "parameter.")

                if self._module.params['in_sg'] == 'absent':
                    self._remove_volumes()

                elif self._module.params['in_sg'] == 'present':
                    self._add_volumes()

            # Freeing a list of TDEVs
            elif self._module.params['freeing']:
                self._freeing_volumes()

            # Deleting a list of TDEVs
            elif self._module.params['delete']:
                self._delete_volumes()

        result = {'state': 'info', 'changed': self._changed}
        self._module.exit_json(ansible_facts={'volume_detail': self._facts}, **result)


def main():
    DellEmcVolume().apply_module()


if __name__ == '__main__':
    main()
