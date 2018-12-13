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
module: dellpmax_createsg

Author: Paul Martin @rawstorage

Contributors: Rob Mortell @robmortell

software versions=ansible 2.6.2
                  python version = 2.7.15rc1 (default, Apr 15 2018,
                  
short_description: module to Protect a storage group on Dell EMC PowerMax 
with SRDF VMAX All Flash or VMAX3 storage arrays.


notes:
    - This module has been tested against UNI 9.0.    Every effort has been 
    made to verify the scripts run with valid input.  These modules 
    are a tech preview.  Additional error handling will be added at a later 
    date, base functionality only right now.

Requirements:
    - Ansible, Python 2.7, Unisphere for PowerMax version 9.0 or higher. 
    VMAX All Flash, VMAX3, or PowerMax storage Array
    Also requires PyU4V to be installed from PyPi using PIP
    python -m pip install PyU4V

playbook options:
    Note:- Some Options are repeated across modules, we will look at 
    reducing these in future work, however you can use variables in your 
    playbook at the outset and reference in the task to reduce error, 
    this also allows flexibility in versioning within a single playbook.   
    
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
    sgname:
        description:
            - Storage Group name
        required:True     
    array_id:
        description:
            - Integer 12 Digit Serial Number of PowerMAX or VMAX array.
        required:True


'''

EXAMPLES = r'''
- name: Create Storage Group
  hosts: localhost
  connection: local
  no_log: True
  vars:
        unispherehost: '192.168.156.63'
        universion: "90"
        verifycert: False
        user: 'smc'
        password: 'smc'
        array_id: '000197600123'

  tasks:
   - name: Protect Storage Group with SRDF
    dellpmax_createsg:
        unispherehost: "{{unispherehost}}"
        universion: "{{universion}}"
        verifycert: "{{verifycert}}"
        user: "{{user}}"
        password: "{{password}}"
        sgname: "{{sgname}}"
        array_id: "{{array_id}}"
        remote_array_id:"000197600124"
        srdfmode: 'Active'
        establish: True       
'''
RETURN = r'''
'''

def main():
    module = AnsibleModule(
        argument_spec=dict(
            sgname=dict(type='str',required=True),
            unispherehost=dict(required=True),
            universion=dict(type='int', required=False),
            verifycert=dict(type='bool', required=True),
            user=dict(type='str', required=True),
            password=dict(type='str', required=True, no_log=True),
            array_id=dict(type='str', required=True),
            remote_sid=dict(type='int', required=True),
            srdfmode=dict(type='str', required=True, choices=['Active',
                        'AdaptiveCopyDisk','Synchronous', 'Asynchronous']),
            establish=dict(type='bool', required=False),
            rdfg_number=dict(type='int', required=False)
        )
    )

    conn = PyU4V.U4VConn(server_ip=module.params['unispherehost'], port=8443,
                         array_id=module.params['array_id'],
                         verify=module.params['verifycert'],
                         username=module.params['user'],
                         password=module.params['password'],
                         u4v_version=module.params['universion'])
    remoteconn = PyU4V.U4VConn(server_ip=module.params['unispherehost'],
                               port=8443,
                         array_id=module.params['remote_sid'],
                         verify=module.params['verifycert'],
                         username=module.params['user'],
                         password=module.params['password'],
                         u4v_version=module.params['universion'])

    # Make REST call to Unisphere Server and execute create storage group

    changed = False
    # Compile a list of existing storage groups.

    sglist = dellemc.provisioning.get_storage_group_list()
    remotesglist = remoteconn.provisioning.get_storage_group_list()

    # Check if Storage Group  exists

    if module.params['sgname'] in sglist and module.params['sgname'] not in \
            remotesglist :
        if dellemc.replication.get_storage_group_rep(storage_group_name
                                                     = module.params[
            'sgname'])["rdf"]=false:
            conn.replication.create_storagegroup_srdf_pairings(
                storagegroup_id=module.params['sgname'],
                remote_sid=module.params['remote_sid'],
                srdfmode=module.params['srdfmode'],
                establish=module.params['establish'],
                async=True,rdfg_number=None)
            changed = True
    else:
        module.fail_json(msg='Storage Group is already SRDF Protected, '
                             'or a storage group with the same names already '
                             'exists on the remote array, check input '
                             'parameters')
    else:
        module.fail_json(msg='Storage Group Does not Exists')

    module.exit_json(changed=changed)



from ansible.module_utils.basic import *
from ansible.module_utils.urls import *

if __name__ == '__main__':
    main()


