import os
import sys
import do_json
import raas_utils
import hyp_utils
import constants
import ipaddress
#import logging
#from logging import info as raas_utils.log_service
#logging.basicConfig(filename='raas.log', filemode='a', format='%(asctime)s %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

"""@params:
    param1 = bgp config file (required)
"""

if __name__=="__main__":
    if (len(sys.argv) < 2):
        raas_utils.log_service("Please give bgp config file")
        exit(1)

    advertise_file = sys.argv[1]

    #pc_name = pc_config_file.split('/')[-1].split('.')[0]

    #Assumed customer always gives correct config file
    advertise_data = do_json.json_read(advertise_file)

    hypervisor = advertise_data["hypervisor_name"]
    hypervisor_arg = "hypervisor="+hypervisor

    hypervisors_data = hyp_utils.get_hypervisors_data()
    hypervisor_ip = hyp_utils.get_hyp_ip(hypervisor)
    
    vpc_name = advertise_data["vpc_name"]
    if not raas_utils.client_exists_vpc(vpc_name):
        raas_utils.log_service("VPC does not exist")
        exit(1)

    spine_name = advertise_data["spine_name"]
    l1_transit_name = advertise_data["l1_transit_name"]

    if not raas_utils.check_exists("spine", spine_name, vpc_name) or \
       not raas_utils.check_exists("l1_transit", l1_transit_name, vpc_name):
        raas_utils.log_service("Either Node does not exists")
        exit(1)


    spine_name_hyp = hyp_utils.get_hyp_spine_name(hypervisor, vpc_name, spine_name)
    l1_transit_name_hyp = hyp_utils.get_hyp_l1_transit_name(hypervisor, l1_transit_name)

    spine_name_hyp_arg = "c_name="+spine_name_hyp

    advertise = advertise_data["networks_advertised"]
    advertise_arg = "adv_subnets=" + advertise

    client_spine_data = raas_utils.get_client_node_data("spine", spine_name, vpc_name)

    self_as = str(client_spine_data["self_as"])
    self_as_arg = "self_as="+ self_as

    client_l1_transit_data = raas_utils.get_client_node_data("l1_transit", l1_transit_name, vpc_name)

    ras = str(client_l1_transit_data["self_as"])
    ras_arg = "ras="+ ras

    ve_spine_l1t = "c" + hyp_utils.get_client_id() + "_" + spine_name_hyp.split('_')[-2] + \
            "ve" + \
            l1_transit_name_hyp.split('_')[-1] + \
            spine_name_hyp.split('_')[-1]

    print(ve_spine_l1t)
    l1_transit_ip_arg = "rip="+ raas_utils.get_ns_ip(hypervisor, l1_transit_name_hyp, ve_spine_l1t)

    
    try:
        extra_vars = constants.ansible_become_pass + " " + \
                spine_name_hyp_arg + " " + self_as_arg +\
                " " + hypervisor_arg + " " + advertise_arg + \
                " " + l1_transit_ip_arg + " " + ras_arg

        rc = raas_utils.run_playbook("ansible-playbook logic/bgp/conf_spine_bgp.yml -i logic/inventory/hosts.yml -vvvv --extra-vars '"+extra_vars+"'")
        if (rc != 0):
            raas_utils.log_service ("bgp advertisement failed")
            raise

        raas_utils.write_client_spine_data(spine_type, spine_name, vpc_name, "adv_subnets", advertise)

    except:
        raas_utils.log_service("conf spine bgp failed python failed")
