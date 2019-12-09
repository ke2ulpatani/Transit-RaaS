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
    param1 = connection config name (required)
"""

if __name__=="__main__":
    if (len(sys.argv) < 2):
        print("Please give connection config file")
        exit(1)

    connection_config_file = sys.argv[1]
    connection_name = connection_config_file.split('/')[-1].split('.')[0]
    cid = hyp_utils.get_client_id()

    connection_data = do_json.json_read(connection_config_file)
    print(connection_data)

    # hypervisor = connection_data["hypervisor_name"]
    # hypervisor_arg = "hypervisor="+hypervisor
    # hypervisors_data = hyp_utils.get_hypervisors_data()
    # hypervisor_ip = hyp_utils.get_hyp_ip(hypervisor)
    
    cid = hyp_utils.get_client_id()

    l1_transit_name = connection_data["l1_transit_name"]
    l1_transit_hypervisor_name = connection_data["l1_transit_hypervisor_name"]
    l1_transit_id = hyp_utils.get_hyp_l1_transit_name(l1_transit_hypervisor_name,l1_transit_name)

    l2_transit_name = connection_data["l2_transit_name"]
    l2_transit_hypervisor_name = connection_data["l2_transit_hypervisor_name"]
    l2_transit_id = hyp_utils.get_hyp_l2_transit_name(l2_transit_hypervisor_name,l2_transit_name)

    if (l1_transit_hypervisor_name == l2_transit_hypervisor_name):
        #connect l1 transit to l2 transit local
        try:
            hypervisor_arg = "hypervisor="+l1_transit_hypervisor_name
            hypervisors_data = hyp_utils.get_hypervisors_data()
            hypervisor_ip = hyp_utils.get_hyp_ip(l1_transit_hypervisor_name)

            network=raas_utils.get_new_veth_subnet('l1t_l2t')
            subnet = network.split('/')

            l1t_ip = str(ipaddress.ip_address(subnet[0])+1) + '/' + subnet[1]
            l2t_ip = str(ipaddress.ip_address(subnet[0])+2) + '/' + subnet[1]
            l1t_ip_arg = " ns1_ip=" + l1t_ip
            l2t_ip_arg = " ns2_ip=" + l2t_ip 

            veth_1=" ve_ns1_ns2=c" + cid + "ve" + l1_transit_id.split('_')[1] + l2_transit_id.split('_')[1]
            veth_2=" ve_ns2_ns1=c" + cid + "ve" + l2_transit_id.split('_')[1] + l1_transit_id.split('_')[1]
            l2_transit_id_arg=" ns2="+l2_transit_id
            l1_transit_id_arg=" ns1="+l1_transit_id

            extra_vars = constants.ansible_become_pass + l1t_ip_arg + l2t_ip_arg + \
                        veth_1 + veth_2 + l1_transit_id_arg + l2_transit_id_arg + " " + hypervisor_arg
            raas_utils.run_playbook("ansible-playbook logic/misc/connect_ns_ns.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")    


            new_subnet=str(ipaddress.ip_address(subnet[0])+8) + '/' + subnet[1]
            raas_utils.update_veth_subnet('l1t_l2t',new_subnet)

        except Exception as e:
            print("l1 transit to l2 transit local failed",e)
            raise
    else:
        print("l1 and l2 transits exist in different hypervisor, GRE connect")
        exit(1)

