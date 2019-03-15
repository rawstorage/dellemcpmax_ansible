#!/usr/bin/python
# Copyright (C) 2018 DellEMC
# Author(s): Paul Martin <paule.martin@dell.com>
# Author(s): Olivier Carminati <olivier.carminati@bpce-it.fr>
# Author(s): Julien Brusset <julien.brusset.prestataire@bpce-it.fr>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
from functools import partial

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
short_description: "Create and manage hosts, host groups on Dell 
EMC PowerMax or VMAX All Flash"
version_added: "2.8"
description:
  - "This module has been tested against UNI 9.0. Every effort has been made
  to verify the scripts run with valid input. These modules are a tech preview"
module: dellemc_pmax_cluster
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
  cluster_name:
    description:
      - "32 Character string no special character permitted except for
      underscore"
  host_list:
    description:
      - "List of Host to be added to Cluster"
  state:
    description:
      - "Whether exected state is for Cluster to be present or absent at 
      the end of the task"
  host_state:
    description:
      - "Whether or not host should be in cluster, in_cluster ensures host 
      is part of the cluster, not_in_cluster will attempt to remove the host"
requirements:
  - Ansible
  - "Unisphere for PowerMax version 9.0 or higher."
  - "VMAX All Flash, VMAX3, or PowerMax storage Array."
  - "PyU4V version 3.0.0.9 or higher using PIP python -m pip install PyU4V"
'''
EXAMPLES = '''
---
- name: "Create Clusters"
  connection: local
  hosts: localhost
  vars_files:
    - vars.yml
  tasks:
  - name: Create Cluster
    dellemc_pmax_cluster:
        unispherehost: "{{unispherehost}}"
        universion: "{{universion}}"
        verifycert: "{{verifycert}}"
        user: "{{user}}"
        password: "{{password}}"
        array_id: "{{array_id}}"
        cluster_name: "Cluster"
        host_list:
        - AnsibleHost1
        - AnsibleHost2
        state: present
        host_state: in_cluster
  - name: Remove Host From Cluster
    dellemc_pmax_cluster:
        unispherehost: "{{unispherehost}}"
        universion: "{{universion}}"
        verifycert: "{{verifycert}}"
        user: "{{user}}"
        password: "{{password}}"
        array_id: "{{array_id}}"
        cluster_name: "Cluster"
        host_list:
        - AnsibleHost1
        state: present
        host_state: not_in_cluster
  - name: Add Host to Cluster
    dellemc_pmax_cluster:
        unispherehost: "{{unispherehost}}"
        universion: "{{universion}}"
        verifycert: "{{verifycert}}"
        user: "{{user}}"
        password: "{{password}}"
        array_id: "{{array_id}}"
        cluster_name: "Cluster"
        host_list:
        - AnsibleHost2
        state: present
        host_state: in_cluster
  - name: Delete Cluster
    dellemc_pmax_cluster:
        unispherehost: "{{unispherehost}}"
        universion: "{{universion}}"
        verifycert: "{{verifycert}}"
        user: "{{user}}"
        password: "{{password}}"
        array_id: "{{array_id}}"
        cluster_name: "Cluster"
        host_list:
        - AnsibleHost2
        state: absent
        host_state: in_cluster
'''
RETURN = r'''
    "ansible_facts": {
        "cluster_detail": {
            "message": "HostGroup Deleted"
        }
    },
