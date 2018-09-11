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


Example--
createemptysg.yml

- name: Simple Sample Playbook
  hosts: localhost
  connection: local
  vars:
        unispherehost: '10.60.156.63'
        universion: "90"
        verifycert: False
        user: 'smc'
        password: 'smc'
        sgname: 'Ansible_EMPTYSG'
        array_id: '000197600156'
  tasks:
  - name: Create New Empty Storage Group
    dellpmax_create_emptysg:
        unispherehost: "{{unispherehost}}"
        universion: "{{universion}}"
        verifycert: "{{verifycert}}"
        user: "{{user}}"
        password: "{{password}}"
        sgname: "{{sgname}}"
        array_id: "{{array_id}}"
        srp_id: 'SRP_1'
        slo: 'Diamond'
        workload: None
