import os
import sys
import do_json
import raas_utils
import hyp_utils
import constants
import ipaddress
import logging
from logging import info as print
logging.basicConfig(filename='raas.log', filemode='a', format='%(asctime)s %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

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
    if (node_type == "spine"):
        vpc_name = multipath_data["vpc_name"]
        if not raas_utils.client_exists_vpc(vpc_name):
            print("VPC does not exist")
            exit(1)

    node_name = multipath_data["node_name"]

    node_name_hyp_arg = "c_name="+node_name_hyp

    if not raas_utils.check_exists(node_type, node_name, vpc_name):
        print("Node does not exists")
        exit(1)

    if (node_type == "spine"):
        node_name_hyp = hyp_utils.get_hyp_spine_name(hypervisor, vpc_name, node_name)
    elif (node_type == "t1_transit"):
        node_name_hyp = hyp_utils.get_hyp_l1_transit_name(hypervisor, node_name)
    elif (node_type == "t2_transit"):
        node_name_hyp = hyp_utils.get_hyp_l2_transit_name(hypervisor, node_name)
    else:
        exit(1)

    client_node_data = raas_utils.get_client_node_data(node_type, node_name, vpc_name)

    activate = multipath_data["activate"]
    self_as = str(client_node_data["self_as"])
    self_as_arg = "self_as="+ self_as

    if activate:
        activate_arg = "activate=" + "true"
    else:
        activate_arg = "activate=" + "false"
    
    try:
        #create_pc
        try:
            extra_vars = constants.ansible_become_pass + " " + \
                    node_name_hyp_arg + " " + self_as_arg +\
                    " " + hypervisor_arg + " " + activate_arg

            print("ansible-playbook logic/bgp/bgp_multipath.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            rc = raas_utils.run_playbook("ansible-playbook logic/bgp/bgp_multipath.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
            if (rc != 0):
                print ("bgp config failed playbook")
                raise
                
            raas_utils.write_client_node_data(node_type, node_name, vpc_name, "ecmp", True)
            raas_utils.write_client_node_data(node_type, node_name, vpc_name, "self_as", self_as)
        except:
            print ("bgp config failed")
            raise
    except:
        print("create pc failed python failed")
