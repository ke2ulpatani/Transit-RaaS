import os
import sys
import do_json
import raas_utils
import hyp_utils
import constants
import ipaddress

"""@params:
    param1 = vpc config file (required)
"""

if __name__=="__main__":
    if (len(sys.argv) < 2):
        print("Please give vpc config file")
        exit(1)

    peer_config_file = sys.argv[1]

    leaf_name = leaf_config_file.split('/')[-1].split('.')[0]

    #Assumed customer always gives correct config file
    peering_data = do_json.json_read(leaf_config_file)

    hypervisor = leaf_data["hypervisor_name"]
    hypervisor_arg = "hypervisor="+hypervisor
    hypervisors_data = hyp_utils.get_hypervisors_data()
    hypervisor_ip = hyp_utils.get_hyp_ip(hypervisor)

    vpc_name = leaf_data["vpc_name"]
    if not raas_utils.client_exists_vpc(vpc_name):
      print(vpc_name+ " VPC does not exist")
      exit(1)
    vpc_id=hyp_utils.get_hyp_vpc_name(hypervisor,vpc_name)
    
    
    spine_name = leaf_data["spine_name"]
    if not raas_utils.client_exists_spine(vpc_name,spine_name):
      print(spine_name+ " spine does not exist")
      exit(1)
    spine_id=hyp_utils.get_hyp_spine_name(hypervisor,vpc_name,spine_name)

    transit_name = leaf_data["l1_transit_name"]
    if not raas_utils.client_exists_l1_transit(transit_name):
      print(transit_name+" transit does not exist")
      exit(1)
    transit_id=hyp_utils.get_hyp_l1_transit_name(hypervisor,transit_name)

    try:
      network=raas_utils.get_new_veth_subnet('spine_l1t')
      subnet = network.split('/')
      
      b_ip = "b_ip="+str(ipaddress.ip_address(subnet[0])+1) + '/' + subnet[1]
      dhcp_range = "dhcp_range="+str(ipaddress.ip_address(subnet[0])+2)+','+ \
                        str(ipaddress.ip_address(subnet[0])+6)
      
      net_name=" s_t_net"+vpc_id + "_net_" + spine_id.split('_')[2]+"_" + transit_id.split('_')[1]
      net_arg=" t_s_net=" +net_name 
      br_arg=" s_t_br=" + vpc_id + "_br_" + spine_id.split('_')[2]+"_" + transit_id.split('_')[1]
      veth_1=" ve_l_s=" + vpc_id + "_ve_" + spine_id.split('_')[2]+"_" + transit_id.split('_')[1]
      veth_2=" ve_s_l=" + vpc_id + "_ve_" + transit_id.split('_')[1]+"_" + spine_id.split('_')[2]
      upper_vm_arg=" t_name="+transit_id
      lower_vm_arg=" s_name="+spine_id
      
      extra_vars = constants.ansible_become_pass + net_arg + br_arg + veth_1 + veth_2 + upper_vm_arg + lower_vm_arg + subnet_ip_arg + subnet_range_arg + " " + hypervisor_arg
                
      raas_utils.run_shell_script("ansible-playbook logic/subnet/connect_leaf_spine.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")
      new_subnet=str(ipaddress.ip_address(subnet[0])+8) + '/' + subnet[1]
      raas_utils.update_veth_subnet('spine_l1t',new_subnet)

    except Exception as e:
        raas_utils.run_shell_script("ansible-playbook logic/subnet/delete_leaf.yml -i logic/inventory/hosts.yml -v --extra-vars '"+extra_vars+"'")