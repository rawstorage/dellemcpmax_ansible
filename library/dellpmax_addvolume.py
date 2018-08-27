#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2017, Simon Dodsley (simon@purestorage.com)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'
                    }
DOCUMENTATION = r'''
---
module: dellpmax_createsg

contributors: Paul Martin, Robin Mortell

software versions=ansible 2.6.2
                  python version = 2.7.15rc1 (default, Apr 15 2018,

short_description: 
    module to add new volumes to existing storage group. This module can be 
    repeated multiple times in a playbook.

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
    port:
        description:
            - Port for REST to communicate with Unisphere server, default is 
            8443 however if unisphere was installed with a different port 
            you will need to change.
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
    srp_id:
        description:
            - Storage Resource Pool Name, Default is set to SRP_1, if your 
            system has mainframe or multiple pools you can set this to a 
            different value to match your environemtn
        required:Optional
    slo:
        description:
            - Service Level for the storage group, Supported on VMAX3 and All 
            Flash and PoweMAX NVMe Arrays running PowerMAX OS 5978 and 
            above.  Default is set to Diamond, but user can override this.
        required: Optional
    workload:
        description:
            - Block workload type, optional and can only be set on VMAX3 
            Hybrid Storage Arrays.  Default None.
        required:Optional
    num_vols:
        description:
           - integer value for the number of volumes. Minimum is 1, module 
           will fail if less than one volume is specified or value is 0.

        notes:
            -if volumes are required of different sizes, addional tasks 
            should be added to playbooks to use dellpmax_addvolume module

        required:True
    vol_size:
        description:
            - Integer value for the size of volumes.  All volumes will be 
            created with same size.  Use dellpmax_addvol to add additional 
            volumes if you require different sized volumes once storage 
            group is created.
        required:True
    cap_unit: 
        description:
            - String value, Unit of capacity for GB,TB,MB or CYL
        required:Optional default is set to GB
    async:
        Optional Parameter to set REST call to run Asyncronously, job will 
        be submitted to job queue and executed.  Task Id will be returned in 
        JSON for lookup purposed to check job completion status. 
    volumeIdentifier:
        description:
        String up to 64 Characters no special character other than _ 
        Provides an optional name or ID to make volumes easily identified on 
        system hosts can run Dell EMC inq utility to identify volumes e.g.
        inq -identify device_name 
        required:Optional 

'''

EXAMPLES = r'''
- name: Create Storage Group
  hosts: localhost
  connection: local
  tasks:
  - name: Add Volume to Storage Group
    dellpmax_addvolume:
        unispherehost: 'IPaddress or Hostname '
        port: 8443
        universion: 90
        verifycert: False
        user: 'smc'
        password: 'smc'
        sgname: 'Ansible_SG'
        array_id: '0001976XXXX Full 12 Digit Serial of array'
        srp_id: 'SRP_1'
        num_vols: 1
        vol_size:  2
        cap_unit: 'GB'
        volumeIdentifier: 'AnsibleAddedVolume'
'''
RETURN = r'''
'''

''''
Sample payload
(
{
  "editStorageGroupActionParam": {
    "expandStorageGroupParam": {
      "addVolumeParam": {
        "num_of_vols": 1,
        "emulation": "FBA",
        "volumeIdentifier": {
          "identifier_name": "Ansibleaddedvolume",
          "volumeIdentifierChoice": "identifier_name"
        },
        "volumeAttribute": {
          "volume_size": "2",
          "capacityUnit": "GB"
        }
      }
    }
  }
})


'''


def main():
    changed = False
    # print (changed)
    module = AnsibleModule(
        argument_spec=dict(
            sgname=dict(type='str', required=True),
            unispherehost=dict(required=True),
            port=dict(type='str', required=True),
            universion=dict(type='int', required=False),
            verifycert=dict(type='bool', required=True),
            user=dict(type='str', required=True),
            password=dict(type='str', required=True),
            array_id=dict(type='str', required=True),
            srp_id=dict(type='str', required=False),
            slo=dict(type='str', required=False),
            workload=dict(type='str', required=False),
            num_vols=dict(type='int', required=True),
            vol_size=dict(type='int', required=True),
            cap_unit=dict(type='str', required=True),
            volumeIdentifier=dict(type='str', required=True)
        )
    )
    # Make REST call to Unisphere Server and execute create storage group/

    payload = (
        {
            "editStorageGroupActionParam": {
                "expandStorageGroupParam": {
                    "addVolumeParam": {
                        "num_of_vols": module.params['num_vols'],
                        "emulation": "FBA",
                        "volumeIdentifier": {
                            "identifier_name": module.params['volumeIdentifier'],
                            "volumeIdentifierChoice": "identifier_name"
                        },
                        "volumeAttribute": {
                            "volume_size": module.params['vol_size'],
                            "capacityUnit": module.params['cap_unit']
                        }
                    }
                }
            }
        }
    )

    headers = ({

        'Content-Type': 'application/json'

    })

    resource_url = "https://{}:{}/univmax/restapi/{}/sloprovisioning/symmetrix" \
                   "/{}/storagegroup/{}".format \
        (module.params['unispherehost'], module.params['port'],
         module.params['universion'], module.params['array_id'],
         module.params['sgname'])

    verify = module.params['verifycert']
    username = module.params['user']
    password = module.params['password']
    print(resource_url)
    open_url(url=resource_url, data=json.dumps(payload), timeout=400,
             headers=headers, method="PUT",
             validate_certs=verify, url_username=username,
             url_password=password, force_basic_auth=True)

    module.exit_json(changed=True)


from ansible.module_utils.basic import *
from ansible.module_utils.urls import *

if __name__ == '__main__':
    main()


