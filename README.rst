# dellemcpmax_ansible

| |Maintenance| |OpenSource| |AskUs| |License|

Update July 17th 2019 - Official modules from Dell EMC are now provided with full support.  Functionality will differ slighly from the open source modules so you will need to review the differences if you plan to siwtch over.

Official modules are available here

https://github.com/dell/ansible-powermax/tree/master/dellemc_ansible

Blog Here
https://rawstorage.wordpress.com/2019/07/16/dell-emc-official-ansible-modules-for-powermax-v1-0/


The OpenSource Project will continue in the background but expectation is that the official modules will become part of Core at some stage and these ones will not be required although customers are free to develop on this code base for their own use.  The API calls will be supported in the usual way.

Library of Modules and Sample Runbooks for Dell EMC PowerMax &amp; VMAX customers to integrate with Ansible

Support Information

While every effort has been made to ensure that these modules are working as intended, there is no formal support.  These modules are intended to provide examples and users should test thoroughly before using in theirenvironments.  The template module is provided for people to be able to quickly implement their own functionality.

If you do run into an issue please open an issue against the GitHub repository and it will be resolved by one of the contributors.

Feedback is always welcome, we hope you find these examples useful.

requirements:
    - Ansible, Python 2.7 or higher, Unisphere for PowerMax version 9.0 or higher.VMAX All Flash, VMAX3, or PowerMAX storage Array

Installation Instructions

Copy dellemc Directory to

/usr/lib/python2.7/dist-packages/ansible/modules/storage/

copy dellemc.py file in module_utils to

/usr/lib/python2.7/dist-packages/ansible/module_utils

If you have installed Unisphere to use a non-default port you can change in this file line 29

Playbooks can then be run from any working directory with ansible-playbook commands

Before running any dellpmax modules as part of your playbooks, you will need to install additional python modules.

Requires PyU4V minimum version 3.0.0.9 Please follow installation instructions on the GitHub

https://github.com/MichaelMcAleer/PyU4V

Note in environments we've seen some failures where it was required to add environment variable to the playbook, this manifested itself as https errors and error code 503.

    environment:
        no_proxy: "*"


All modules are fully documented with sample task code in and return data,

To check how each can be consumed and what parameters are required please use ansible documentation commands to inspect:
e.g.

ansible-doc -t module dellemc_pmax_manage_snap




.. BadgeLinks

.. |Maintenance| image:: https://img.shields.io/badge/Maintained-No-Red
   :target: https://github.com/rawstorage/dellemcpmax_ansible/master
.. |OpenSource| image:: https://img.shields.io/badge/Open%20Source-Yes-blue
   :target: https://github.com/rawstorage/dellemcpmax_ansible/
.. |AskUs| image:: https://img.shields.io/badge/Ask%20Us...-Anything-blue
   :target: https://github.com/rawstorage/dellemcpmax_ansible/issues
.. |License| image:: https://img.shields.io/badge/License-AGPL%20v3-blue
   :target: https://github.com/rawstorage/dellemcpmax_ansible/blob/master/LICENSE



