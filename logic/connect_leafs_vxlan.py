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
    param1 = connection config name (required)
"""

if __name__=="__main__":
    if (len(sys.argv) < 2):
        raas_utils.log_service("Please give connection config file")
        exit(1)

    connection_config_file = sys.argv[1]
    connection_name = connection_config_file.split('/')[-1].split('.')[0]
    cid = hyp_utils.get_client_id()

    connection_data = do_json.json_read(connection_config_file)
    raas_utils.log_service(connection_data)

    
    cid = hyp_utils.get_client_id()

    leaf1_vpc_name = connection_data["leaf1_vpc_name"]
    leaf2_vpc_name = connection_data["leaf2_vpc_name"]

    leaf1_name = connection_data["leaf1_name"]
    leaf1_hypervisor_name = connection_data["leaf1_hypervisor_name"]
    leaf1_id = hyp_utils.get_hyp_leaf_name(leaf1_hypervisor_name, leaf1_vpc_name,leaf1_name)
    l1_hypervisor_arg = " hypervisor=" + leaf1_hypervisor_name

    leaf2_name = connection_data["leaf2_name"]
    leaf2_hypervisor_name = connection_data["leaf2_hypervisor_name"]
    leaf2_id = hyp_utils.get_hyp_leaf_name(leaf2_hypervisor_name, leaf2_vpc_name, leaf2_name)
    l2_hypervisor_arg = " hypervisor=" + leaf2_hypervisor_name

    #connect leaf1 to leaf2 vxlan remote
    try:
        #c1_ve_h_l2t2
        vxlan_tunnel_name_arg=" vxlan_tunnel_name=vxlantun26"
        
        loopback_net=raas_utils.get_new_veth_subnet('loopbacks').split('/')
        grep_lo_net=".".join(loopback_net[0].split('.')[0:-1])

        leaf1_lo_ip=raas_utils.get_ns_ip(leaf1_hypervisor_name,leaf1_id,grep_lo_net)

        leaf2_lo_ip=raas_utils.get_ns_ip(leaf2_hypervisor_name,leaf2_id,grep_lo_net)

        try:
            # Configure VXLAN on Leaf 1 Transit
            leaf1_id_arg=" l_name=" + leaf1_id
            l_local_ip_arg=" l_ip=" + leaf1_lo_ip
            l_remote_ip_arg=" remote_l_ip=" + leaf2_lo_ip
            br_name_arg=" l_br_name="+leaf1_id+"_br"

            extra_vars = constants.ansible_become_pass + l1_hypervisor_arg + leaf1_id_arg + l_local_ip_arg + l_remote_ip_arg + vxlan_tunnel_name_arg + br_name_arg

            raas_utils.run_playbook("ansible-playbook logic/subnet/add_vxlan_to_leaf.yml -i logic/inventory/hosts.yml -v --extra-vars '" + extra_vars + "'") 
        except Exception as e:
            raas_utils.log_service("Configure VXLAN on leaf 1 subnet failed"+str(e))
            raise
        
        try:
            # Configure VXLAN on Leaf 1 Transit
            leaf2_id_arg=" l_name=" + leaf2_id
            l_local_ip_arg=" l_ip=" + leaf2_lo_ip
            l_remote_ip_arg=" remote_l_ip=" + leaf1_lo_ip
            br_name_arg=" l_br_name="+leaf2_id+"_br"

            extra_vars = constants.ansible_become_pass + l2_hypervisor_arg + leaf2_id_arg + l_local_ip_arg + l_remote_ip_arg + vxlan_tunnel_name_arg + br_name_arg

            raas_utils.run_playbook("ansible-playbook logic/subnet/add_vxlan_to_leaf.yml -i logic/inventory/hosts.yml -v --extra-vars '" + extra_vars + "'") 
        except Exception as e:
            raas_utils.log_service("Configure VXLAN on leaf 2 subnet failed"+str(e))
            raise
        
        try:
            spines_data = raas_utils.get_all_spines(leaf1_vpc_name)
            leaf1_loopback_arg=" leaf_loopback=" + leaf1_lo_ip
            for spine in spines_data:
                spine_id = hyp_utils.get_hyp_spine_name(leaf1_hypervisor_name,leaf1_vpc_name,spine)
                if spine_id is None:
                    continue
                node_name_hyp_arg = "c_name="+spine_id
                spine_self_as = raas_utils.get_client_node_data("spine",spine_id,leaf1_vpc_name)["self_as"]
                spine_self_as_arg = " spine_self_as=" + str(spine_self_as)
                extra_vars = constants.ansible_become_pass + l1_hypervisor_arg + leaf1_loopback_arg + spine_self_as_arg + node_name_hyp_arg
                raas_utils.run_playbook("ansible-playbook logic/subnet/advertise_leaf_to_spine.yml -i logic/inventory/hosts.yml -v --extra-vars '" + extra_vars + "'") 
        except:
            raas_utils.log_service("Advertising routes of leaf 1 failed"+str(e))

        try:
            spines_data = raas_utils.get_all_spines(leaf2_vpc_name)
            leaf2_loopback_arg=" leaf_loopback=" + leaf2_lo_ip
            for spine in spines_data:
                spine_id = hyp_utils.get_hyp_spine_name(leaf2_hypervisor_name,leaf2_vpc_name,spine)
                if spine_id is None:
                    continue
                node_name_hyp_arg = "c_name="+spine_id
                spine_self_as = raas_utils.get_client_node_data("spine",spine_id,leaf2_vpc_name)["self_as"]
                spine_self_as_arg = " spine_self_as=" + str(spine_self_as)
                extra_vars = constants.ansible_become_pass + l2_hypervisor_arg + leaf2_loopback_arg + spine_self_as_arg + node_name_hyp_arg
                raas_utils.run_playbook("ansible-playbook logic/subnet/advertise_leaf_to_spine.yml -i logic/inventory/hosts.yml -v --extra-vars '" + extra_vars + "'") 
        except:
            raas_utils.log_service("Advertising routes of leaf 2 failed"+str(e))

    except Exception as e:
        raas_utils.log_service("Configure VXLAN failed"+str(e))

