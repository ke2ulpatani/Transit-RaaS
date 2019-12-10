import json
import os
import hyp_utils
import raas_utils
import sys
import constants

def _finditem(obj, key, containers):
    if key in obj: 
        containers.append(obj[key])
    for k, v in obj.items():
        if isinstance(v,dict):
            item = _finditem(v, key, containers)
            if item is not None:
                containers.append(item)


def create_checkpoint(pod,version,hypervisor):
      hypervisor_arg = " hypervisor="+hypervisor
      pod_arg= " pod="+pod
      version_arg= " version="+version
      extra_vars = constants.ansible_become_pass + hypervisor_arg + pod_arg + version_arg
      
      rc = raas_utils.run_playbook("ansible-playbook logic/checkpoint/create_checkpoint.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")    
#      if (rc != 0):
#          raas_utils.log_service ("create checkpoint failed")

def restore_pod_checkpoint(pod,version,hypervisor):
      hypervisor_arg = " hypervisor="+hypervisor
      pod_arg= " pod="+pod
      version_arg= " version="+version
      extra_vars = constants.ansible_become_pass + hypervisor_arg + pod_arg + version_arg
      
      rc = raas_utils.run_playbook("ansible-playbook logic/checkpoint/restore_checkpoint.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")    
#      if (rc != 0):
#          raas_utils.log_service ("restore checkpoint failed")


if (len(sys.argv) < 2):
    raas_utils.log_service("Please give correct arguments <checkpoint/restore> <version>")
    exit(1)

with open('var/hypervisors.json') as tenant_file:
    
    action=sys.argv[1]
    version=sys.argv[2]

    data = json.load(tenant_file)
    
    nodes=[]

    h1_cns=[]
    _finditem(data['h1'],'name',h1_cns)
    nodes.append(['h1',h1_cns])

    h2_cns=[]
    _finditem(data['h2'],'name',h1_cns)
    nodes.append(['h2', h2_cns])

    for node_cns in nodes:
        hypervisor=node_cns[0]
        pods=node_cns[1]
        for pod in pods:
            parts=pod.split('_')
            if len(parts)==2 and "v" in parts[1]:
                continue
            if(action == 'checkpoint'):
                create_checkpoint(pod,version,hypervisor)
            if(action == 'restore'):
                restore_pod_checkpoint(pod,version,hypervisor)
