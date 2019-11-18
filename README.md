# Transit_RaaS

Run below playbook steps to configure a client, more than one vpcs, transit vpc

sudo ansible-playbook client-setup.yml -i inventory/hosts.yml -K --extra-vars @vars/c1_setup.yml

sudo ansible-playbook create-vpc.yml -i inventory/hosts.yml -K --extra-vars @vars/c1v1.yml  #Created
sudo ansible-playbook create-vpc.yml -i inventory/hosts.yml -K --extra-vars @vars/c1v2.yml  #Created

sudo ansible-playbook create-transit.yml -i inventory/hosts.yml -K --extra-vars @vars/c1h1.yml
sudo ansible-playbook configure-transit.yml -i inventory/hosts.yml -K --extra-vars @vars/c1h1.yml
