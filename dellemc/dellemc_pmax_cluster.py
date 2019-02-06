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
short_description: "Create and manage hosts, host groups on Dell 
EMC PowerMax or VMAX All Flash"
version_added: "2.8"
description:
  - "This module has been tested against UNI 9.0. Every effort has been made
  to verify the scripts run with valid input. These modules are a tech preview"
module: dellemc_pmax_createhost
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
  clustername:
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
  - "PyU4V version 3.0.0.8 or higher using PIP python -m pip install PyU4V"
'''
EXAMPLES = '''
---
- name: "Create Clusters"
  connection: local
  hosts: localhost
  vars:
    array_id: 000197600156
    password: smc
    unispherehost: "192.168.1.1"
    universion: "90"
    user: smc
    verifycert: false

  tasks:
  - name: Create Cluster
    dellemc_pmax_cluster:
        unispherehost: "{{unispherehost}}"
        universion: "{{universion}}"
        verifycert: "{{verifycert}}"
        user: "{{user}}"
        password: "{{password}}"
        array_id: "{{array_id}}"
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


def create_or_modify_hostgroup(apiconnection, module):
    changed = False
    # Create a New Host
    conn = apiconnection
    dellemc = conn.provisioning
    message = "The Following hosts don't exist "
    # Check for each host in the host list that it exists, otherwise fail
    # module.

    hostgrouplist = dellemc.get_hostgroup_list()
    changed = False
    # Create a New Host
    conn = apiconnection
    dellemc = conn.provisioning
    message = ""

    if module.params['cluster_name'] not in hostgrouplist:
        try:
            dellemc.create_hostgroup(hostgroup_id=module.params[
                'cluster_name'], host_list=module.params['host_list'])
            changed = True
        except Exception:
            message = "Unable to create cluster"

    elif module.params['cluster_name'] in hostgrouplist and module.params[
        'host_state'] == "in_cluster":
        try:
            dellemc.modify_hostgroup(hostgroup_id=module.params['cluster_name'],
                                     add_host_list=module.params['host_list'])
            changed = True
        except Exception:
            message = "Unable to add hosts Cluster"

    elif module.params['cluster_name'] in hostgrouplist and module.params[
            'host_state'] == "not_in_cluster":
        try:
            dellemc.modify_hostgroup(
                hostgroup_id=module.params['cluster_name'],
                remove_host_list=module.params['host_list'])
            changed = True
        except Exception:
            message = "Problem removing host from cluster"
    else:
        message = "Nothing Happened"
    facts = ({'message': message})
    result = {'state': 'info', 'changed': changed}
    module.exit_json(ansible_facts={'host_detail': facts}, **result)


def delete_hostgroup(apiconnection, module):
    changed = False
    # Create a New Host
    conn = apiconnection
    dellemc = conn.provisioning
    hostlist = dellemc.get_host_list()
    # Compile a list of existing hosts.
    hostgrouplist = dellemc.get_hostgroup_list()
    # Check if Host Name already exists.
    if module.params['cluster_name'] in hostgrouplist:
        mvlist = dellemc.get_masking_views_by_host(\
                initiatorgroup_name=module.params['cluster_name'])
        if len(mvlist) < 1:
            dellemc.delete_hostgroup(hostgroup_id=module.params['cluster_name'])
            changed = True
            message = "Cluster Deleted"
        else:
            message = module.params['host_id'] + " host is part of a Masking " \
                                                "view"
    # Additional Check, if user deleted all hosts from hostgroup,
    # the hostgroup becomes a host, if this is the case delete should still
    # be successful
    elif module.params['cluster_name'] in hostlist:
        hostdetails = dellemc.get_host(module.params['cluster_name'])
        if (hostdetails["num_of_initiators"]) < 1:
            dellemc.delete_host(host_id=module.params['cluster_name'])
        message = "Delete Successful"
    else:
        message = "Specified hostgroup does not exist"
    facts = ({'message': message})
    result = {'state': 'info', 'changed': changed}
    module.exit_json(ansible_facts={'cluster_detail': facts}, **result)


def main():
    argument_spec = dellemc_pmax_argument_spec()
    argument_spec.update(dict(
        cluster_name=dict(type='str', required=True),
        host_list=dict(type='list', required=True),
        state=dict(type='str', required=True, choices=['present', 'absent']),
        host_state=dict(type='str', required=True, choices=['in_cluster',
                                                            'not_in_cluster'])
    )
    )
    module = AnsibleModule(argument_spec=argument_spec)
    # Setup connection to API
    conn = pmaxapi(module)
    if module.params['state'] == "present":
        create_or_modify_hostgroup(apiconnection=conn, module=module)
    elif module.params['state'] == "absent":
        delete_hostgroup(apiconnection=conn, module=module)


if __name__ == '__main__':
    main()
