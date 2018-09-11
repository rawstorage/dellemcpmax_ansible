# dellemcpmax_ansible
Library of Modules and Sample Runbooks for Dell EMC PowerMax &amp; VMAX customers to integrate with Ansible

requirements:
    - Ansible, Python 2.7, Unisphere for PowerMax version 9.0 or higher. 
    VMAX All Flash, VMAX3, or PowerMAX storage Array
    
    Installation Instructions

Copy contents of Library Directory to 

/usr/lib/python2.7/dist-packages/ansible/modules/storage/dellemc

Playbooks can then be run from any working directory with ansible-playbook commands

Before running any dellemc modules as part of your playbooks, you will need to install additional python modules.

Requires PyU4V installable from PIP

apt-get install python-pip

pip install PyU4V



