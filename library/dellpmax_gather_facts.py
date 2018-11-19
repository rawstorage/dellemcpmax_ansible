#!/usr/bin/python
from ansible.module_utils.six.moves.urllib.error import HTTPError

__metaclass__ = type
import PyU4V

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'VMAX REST API Community '
                                    'https://community.emc.com/docs/DOC-56447'
                    }
DOCUMENTATION = r'''
---
module: dellpmax_gather_facts

Author: Corey Wanless @coreywan

software versions=ansible 2.7.1
                  python version = 2.7.15rc1 (default, Apr 15 2018,

short_description: 
    Module to gather facts about PowerMAX array.

notes:
    -  These modules are a tech preview.
    Additional error handling will be added at a later
    date, base functionality only right now.



Requirements:
    - Ansible, Python 2.7, Unisphere for PowerMax version 9.0 or higher. 
    VMAX All Flash, VMAX3, or PowerMAX storage Array. Python module PyU4V 
    also needs to be installed from pip or PyPi



playbook options:
    unispherehost:
        description:
            - Full Qualified Domain Name or IP address of Unisphere for 
            PowerMax host.
        required:True

    universion:
        -description:
            - Integer, version of unipshere software 
            https://{HostName|IP}:8443/univmax/restapi/{version}/{resource}
            90 is the release at time of writing module.
        -required:True
    verifycert:
        description: 
            -Boolean, securitly check on ssl certificates
        required:True             

        required: True
    array_id:
        description:
            - Integer 12 Digit Serial Number of PowerMAX or VMAX array.
        required:True
    gather_subset:
        description:
            - Optional parameter to tell ansible which facts to gather about the system.
                Possible values for this argument include
                hosts, host_groups, masking_views, port_groups,
                slo, srp, storage_groups, volumes
                Can specify a list of values to include a larger subset.  Values can also be used
                with an initial C(M(!)) to specify that a specific subset should
                not be collected.
        default: "all"
        required: false
'''

EXAMPLES = r'''
    - name: Gather all facts except for the volumes
      dellpmax_gather_facts:
        unispherehost: "{{unispherehost}}"
        universion: "{{universion}}"
        verifycert: "{{verifycert}}"
        user: "{{user}}"
        password: "{{password}}"
        array_id: "{{array_id}}"
        gather_subset: "!volumes"
    - debug: var=dellpmax_facts

    - name: Gather only storage_groups and masking_views facts
      dellpmax_gather_facts:
        unispherehost: "{{unispherehost}}"
        universion: "{{universion}}"
        verifycert: "{{verifycert}}"
        user: "{{user}}"
        password: "{{password}}"
        array_id: "{{array_id}}"
        gather_subset:
          - storage_groups
          - masking_views
    - debug: var=dellpmax_facts
'''
RETURN = r'''
dellpmax_facts:
    description: Returns various information about PowerMAX Array
    returned: always
    type: dict
    sample: '{
        "dellpmax_facts": {
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

class Dellpmax_Gather_Facts(object):
    def __init__(self,module):
        self.module = module
        self.conn = PyU4V.U4VConn(server_ip=module.params['unispherehost'], port=8443,
                         array_id=module.params['array_id'],
                         verify=module.params['verifycert'],
                         username=module.params['user'],
                         password=module.params['password'],
                         u4v_version=module.params['universion'],
                         )
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
        ''' Generic Function to gather list of object types and get the details and return the dictionary of entries '''
        list_func = getattr(self.dellemc, 'get_%s_list' % name)
        get_func = getattr(self.dellemc, 'get_%s' % name)
        results = {}
        for i in list_func():
            tmp_data = get_func(i)
            try:
                getattr(tmp_data, 'success')
            except AttributeError:
                # We are on Unisphere 9.x or above. As they dont have an attribute success
                results[i] = tmp_data
            else:
                # We are on Unisphere 8.x. They present a sub key with a list of results.. Which is always 1 item in the list
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
        ''' Gathers a list of objects to gather facts on based on the module inputs '''
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
    module = AnsibleModule(
        argument_spec=dict(
            unispherehost=dict(required=True),
            universion=dict(type='int', required=False),
            verifycert=dict(type='bool', required=True),
            user=dict(type='str', required=True),
            password=dict(type='str', required=True),
            array_id=dict(type='str', required=True),
            gather_subset=dict(default=['all'], type='list'),
        ),
        supports_check_mode=True,
    )

    ### Get the Subset of objects to collect
    d = Dellpmax_Gather_Facts(module)
    facts = d.get_data()
    result = {'state': 'info', 'changed': False}
    module.exit_json(ansible_facts={'dellpmax_facts': facts}, **result)

from ansible.module_utils.basic import *
from ansible.module_utils.urls import *

if __name__ == '__main__':
    main()


