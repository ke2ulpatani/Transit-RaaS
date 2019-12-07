import os
import sys
import do_json
import raas_utils
import hyp_utils
import constants
import ipaddress

"""@params:
    param1 = connection config name (required)
"""

if __name__=="__main__":
    if (len(sys.argv) < 2):
        print("Please give connection config file")
        exit(1)

    connection_config_file = sys.argv[1]
    connection_name = pc_config_file.split('/')[-1].split('.')[0]
    cid = hyp_utils.get_client_id()

    connection_data = do_json.json_read(connection_config_file)
    vpc_name = connection_data["vpc_name"]
    pc_name = connection_data["pc_name"]
    leaf_name = connection_data["leaf_name"]

    if raas_utils.client_exists_pc(vpc_name, pc_name):
        print("pc does not exists")
        exit(1)

    if raas_utils.client_exists_leaf(vpc_name, leaf_name):
        print("leaf does not exist")
        exit(1)

    pc_hypervisor_name = connection_data["pc_hypervisor_name"]
    leaf_hypervisor_name = connection_data["leaf_hypervisor_name"]

    if (pc_hypervisor_name == leaf_hypervisor_name):
        print("pc and leaf exist in same hypervisor, direct connect")
        hypervisor = pc_hypervisor_name
        hypervisor_arg = "hypervisor="+hypervisor
        hypervisors_data = hyp_utils.get_hypervisors_data()
        hypervisor_ip = hyp_utils.get_hyp_ip(hypervisor)

        try:
            #connect pc to leaf
            try:
                hyp_pc_name = hyp_utils.get_hyp_pc_name(hypervisor, vpc_name, pc_name)

                pc_name_ansible_arg = "pc_name=" + hyp_pc_name

                hyp_leaf_name = hyp_utils.get_hyp_leaf_name(hypervisor, vpc_name, leaf_name)

                net_name = hyp_leaf_name + "_net"

                net_name_arg = "net_name_arg=" + net_name

                extra_vars = constants.ansible_become_pass + " " + \
                        pc_name_ansible_arg + " " + \
                        net_name_arg + " " +  hypervisor_arg

                #print("here2")
                print("ansible-playbook logic/subnet/add_to_subnet.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
                raise
                rc = os.system("ansible-playbook logic/subnet/add_to_subnet.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
                if (rc != 0):
                    raise
                    
                hyp_utils.write_pc_id(pcid+1, vpc_name, hypervisor)
                #print("here4", pc_name, vpc_name, hypervisor, pc_name_ansible)
                hyp_utils.vpc_add_pc(hypervisor, vpc_name, pc_name, pc_name_ansible)
                raas_utils.client_add_pc(vpc_name, pc_name)

                #raise
                #raas_utils.add_mgmt_ns(hypervisor)
            except:
                print("connect pc failed")
                raise
            #print("ansible-playbook logic/vpc/delete_pc.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")

        except:
            print("create pc failed python failed")

    else:
        print("pc and leaf exist in different hypervisor, vxlan connect")
        exit(1)



    
    

