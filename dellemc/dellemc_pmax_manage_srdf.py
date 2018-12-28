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
short_description: "Module to control the status of an SRDF replicated 
storage group"
version_added: "2.8"
description:
  - "This module requires that SRDF Protection has already been configured 
  and the group is protected with SRDF.  Single Hop SRDF is supported with 
  this module.  SRDF/S and A are supported with this module.  This has been 
  tested against UNI 9.0, minimum version for support is 8.4. Every effort has 
  been made to verify the scripts run with valid input. These modules are 
  a tech preview."
module: dellemc_pmax_createsg
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
  sgname:
    description:
      - "Name of SRDF Protected Storage Group"  
  action:
    description:
      - "Any one of the following actions Establish, Suspend, Split, Failover,
      Failback" 
requirements:
  - Ansible
  - "Unisphere for PowerMax version 9.0 or higher."
  - "VMAX All Flash, VMAX3, or PowerMax storage Array."
  - "PyU4V version 3.0.0.8 or higher using PIP python -m pip install PyU4V"
'''
EXAMPLES = '''
---
- name: "Provision Storage For DB Cluster"
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
    - name: "Base Values for Task Add module Specific paramters"
      dellemc_pmax_manage_srdf:
        unispherehost: "{{unispherehost}}"
        universion: "{{universion}}"
        array_id: "{{array_id}}"
        user: "{{user}}"
        password: "{{password}}"
        verifycert: "{{verifycert}}"
        sgname: "Ansible_SG"
        action: "Suspend"
'''
RETURN = '''
dellemc_pmax_manage_srdf:
    description: Information about storage group created
    returned: success
    type: dict
    "rdfstate": {
            "hop2Modes": [],
            "hop2Rdfgs": [],
            "hop2States": [],
            "largerRdfSides": [
                "Equal"
            ],
            "localR1InvalidTracksHop1": 0,
            "localR2InvalidTracksHop1": 0,
            "modes": [
                "Synchronous"
            ],
            "rdfGroupNumber": 3,
            "remoteR1InvalidTracksHop1": 0,
            "remoteR2InvalidTracksHop1": 0,
            "states": [
                "Suspended"
            ],
            "storageGroupName": "Ansible_SG",
            "symmetrixId": "000197600156",
            "totalTracks": 24585,
            "volumeRdfTypes": [
                "R1"
            ]
        }
    },

'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.dellemc import dellemc_pmax_argument_spec, pmaxapi


def main():
    changed = False
    argument_spec = dellemc_pmax_argument_spec()
    argument_spec.update(dict(
            sgname=dict(type='str', required=True),
            action=dict(type='str',choices=['Establish','Suspend','Split',
                                            'Failover','Failback'],
                        required=True)
        )
    )
    # Make REST call to Unisphere Server and execute SRDF control operation

    module = AnsibleModule(argument_spec=argument_spec)
    # Setup connection to API and import replicaiton functions.
    conn = pmaxapi(module)

    rep=conn.replication

    rdf_sglist = rep.get_storage_group_rep_list(has_srdf=True)

    if module.params['sgname'] in rdf_sglist:
        rdfg_list = rep.get_storagegroup_srdfg_list(module.params['sgname'])
        if len(rdfg_list)<=1:
            rdfg = rdfg_list[0]
            rep.modify_storagegroup_srdf(storagegroup_id=module.params['sgname']
            , action=module.params['action'], rdfg=rdfg)
            changed = True
        else:
            module.fail_json(changed=changed,
                msg='Specified Storage Group has mult-site RDF Protection '
                    'Ansible Module currently supports single Site SRDF '
                    'please use Unishpere for PowerMax UI for SRDF group '
                    'managment')

    else:

        module.fail_json(msg='Specified Storage Group is not currently SRDF '
                             'Protected')
    rdfstate=rep.get_storagegroup_srdf_details(
        storagegroup_id=module.params['sgname'], rdfg_num=rdfg)
    facts = rdfstate
    result = {'state': 'info', 'changed': changed}
    module.exit_json(ansible_facts={'rdfstate': facts}, **result)


if __name__ == '__main__':
    main()
