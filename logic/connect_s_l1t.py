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
    param1 = config file (required)
"""

if __name__=="__main__":
    if (len(sys.argv) < 2):
        raas_utils.log_service("Please give peering config file")
        exit(1)

    peer_config_file = sys.argv[1]

    leaf_name = peer_config_file.split('/')[-1].split('.')[0]

    #Assumed customer always gives correct config file
    peering_data = do_json.json_read(peer_config_file)

    hypervisor = peering_data["hypervisor_name"]
    hypervisor_arg = "hypervisor="+hypervisor
    hypervisors_data = hyp_utils.get_hypervisors_data()
    hypervisor_ip = hyp_utils.get_hyp_ip(hypervisor)

    vpc_name = peering_data["vpc_name"]
    if not raas_utils.client_exists_vpc(vpc_name):
      raas_utils.log_service(vpc_name+ " VPC does not exist")
      exit(1)
    vpc_id=hyp_utils.get_hyp_vpc_name(hypervisor,vpc_name)
    
    
    spine_name = peering_data["spine_name"]
    if not raas_utils.client_exists_spine(vpc_name,spine_name):
      raas_utils.log_service(spine_name+ " spine does not exist")
      exit(1)
    spine_id=hyp_utils.get_hyp_spine_name(hypervisor,vpc_name,spine_name)

    transit_name = peering_data["l1_transit_name"]
    if not raas_utils.client_exists_l1_transit(transit_name):
      raas_utils.log_service(transit_name+" transit does not exist")
      exit(1)
    transit_id=hyp_utils.get_hyp_l1_transit_name(hypervisor,transit_name)

    try:
      
      
      network=raas_utils.get_new_veth_subnet('spine_l1t')
      subnet = network.split('/')
      s_ip = str(ipaddress.ip_address(subnet[0])+1) + '/' + subnet[1]
      t_ip = str(ipaddress.ip_address(subnet[0])+2) + '/' + subnet[1]
      s_ip_arg = " ns1_ip=" + s_ip 
      t_ip_arg = " ns2_ip=" + t_ip

      
      veth_1=" ve_ns1_ns2=" + vpc_id + "ve" + spine_id.split('_')[2] + transit_id.split('_')[1]
      veth_2=" ve_ns2_ns1=" + vpc_id + "ve" + transit_id.split('_')[1] + spine_id.split('_')[2]
      s_name_arg=" ns1="+spine_id
      t_name_arg=" ns2="+transit_id
      

      extra_vars = constants.ansible_become_pass + s_ip_arg + t_ip_arg + \
                  veth_1 + veth_2 + s_name_arg + t_name_arg + " " + hypervisor_arg
      

        
      rc = raas_utils.run_playbook("ansible-playbook logic/misc/connect_ns_ns.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")    
      if (rc != 0):
          raas_utils.log_service ("connect spine to l1t failed")
          raise


      
      new_subnet=str(ipaddress.ip_address(subnet[0])+8) + '/' + subnet[1]
      raas_utils.update_veth_subnet('spine_l1t',new_subnet)
      

    except Exception as e:
        raas_utils.log_service("[Err] Connecting spine to transit failed: "+str(e))
