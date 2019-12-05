#!/bin/python

#ansible-playbook release.yml --extra-vars=@some_file --extra-vars=@some_other_file

def create_customer_vm():
    ansible_command = "ansible-playbook -i ./etc/customer_vm/inventory/hosts.yml ./etc/customer_vm/main.yml"
    print os.system(ansible_command)

def connect_leaf_spine():
    shell_command = "./etc/connect_leaf_spine/run.sh"
    print os.system(shell_command)

if __name__ == "__main__":
    create_customer_vm()
    connect_leaf_spine()
