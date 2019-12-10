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

    l1_transit_name = connection_data["l1_transit_name"]
    l1_transit_hypervisor_name = connection_data["l1_transit_hypervisor_name"]
    l1_transit_id = hyp_utils.get_hyp_l1_transit_name(l1_transit_hypervisor_name,l1_transit_name)
    l1_hypervisor_arg = " hypervisor=" + l1_transit_hypervisor_name

    l2_transit_name = connection_data["l2_transit_name"]
    l2_transit_hypervisor_name = connection_data["l2_transit_hypervisor_name"]
    l2_transit_id = hyp_utils.get_hyp_l2_transit_name(l2_transit_hypervisor_name,l2_transit_name)
    l2_hypervisor_arg = " hypervisor=" + l2_transit_hypervisor_name

    if (l1_transit_hypervisor_name == l2_transit_hypervisor_name):
        #connect l1 transit to l2 transit local
        try:

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
                        veth_1 + veth_2 + l1_transit_id_arg + l2_transit_id_arg + " " + l1_hypervisor_arg
            raas_utils.run_playbook("ansible-playbook logic/misc/connect_ns_ns.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")    


            new_subnet=str(ipaddress.ip_address(subnet[0])+8) + '/' + subnet[1]
            raas_utils.update_veth_subnet('l1t_l2t',new_subnet)

        except Exception as e:
            raas_utils.log_service("l1 transit to l2 transit local failed"+str(e))
    else:
        #connect l1 transit to l2 transit remote
        try:
            #c1_ve_h_l2t2
            gre_tunnel_name_arg=" gre_tunnel_name=gretun26"
            loopback_net=raas_utils.get_new_veth_subnet('loopbacks').split('/')
            grep_lo_net=".".join(loopback_net[0].split('.')[0:-1])

            veth_l1="c"+cid+"_ve_h_"+l1_transit_id.split('_')[1]
            l1_transit_ip=raas_utils.get_hv_ip(l1_transit_hypervisor_name,veth_l1).split('/')[0]
            l1_transit_lo_ip=raas_utils.get_ns_ip(l1_transit_hypervisor_name,l1_transit_id,grep_lo_net)+'/'+loopback_net[1]

            veth_l2="c"+cid+"_ve_h_"+l2_transit_id.split('_')[1]
            l2_transit_ip=raas_utils.get_hv_ip(l2_transit_hypervisor_name,veth_l2).split('/')[0]
            l2_transit_lo_ip=raas_utils.get_ns_ip(l2_transit_hypervisor_name,l2_transit_id,grep_lo_net)+'/'+loopback_net[1]

            try:
                # Configure GRE on Level 1 Transit
                l1_transit_id_arg=" t_name=" + l1_transit_id
                l1_t_local_ip_arg=" local_transit_ip=" + l1_transit_ip
                l2_t_remote_ip_arg=" remote_transit_ip=" + l2_transit_ip
                l2_transit_lo_ip_arg=" remote_subnet=" + l2_transit_lo_ip

                extra_vars = constants.ansible_become_pass + l1_hypervisor_arg + l1_transit_id_arg + l1_t_local_ip_arg + l2_t_remote_ip_arg + l2_transit_lo_ip_arg + gre_tunnel_name_arg

                raas_utils.run_playbook("ansible-playbook logic/transit/connect_transit_transit_remote.yml -i logic/inventory/hosts.yml -v --extra-vars '" + extra_vars + "'") 
            except Exception as e:
                raas_utils.log_service("Configure GRE on Level 1 Transit failed"+str(e))
                raise
            
            try:
                # Configure GRE on Level 2 Transit
                l2_transit_id_arg=" t_name=" + l2_transit_id
                l2_t_local_ip_arg=" local_transit_ip=" + l2_transit_ip
                l1_t_remote_ip_arg=" remote_transit_ip=" + l1_transit_ip
                l1_transit_lo_ip_arg=" remote_subnet=" + l1_transit_lo_ip

                extra_vars = constants.ansible_become_pass + l2_hypervisor_arg + l2_transit_id_arg + l2_t_local_ip_arg + l1_t_remote_ip_arg + l1_transit_lo_ip_arg + gre_tunnel_name_arg

                raas_utils.run_playbook("ansible-playbook logic/transit/connect_transit_transit_remote.yml -i logic/inventory/hosts.yml -v --extra-vars '" + extra_vars + "'") 
            except Exception as e:
                raas_utils.log_service("Configure GRE on Level 2 Transit failed"+str(e))
                raise
        except Exception as e:
            raas_utils.log_service("l1 transit to l2 transit remote failed"+str(e))

