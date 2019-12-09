import os
import sys
import do_json
import raas_utils
import hyp_utils
import constants
import ipaddress
from logging import info as print
logging.basicConfig(filename='raas.log', filemode='a', format='%(asctime)s %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

"""@params:
    param1 = bgp config file (required)
"""

if __name__=="__main__":
    if (len(sys.argv) < 2):
        print("Please give bgp config file")
        exit(1)

    weight_file = sys.argv[1]

    #pc_name = pc_config_file.split('/')[-1].split('.')[0]

    #Assumed customer always gives correct config file
    weight_data = do_json.json_read(weight_file)

    hypervisor = weight_data["hypervisor_name"]
    hypervisor_arg = "hypervisor="+hypervisor

    hypervisors_data = hyp_utils.get_hypervisors_data()
    hypervisor_ip = hyp_utils.get_hyp_ip(hypervisor)
    
    node_type = weight_data["node_type"]
    path_choice_type = weight_data["path_choice_type"]

    vpc_name = ""
    #check if vpc exists for spine
    if (node_type == "spine"):
        vpc_name = weight_data["vpc_name"]
        if not raas_utils.client_exists_vpc(vpc_name):
            print("VPC does not exist")
            exit(1)

    if (path_choice_type == "spine"):
        vpc_name = weight_data["vpc_name"]
        if not raas_utils.client_exists_vpc(vpc_name):
            print("VPC does not exist")
            exit(1)

    node_name = weight_data["node_name"]
    path_choice_name = weight_data["path_choice"]

    if not raas_utils.check_exists(node_type, node_name, vpc_name) or \
       not raas_utils.check_exists(path_choice_type, path_choice_name, vpc_name):
        print("Either Node does not exists")
        exit(1)

    if (node_type == "spine"):
        node_name_hyp = hyp_utils.get_hyp_spine_name(hypervisor, vpc_name, node_name)
    elif (node_type == "l1_transit"):
        node_name_hyp = hyp_utils.get_hyp_l1_transit_name(hypervisor, node_name)
    elif (node_type == "l2_transit"):
        node_name_hyp = hyp_utils.get_hyp_l2_transit_name(hypervisor, node_name)
    else:
        exit(1)

    node_name_hyp_arg = "c_name="+node_name_hyp

    if (path_choice_type == "spine"):
        path_choice_name_hyp = hyp_utils.get_hyp_spine_name(hypervisor, vpc_name, path_choice_name)
    elif (path_choice_type == "l1_transit"):
        path_choice_name_hyp = hyp_utils.get_hyp_l1_transit_name(hypervisor, path_choice_name)
    elif (path_choice_type == "l2_transit"):
        path_choice_name_hyp = hyp_utils.get_hyp_l2_transit_name(hypervisor, path_choice_name)
    else:
        exit(1)


    print("here1 ", path_choice_name_hyp)
    weight = weight_data["weight"]
    weight_arg = "bgp_weight=" + weight

    client_node_data = raas_utils.get_client_node_data(path_choice_type, path_choice_name, vpc_name)
    print(client_node_data)
    self_as = str(client_node_data["self_as"])
    self_as_arg = "self_as="+ self_as

    ve_ns1_ns2 = "c" + hyp_utils.get_client_id() + \
            "ve" + \
            path_choice_name_hyp.split('_')[-1] + \
            node_name_hyp.split('_')[-1]
            

    path_choice_ip_arg = "neighbor_ip="+ raas_utils.get_ns_ip(hypervisor, path_choice_name_hyp, ve_ns1_ns2)
    
    try:
        extra_vars = constants.ansible_become_pass + " " + \
                node_name_hyp_arg + " " + self_as_arg +\
                " " + hypervisor_arg + " " + weight_arg + \
                " " + path_choice_ip_arg

        print("ansible-playbook logic/bgp/bgp_set_weight.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
        rc = raas_utils.run_playbook("ansible-playbook logic/bgp/bgp_set_weight.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
        if (rc != 0):
            print ("bgp set weight failed")
            raise

        raas_utils.write_client_node_data(node_type, node_name, vpc_name, "path_choice", path_choice_name)
        raas_utils.write_client_node_data(node_type, node_name, vpc_name, "weight", str(weight))

    except:
        print("create pc failed python failed")
