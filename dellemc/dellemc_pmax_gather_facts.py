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
  - "Corey Wanless (@coreywan)"
short_description: "Module to gather facts about PowerMAX array."
version_added: "2.8"
description:
  - "This module has been tested against UNI 9.0. Every effort has been made
  to verify the scripts run with valid input. These modules are a tech preview"
module: dellemc_pmax_gather_facts
short_description: ""
requirements:
  - Ansible
  - "Unisphere for PowerMax version 9.0 or higher."
  - "VMAX All Flash, VMAX3, or PowerMax storage Array."
  - "PyU4V version 3.0.0.8 or higher using PIP python -m pip install PyU4V"
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
  gather_subset:
    - description:
      - "Optional parameter to tell ansible which facts to gather about the
      system. Possible values for this argument include hosts, host_groups,
      masking_views, port_groups, slo, srp, storage_groups, volumes can
      specify a list of values to include a larger subset. Values can also
      be used with an initial C(M(!)) to specify that a specific subset 
      should not be collected.
    default: "all"
    required: false
'''

EXAMPLES = '''
---
- name: "Gather all facts except for the volumes"
  dellemc_pmax_gather_facts:
    unispherehost: "{{unispherehost}}"
    universion: "{{universion}}"
    verifycert: "{{verifycert}}"
    user: "{{user}}"
    password: "{{password}}"
    array_id: "{{array_id}}"
    gather_subset: "!volumes"
- debug: var=dellemc_pmax_facts

- name: "Gather only storage_groups and masking_views facts"
  dellemc_pmax_gather_facts:
    unispherehost: "{{unispherehost}}"
    universion: "{{universion}}"
    verifycert: "{{verifycert}}"
    user: "{{user}}"
    password: "{{password}}"
    array_id: "{{array_id}}"
    gather_subset:
      - storage_groups
      - masking_views
- debug: var=dellemc_pmax_facts
'''
RETURN = r'''
dellemc_pmax_facts:
    description: Returns various information about PowerMAX Array
    returned: always
    type: dict
    sample: '{
        "dellemc_pmax_facts": {
            "hosts": {...},
            "host_groups": {...},
            "masking_views": {...},
            "port_groups": {...},
            "slo": {...},
            "srp": {...},
            "storage_groups": {...},
            "volumes": {...}
    }'
'''
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.dellemc import dellemc_pmax_argument_spec, pmaxapi

class Dellpmax_Gather_Facts(object):
    def __init__(self,module):
        self.module = module
        self.conn = pmaxapi(module)
        self.dellemc = self.conn.provisioning
        self.facts = {}
        self.gather_subset = module.params['gather_subset']
        self.fact_subsets = {
            'hosts': {
                'method': self.generic_get_object_facts,
                'kwargs': {
                    'name': 'host',
                },
            },
            'host_groups': {
                'method': self.generic_get_object_facts,
                'kwargs': {
                    'name': 'hostgroup',
                },
            },
            'masking_views': {
                'method': self.generic_get_object_facts,
                'kwargs': {
                    'name': 'masking_view',
                },
            },
            'port_groups': {
                'method': self.generic_get_object_facts,
                'kwargs': {
                    'name': 'portgroup'
                },
            },
            'slo': {
                'method': self.generic_get_object_facts,
                'kwargs': {
                    'name': 'slo'
                },
            },
            'srp': {
                'method': self.generic_get_object_facts,
                'kwargs': {
                    'name': 'srp'
                },
            },
            'storage_groups': {
                'method': self.generic_get_object_facts,
                'kwargs': {
                    'name': 'storage_group'
                },
            },
            'volumes': {
                'method': self.generic_get_object_facts,
                'kwargs': {
                    'name': 'volume'
                },
            },
        }
    def generic_get_object_facts(self, name):
        ''' Generic Function to gather list of object types and get the details
         and return the dictionary of entries '''
        list_func = getattr(self.dellemc, 'get_%s_list' % name)
        get_func = getattr(self.dellemc, 'get_%s' % name)
        results = {}
        for i in list_func():
            tmp_data = get_func(i)
            try:
                getattr(tmp_data, 'success')
            except AttributeError:
                # We are on Unisphere 9.x or above. As they don't have an
                # attribute success
                results[i] = tmp_data
            else:
                # We are on Unisphere 8.x. They present a sub key with a
                # list of results.. Which is always 1 item in the list
                key = [key for key in tmp_data.keys() if key != 'success'][0]
                results[i] = tmp_data[key]
        return results

    def get_data(self):
        self.run_subset = self.get_subset()
        facts = {}
        for subset in self.run_subset:
            call = self.fact_subsets[subset]
            facts[subset] = call['method'](**call['kwargs'])
        return facts

    def get_subset(self):
        ''' Gathers a list of objects to gather facts on based on the
        module inputs '''
        runable_subsets = set()
        exclude_subsets = set()
        for subset in self.gather_subset:
            if subset == 'all':
                runable_subsets.update(self.fact_subsets.keys())
                return runable_subsets
            if subset.startswith('!'):
                subset = subset[1:]
                if subset == 'all':
                    return set()
                exclude = True
            else:
                exclude = False
            if subset not in self.fact_subsets.keys():
                module.fail_json(msg='Bad subset')
            if exclude:
                exclude_subsets.add(subset)
            else:
                runable_subsets.add(subset)
        if not runable_subsets:
            runable_subsets.update(self.fact_subsets.keys())
        runable_subsets.difference_update(exclude_subsets)
        return runable_subsets

def main():
    argument_spec = dellemc_pmax_argument_spec()
    argument_spec.update(dict(
            gather_subset=dict(default=['all'], type='list'),
        )
    )
    module = AnsibleModule(argument_spec=argument_spec,
        supports_check_mode=True)
    ### Get the Subset of objects to collect
    d = Dellpmax_Gather_Facts(module)
    facts = d.get_data()
    result = {'state': 'info', 'changed': False}
    module.exit_json(ansible_facts={'dellemc_pmax_facts': facts}, **result)


if __name__ == '__main__':
    main()


