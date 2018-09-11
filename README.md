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

ansible-playbook createemptysg.yml -vvv
ansible-playbook 2.6.2
  config file = /etc/ansible/ansible.cfg
  configured module search path = [u'/root/.ansible/plugins/modules', u'/usr/share/ansible/plugins/modules']
  ansible python module location = /usr/lib/python2.7/dist-packages/ansible
  executable location = /usr/bin/ansible-playbook
  python version = 2.7.15rc1 (default, Apr 15 2018, 21:51:34) [GCC 7.3.0]
Using /etc/ansible/ansible.cfg as config file
Parsed /etc/ansible/hosts inventory source with ini plugin

PLAYBOOK: createemptysg.yml *****************************************************************************************************************************************************************************************************************
1 plays in createemptysg.yml

PLAY [Simple Sample Playbook] ***************************************************************************************************************************************************************************************************************

TASK [Gathering Facts] **********************************************************************************************************************************************************************************************************************
task path: /createemptysg.yml:1
<127.0.0.1> ESTABLISH LOCAL CONNECTION FOR USER: root
<127.0.0.1> EXEC /bin/sh -c 'echo ~root && sleep 0'
<127.0.0.1> EXEC /bin/sh -c '( umask 77 && mkdir -p "` echo /root/.ansible/tmp/ansible-tmp-1536663703.03-138967398531468 `" && echo ansible-tmp-1536663703.03-138967398531468="` echo /root/.ansible/tmp/ansible-tmp-1536663703.03-138967398531468 `" ) && sleep 0'
Using module file /usr/lib/python2.7/dist-packages/ansible/modules/system/setup.py
<127.0.0.1> PUT /root/.ansible/tmp/ansible-local-10163TSOlPA/tmpyr0eoO TO /root/.ansible/tmp/ansible-tmp-1536663703.03-138967398531468/setup.py
<127.0.0.1> EXEC /bin/sh -c 'chmod u+x /root/.ansible/tmp/ansible-tmp-1536663703.03-138967398531468/ /root/.ansible/tmp/ansible-tmp-1536663703.03-138967398531468/setup.py && sleep 0'
<127.0.0.1> EXEC /bin/sh -c '/usr/bin/python /root/.ansible/tmp/ansible-tmp-1536663703.03-138967398531468/setup.py && sleep 0'
<127.0.0.1> EXEC /bin/sh -c 'rm -f -r /root/.ansible/tmp/ansible-tmp-1536663703.03-138967398531468/ > /dev/null 2>&1 && sleep 0'
ok: [localhost]
META: ran handlers

TASK [Create New Empty Storage Group] *******************************************************************************************************************************************************************************************************
task path: /createemptysg.yml:13
<127.0.0.1> ESTABLISH LOCAL CONNECTION FOR USER: root
<127.0.0.1> EXEC /bin/sh -c 'echo ~root && sleep 0'
<127.0.0.1> EXEC /bin/sh -c '( umask 77 && mkdir -p "` echo /root/.ansible/tmp/ansible-tmp-1536663703.62-184754246264574 `" && echo ansible-tmp-1536663703.62-184754246264574="` echo /root/.ansible/tmp/ansible-tmp-1536663703.62-184754246264574 `" ) && sleep 0'
Using module file /usr/lib/python2.7/dist-packages/ansible/modules/storage/dellemc/dellpmax_create_emptysg.py
<127.0.0.1> PUT /root/.ansible/tmp/ansible-local-10163TSOlPA/tmpXhr5QU TO /root/.ansible/tmp/ansible-tmp-1536663703.62-184754246264574/dellpmax_create_emptysg.py
<127.0.0.1> EXEC /bin/sh -c 'chmod u+x /root/.ansible/tmp/ansible-tmp-1536663703.62-184754246264574/ /root/.ansible/tmp/ansible-tmp-1536663703.62-184754246264574/dellpmax_create_emptysg.py && sleep 0'
<127.0.0.1> EXEC /bin/sh -c '/usr/bin/python /root/.ansible/tmp/ansible-tmp-1536663703.62-184754246264574/dellpmax_create_emptysg.py && sleep 0'
<127.0.0.1> EXEC /bin/sh -c 'rm -f -r /root/.ansible/tmp/ansible-tmp-1536663703.62-184754246264574/ > /dev/null 2>&1 && sleep 0'
 [WARNING]: Module did not set no_log for password


changed: [localhost] => {
    "changed": true,
    "invocation": {
        "module_args": {
            "array_id": "000197600123",
            "password": "xxxxxxxx",
            "sgname": "Ansible_EMPTYSG",
            "slo": "Diamond",
            "srp_id": "SRP_1",
            "unispherehost": "192.168.156.63",
            "universion": 90,
            "user": "smc",
            "verifycert": false,
            "workload": "None"
        }
    }
}
META: ran handlers
META: ran handlers

PLAY RECAP **********************************************************************************************************************************************************************************************************************************
localhost                  : ok=2    changed=1    unreachable=0    failed=0
