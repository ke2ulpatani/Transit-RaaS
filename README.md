# Transit_RaaS

## Run below playbook steps to configure a client, more than one vpcs, transit vpc

### Setup Tenant 1:
sudo ansible-playbook client-setup.yml -i inventory/hosts.yml -K --extra-vars @vars/c1_setup.yml

### Create VPC 1 for Tenant 1:
sudo ansible-playbook create-vpc.yml -i inventory/hosts.yml -K --extra-vars @vars/c1v1.yml  

### Create VPC 2 for Tenant 1:
sudo ansible-playbook create-vpc.yml -i inventory/hosts.yml -K --extra-vars @vars/c1v2.yml 

### Create and configure Transit for Tenant 1 on hypervisor 2:
sudo ansible-playbook create-transit.yml -i inventory/hosts.yml -K --extra-vars @vars/c1h1.yml
sudo ansible-playbook configure-transit.yml -i inventory/hosts.yml -K --extra-vars @vars/c1h1.yml

### Create subnet:
sudo ansible-playbook main.yml -i inventory/hosts.yml

### Connect leaf gateway to spine gateways:
Update all the leaf's yml config file in leaf folder then run: sudo sh run.sh

## GRE and BGP configuration
1. conf_spine_bgp.sh - Configures BGP on spine router VMs
2. conf_transit_bgp.sh - Configures BGP on transit router VMs
3. gre_endpoint_setup_bgp.sh - Configures GRE related underlay configuration on hypervisors
4. gre_endpoint_setup_transit.sh - Configures GRE related underlay configuration on transit VMs
5. gre_setup_transit.sh - Configures GRE devices on transit VMs
6. conf_inter_transit_bgp.sh - Configures BGP between transit VMs across hypervisors.