'''
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.dellemc import dellemc_pmax_argument_spec, pmaxapi

BASE_FLAGS = {'volume_set_addressing': {'enabled': False, 'override': False},
              'disable_q_reset_on_ua': {'enabled': False, 'override': False},
              'environ_set': {'enabled': False, 'override': False},
              'avoid_reset_broadcast': {'enabled': False, 'override': False},
              'openvms': {'enabled': False, 'override': False},
              'scsi_3': {'enabled': False, 'override': False},
              'spc2_protocol_version': {'enabled': False, 'override': False},
              'scsi_support1': {'enabled': False, 'override': False},
              'consistent_lun': False
              }


class DellEmcPmaxCluster(object):
    """
    Creating, updating and deleting an HostGroup
    """

    def __init__(self):
        self._argument_spec = dellemc_pmax_argument_spec()
        self._argument_spec.update(dict(
            cluster_name=dict(type='str', required=True),
            host_list=dict(type='list', required=True),
            state=dict(type='str', required=True,
                       choices=['present', 'absent']),
            host_state=dict(type='str',
                            required=True,
                            choices=['in_cluster', 'not_in_cluster'])
        ))

        self._module = AnsibleModule(argument_spec=self._argument_spec)
        self._conn = pmaxapi(self._module)

        self._changed = False
        self._message = ''

        self._cluster_name = self._module.params['cluster_name']
        self._host_list = self._module.params['host_list']
        self._host_state = self._module.params['host_state']

    def _consistent_lun_needed(self):
        """
        Check if the host-group must be created with a consistent_lun
        (depending on child: if all of them are using c_lun : True)
        :return: (bool)
        """

        # Extract for all host their consistent_lun status
        c_lun = []
        for host in self._host_list:
            c_lun.append(self._conn.provisioning.
                         get_host(host_id=host)['consistent_lun'])

        # It's not possible to mix consistent_lun states in host-group so it's
        # an error case
        if True in c_lun and False in c_lun:
            self._module.fail_json(msg='Error child hosts have mixed consistent'
                                       '_lun options. Hosts from a given '
                                       'HostGroup must have the same '
                                       'consistent_lun parameters')
        return all(c_lun)

    def _create_or_modify_hostgroup(self):
        """
        Create or modify an host-group
        :return: (None)
        """
        hgrp_list = self._conn.provisioning.get_hostgroup_list()

        # Creating a brand new host-group
        if self._cluster_name not in hgrp_list:

            # Composing the method of creation depending if the consistent_lun
            # is require or not
            create_hgrp = partial(self._conn.provisioning.create_hostgroup,
                                  hostgroup_id=self._cluster_name,
                                  host_list=self._host_list)
            if self._consistent_lun_needed():
                flags = BASE_FLAGS.copy()
                flags['consistent_lun'] = True
                create_hgrp = partial(self._conn.provisioning.create_hostgroup,
                                      hostgroup_id=self._cluster_name,
                                      host_list=self._host_list,
                                      host_flags=flags)

            try:
                create_hgrp()
                self._changed = True
                self._message = "Cluster {} created with {}".\
                                format(self._cluster_name,
                                       ", ".join(self._host_list))

            except Exception as error:
                self._module.fail_json(msg="Unable to create cluster {} ({})".
                                       format(self._cluster_name, error))

        # Adding new host to an existing host-group
        elif self._cluster_name in hgrp_list and self._host_state == 'in_cluster':
            try:
                self._conn.provisioning.\
                    modify_hostgroup(hostgroup_id=self._cluster_name,
                                     add_host_list=self._host_list)
                self._changed = True
                self._message = "{} added to cluster {}".\
                                format(", ".join(self._host_list),
                                       self._cluster_name)

            except Exception as error:
                self._module.fail_json(msg="Unable to add hosts {} into {} "
                                           "Cluster ({})".
                                       format(self._host_list,
                                              self._cluster_name,
                                              error))

        # Removing an host from an existing host-group
        elif self._cluster_name in hgrp_list and \
                self._host_state == 'not_in_cluster':
            try:
                self._conn.provisioning.\
                    modify_hostgroup(hostgroup_id=self._cluster_name,
                                     remove_host_list=self._host_list)
                self._changed = True
                self._message = "{} removed from cluster {}".\
                                format(", ".join(self._host_list),
                                       self._cluster_name)

            except Exception as error:
                self._module.\
                    fail_json(msg="Problem removing host {} from cluster {} ({})".
                                  format(", ".join(self._host_list),
                                         self._cluster_name,
                                         error))
        else:
            self._message = "Nothing changed"

    def _delete_hostgroup(self):
        """
        Deleting an host-group
        :return: (None)
        """
        host_groups = self._conn.provisioning.get_hostgroup_list()
        if self._cluster_name not in host_groups:
            self._module.fail_json(msg="{} does not exist".
                                   format(self._cluster_name))

        mvlist = self._conn.provisioning.\
            get_masking_views_by_host(initiatorgroup_name=self._cluster_name)

        if len(mvlist) < 1:
            self._conn.provisioning.\
                delete_hostgroup(hostgroup_id=self._cluster_name)
            self._changed = True
            self._message = "Cluster {} deleted".format(self._cluster_name)

        else:
            self._message = "{} host is part of a MaskingView".\
                            format(self._cluster_name)

        # Additional Check, if user deleted all hosts from hostgroup,
        # the hostgroup becomes a host, if this is the case delete should still
        # be successful
        if self._cluster_name in self._conn.provisioning.get_host_list():
            hostdetails = self._conn.provisioning.get_host(self._cluster_name)

            if hostdetails['num_of_initiators'] < 1:
                self._conn.provisioning.delete_host(host_id=self._cluster_name)
                self._message = "{} successfully deleted".\
                                format(self._cluster_name)

    def apply_module(self):
        """
        Execute the module logic
        :return: None
        """
        if self._module.params['state'] == 'present':
            self._create_or_modify_hostgroup()

        elif self._module.params['state'] == 'absent':
            self._delete_hostgroup()

        facts = ({'message': self._message})
        result = {'state': 'info', 'changed': self._changed}
        self._module.exit_json(ansible_facts={'host_detail': facts}, **result)


def main():
    DellEmcPmaxCluster().apply_module()


if __name__ == '__main__':
    main()