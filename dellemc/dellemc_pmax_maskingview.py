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
  vars:
    array_id: 000197600156
    password: smc
    sgname: Ansible_SG
    unispherehost: "192.168.1.123"
    universion: "90"
    user: smc
    verifycert: false

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
'''
RETURN = r'''
'''
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.dellemc import dellemc_pmax_argument_spec, pmaxapi

def main():
    changed = False
    argument_spec = dellemc_pmax_argument_spec()
    argument_spec.update(dict(
            sgname=dict(type='str', required=True),
            host_or_cluster=dict(type='str', required=True),
            portgroup_id=dict(type='str', required=True),
            maskingview_name=dict(type='str', required=True)
        )
    )
    module = AnsibleModule(argument_spec=argument_spec)
    # Create Connection to Unisphere Server to Make REST calls
    conn = pmaxapi(module)
    dellemc = conn.provisioning
    # Make REST call to Unisphere Server and execute create masking view
    mvlist = dellemc.get_masking_view_list()
    # Check if Storage Group already exists
    host = ""
    pg = ""
    sg = ""
    valid_mv_components = True
    mv_details = "New Masking View Not Created"
    # Make sure parameters aren't used in a masking view with a different
    # name and that SG PG and Host exist
    sglist = dellemc.get_storage_group_list()
    pg_list = dellemc.get_portgroup_list()
    hostlist = dellemc.get_host_list()
    hostgrouplist = dellemc.get_hostgroup_list()
    new_mv_components_exits = False

    #Check Masking
    if module.params['maskingview_name'] not in mvlist:
        if (module.params['host_or_cluster'] in hostlist or hostgrouplist) and  \
                (module.params['sgname'] in sglist) and (module.params['portgroup_id'] in pg_list):

            # Check if storage group is already in a view
            existing_sg_mvs = dellemc.get_masking_views_from_storage_group(
                storagegroup=module.params['sgname'])
            if len(existing_sg_mvs) > 0:
                for mv in existing_sg_mvs:
                    existing_mv_details = dellemc.get_masking_view(
                        masking_view_name=mv)
                    if 'hostId' in existing_mv_details:
                        host = existing_mv_details['hostId']
                    else:
                        host = existing_mv_details['hostGroupId']
                    sg = existing_mv_details['storageGroupId']
                    pg = existing_mv_details['portGroupId']
                if sg == module.params['sgname'] and pg == module.params[
                    'portgroup_id'] \
                        and host == module.params['host_or_cluster']:
                    valid_mv_components = False
                    mv_details = mv + " Contains the Same Storage Group, " \
                                      "Port Group and Hosts"

            if valid_mv_components and new_mv_components_exits:
                dellemc.create_masking_view_existing_components(
                    port_group_name=module.params['portgroup_id'],
                    masking_view_name=module.params['maskingview_name'],
                    host_name=module.params['host_or_cluster'],
                    storage_group_name=module.params['sgname'])
                changed = True
                message = "Masking view sucessfully created"
                mv_details = dellemc.get_masking_view(
                    module.params['maskingview_name'])
            elif not valid_mv_components:
                message = "Masking Views should be a unique combination of SG, " \
                          "Port Group and Host or HostGroup please check input " \
                          "parameters"
    else:
        message = "Masking View Already Esists"
    facts = ({'message': message,
              'mv_details': mv_details})
    result = {'state': 'info', 'changed': changed}
    module.exit_json(ansible_facts={'maskingview_detail': facts}, **result)


if __name__ == '__main__':
    main()