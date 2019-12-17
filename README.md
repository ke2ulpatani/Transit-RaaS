# Multi Cloud Transit VPC based Routing as a Service


## /etc :
This directory is where tenants place their config files (We have populated this directory for demo purposes)

## /var : 
This directory is where any run time information and logs are placed

## /logic :
This directory is where all the core processing logic and Ansible playbooks

## execute.sh that is used to run as the driver code in order to create VPCs, Spines, Leaves, L1 Transits or L2 Transit Nodes.

### constants.py :
Has a set of pre defined constants and paths

### create-vms.yml :
Define, Start and Attach interface to VMs  

### create_leaf.py : 
Used to create leaf nodes that hosts a subnet with one or more multiple PCs 

### create_spine.py :
Used to create spines, L1 transits and L2 transits nodes

### create_vpc.py :
Used to create a VPC

### hyp_utils.py :
Utitlity functions that are built to work on the JSON file stored on the hypervisor, which is used to keep track of all nodes that are owned by all tenants.

## raas_utils.py :
Utility functions that are built to work on the JSON file stored in the /var directory of every tenant, that is used to keep track of all nodes that are owned by the said tenant.

