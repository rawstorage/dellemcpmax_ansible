#!/usr/bin/python


from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'VMAX REST API Community '
                                    'https://community.emc.com/docs/DOC-56447'
                    }
DOCUMENTATION = r'''
---
module: dellpmax_createsg

contributors: Paul Martin, Rob Mortell

software versions=ansible 2.6.2
                  python version = 2.7.15rc1 (default, Apr 15 2018,

short_description: 
    -Module to create a Masking view to provision storage to a host.  
    
requirements:
    -Storage Group, Host or Host Group and Port Group must already exist for 
    this to run sucessfully.

notes:
    - This module has been tested against UNI 9.0.  Every effort has been 
    made to verify the scripts run with valid input.  These modules 
    are a tech preview.  Additional error handling will be added at a later 
    date, base functionality only right now.



Requirements:
    - Ansible, Python 2.7, Unisphere for PowerMax version 9.0 or higher. 
    VMAX All Flash, VMAX3, or PowerMAX storage Array



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
    host_name:
         description:
            -  String value to denote Hostname or Cluster, No Special 
            character except for _.  Case sensistive for REST Calls. Host 
            must exist
        required:True
    portgroup:
        description:
            - Name of Port Group to provision storage volume to host.  
            Must already be created.  It is assumed host HBA is already 
            zoned for access to front end ports.           
        required:True
    
    storagegroup:
        description:
            - Name of storage Group to provision storage volume to host.  
            Must already be created  
        required:True
    maskingview:
        description:
            - Name ot be assigned to new Masking view, it is assumed this 
            name must be unique and is case sensitive.  cahracter lmiits are 
            same as storage group
        required: True 
            
    async:
        Optional Parameter to set REST call to run Asyncronously, job will 
        be submitted to job queue and executed.  Task Id will be returned in 
        JSON for lookup purposed to check job completion status. 

'''

EXAMPLES = r'''
- name: Create Host
  hosts: localhost
  connection: local
  vars:
        unispherehost: '192.168.20.63'
        uniport: 8443
        universion: "90"
        verifycert: False
        user: 'smc'
        password: 'smc'
        array_id: "000197600123"
  tasks:
    - name: Create Masking View for Host Access
    dellpmax_createmaskingview:
             unispherehost: "{{unispherehost}}"
             universion: "{{universion}}"
             verifycert: "{{verifycert}}"
             user: "{{user}}"
             password: "{{password}}"
             array_id: "{{array_id}}"
             host_or_cluster: "AnsibleCluster"
             sgname: "{{sgname}}"
             pg_id: "Ansible_PG"
             maskingview_id: "MyMaskingView"
'''
RETURN = r'''
'''


def main():
    changed = False
    # print (changed)
    module = AnsibleModule(
        argument_spec=dict(
            unispherehost=dict(required=True),
            universion=dict(type='int', required=False),
            verifycert=dict(type='bool', required=True),
            user=dict(type='str', required=True),
            password=dict(type='str', required=True),
            array_id=dict(type='str', required=True),
            sgname = dict(type='str', required=True),
            host_or_cluster=dict(type='str', required=True),
            pg_id=dict(type='str', required=True),
            maskingview_id=dict(type='str', required=True),
            compliancealterts=dict(type='bool',required=False)

        )
    )
    # Make REST call to Unisphere Server and execute create Host

    payload = (
        {
            "portGroupSelection": {
                "useExistingPortGroupParam": {
                    "portGroupId": module.params['pg_id']
                }
            },
            "maskingViewId": module.params['maskingview_id'],
            "hostOrHostGroupSelection": {
                "useExistingHostGroupParam": {
                    "hostGroupId": module.params['host_or_cluster']
                }
            },
            "storageGroupSelection": {
                "useExistingStorageGroupParam": {
                    "storageGroupId": module.params['sgname']
                }
            },
            "enableComplianceAlerts": True
        }
    )

    headers = ({

        'Content-Type': 'application/json'

    })

    resource_url = "https://{}:8443/univmax/restapi/{}/sloprovisioning/" \
                   "symmetrix/{}/maskingview/".format \
        (module.params['unispherehost'], module.params['universion'],
         module.params['array_id'])
    verify = module.params['verifycert']
    username = module.params['user']
    password = module.params['password']
    print(resource_url)
    open_url(url=resource_url, data=json.dumps(payload), timeout=600,
             headers=headers, method="POST",
             validate_certs=verify, url_username=username,
             url_password=password, force_basic_auth=True)

    module.exit_json(changed=True)


from ansible.module_utils.basic import *
from ansible.module_utils.urls import *

if __name__ == '__main__':
    main()


