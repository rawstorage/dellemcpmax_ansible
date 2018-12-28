# dellemcpmax_ansible
Library of Modules and Sample Runbooks for Dell EMC PowerMax &amp; VMAX customers to integrate with Ansible

requirements:
    - Ansible, Python 2.7, Unisphere for PowerMax version 9.0 or higher. 
    VMAX All Flash, VMAX3, or PowerMAX storage Array
    
    Installation Instructions

Copy dellemc Directory to 

/usr/lib/python2.7/dist-packages/ansible/modules/storage/

copy dellemc.py file in module_utils to 

/usr/lib/python2.7/dist-packages/ansible/module_utils

Playbooks can then be run from any working directory with ansible-playbook commands

Before running any dellpmax modules as part of your playbooks, you will need to install additional python modules.

Requires PyU4V Please follow installation instructions on the GitHub

https://github.com/ciarams87/PyU4V

Note in environments we've seen some failures where it was required to add environment variable to the playbook, this manifested itself as https errors and error code 503.

    environment:
        no_proxy: "*"

All modules are fully documented with sample task code in and return data, 

To check how each can be consumed and what parameters are required please 
use ansible documentation commands to inspect:

e.g.

ansible-doc -t module dellemc_pmax_manage_snap