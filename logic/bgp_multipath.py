import os
import sys
import do_json
import raas_utils
import hyp_utils
import constants
import ipaddress

"""@params:
    param1 = bgp config file (required)
"""

if __name__=="__main__":
    if (len(sys.argv) < 2):
        print("Please give bgp config file")
        exit(1)

    multipath_file = sys.argv[1]

    #pc_name = pc_config_file.split('/')[-1].split('.')[0]

    #Assumed customer always gives correct config file
    multipath_data = do_json.json_read(multipath_file)

    hypervisor = multipath_data["hypervisor_name"]
    hypervisor_arg = "hypervisor="+hypervisor

    hypervisors_data = hyp_utils.get_hypervisors_data()
    hypervisor_ip = hyp_utils.get_hyp_ip(hypervisor)
    
    node_type = multipath_data["node_type"]

    vpc_name = ""
    #check if vpc exists for spine
    if (node_type == "spine")
        vpc_name = multipath_data["vpc_name"]
        if not raas_utils.client_exists_vpc(vpc_name):
            print("VPC does not exist")
            exit(1)

    node_name = multipath_data["node_name"]
    node_name_arg = "c_name=" node_name

    if not check_exists(node_type, node_name, vpc_name):
        print("Node does not exists")
        exit(1)

    client_node_data = raas_utils.get_client_node_data(node_type, node_name, vpc_name):

    activate = multipath_data["activate"]
    self_as_arg = "self_as="client_node_data["self_as"]
    
    try:
        #create_pc
        try:
            extra_vars = constants.ansible_become_pass + " " + \
                    node_name_arg + self_as_arg +\
                    " " + hypervisor_arg

            raas_utils.run_playbook("ansible-playbook logic/misc/create_container.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
                
            hyp_utils.write_pc_id(pcid+1, vpc_name, hypervisor)
            hyp_utils.vpc_add_pc(hypervisor, vpc_name, pc_name, pc_name_ansible)
            raas_utils.client_add_pc(hypervisor, vpc_name, pc_name, pc_capacity)
        except:
            print("create pc failed")
            raas_utils.run_playbook("ansible-playbook logic/misc/delete_container.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            raise
    except:
        print("create pc failed python failed")
